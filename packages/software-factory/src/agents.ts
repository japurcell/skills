import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { StringDecoder } from 'node:string_decoder';
import { setTimeout as delay, setImmediate as nextTurn } from 'node:timers/promises';
import { currentOwner, duration, LiveProcessScope } from './native/process.js';
import { resolveStepInputs } from './profiles.js';
import type { ProfileFields, EffectiveInputs } from './profiles.js';
import type { AgentAdapter, AgentResult, PayloadValidator } from './adapters/types.js';
import type { Admission } from './accounting.js';
import type { CommandRunner } from './workflow.js';
import { NeedsInput, ShutdownInterrupted } from './execution-control.js';
export interface AgentOptions<T = unknown> extends ProfileFields {
  profile?: string;
  purpose?: 'implementation' | 'review' | 'report';
  context?: string;
  output?: PayloadValidator<T>;
  reuse?: boolean;
  timeoutMs?: number;
  intent?: Admission['intent'];
  priorAttemptId?: string;
  loopKey?: string;
}
export interface AgentConfiguration {
  adapters?: Record<string, AgentAdapter>;
  agentOverrides?: Record<string, ProfileFields>;
}
export class AgentCalls {
  private readonly sessions = new Map<string, { nativeId?: string; inputs: EffectiveInputs; adapter: AgentAdapter }>();
  private readonly invalid = new Map<string, string>();
  private readonly outputContracts = new Map<string, PayloadValidator>();
  private readonly correctionParents = new Map<string, string>();
  constructor(
    private readonly runner: CommandRunner,
    private readonly config: AgentConfiguration,
  ) {}
  assertValid() {
    if (this.invalid.size) throw new Error(`unresolved invalid agent result: ${[...this.invalid.keys()].join(', ')}`);
  }
  async execute<T>(key: string, options: AgentOptions<T>): Promise<AgentResult<T>> {
    const host = this.runner;
    if (host.dispatchStopped) throw new ShutdownInterrupted('shutdown stopped agent dispatch');
    if (!this.config.adapters || Object.keys(this.config.adapters).length === 0)
      throw new Error('agent adapters unavailable; no agent attempt launched');
    const {
      profile,
      purpose = 'implementation',
      context = '',
      output,
      reuse = false,
      timeoutMs,
      intent = 'initial',
      priorAttemptId,
      loopKey,
      ...fields
    } = options;
    if (
      !['implementation', 'review', 'report'].includes(purpose) ||
      typeof context !== 'string' ||
      typeof reuse !== 'boolean'
    )
      throw new Error('invalid agent request');
    if (output && (typeof output.name !== 'string' || !output.name.trim() || typeof output.validate !== 'function'))
      throw new Error('structured output requires a named explicit validator');
    let effectiveOutput: PayloadValidator | undefined = output ? { name: output.name, validate: output.validate } : undefined;
    const inputs = resolveStepInputs(host.worktree, profile, fields, this.config.agentOverrides?.[key]);
    const inputCapture = await host.recorder.openCapture({ channel: 'context' });
    await inputCapture.write(JSON.stringify({ step: key, inputs, purpose, context, validator: effectiveOutput?.name ?? null }));
    await inputCapture.finish();
    const adapter = this.config.adapters?.[inputs.harness];
    if (!adapter || adapter.id !== inputs.harness)
      throw new Error(`agent adapter unavailable: ${inputs.harness}; no agent attempt launched`);
    for (const capability of [
      'live-output',
      'lifecycle',
      'final-output',
      'stop',
      ...inputs.requiredCapabilities,
      ...(inputs.model ? ['model'] : []),
      ...(inputs.reasoning ? ['reasoning'] : []),
      inputs.permissions,
      ...(inputs.skills.length ? [inputs.skillDelivery === 'native' ? 'native-skills' : 'instructions'] : []),
    ])
      if (!adapter.capabilities.includes(capability)) throw new Error(`required capability unsupported: ${capability}`);
    adapter.validateProfile(inputs);
    const correction = intent === 'code_correction' || intent === 'format_correction';
    if (correction && !context.trim()) throw new Error('correction requires explicit saved context and findings');
    if (intent === 'format_correction' && inputs.permissions !== 'read-only')
      throw new Error('format correction requires read-only permissions');
    if (priorAttemptId) {
      const prior = host.store.readAttempt(priorAttemptId);
      if (
        correction &&
        (prior.kind !== 'agent' ||
          prior.outcome === null ||
          !['succeeded', 'failed'].includes(prior.outcome) ||
          !prior.agent)
      )
        throw new Error('correction requires a completed agent result');
      if (correction && prior.agent?.validator) {
        if (effectiveOutput?.name !== prior.agent.validator)
          throw new Error(`correction must preserve output validator: ${prior.agent.validator}`);
        // A same-name replacement function cannot weaken the original contract.
        effectiveOutput = this.outputContracts.get(priorAttemptId) ?? effectiveOutput;
      }
      if (intent === 'format_correction' && !this.invalid.has(priorAttemptId))
        throw new Error('format correction requires invalid output in this invocation');
    }
    if (reuse && !correction) throw new Error('only same-invocation corrections may request reuse');
    const prior = priorAttemptId ? this.sessions.get(priorAttemptId) : undefined;
    const compatible = !!(
      reuse &&
      correction &&
      purpose !== 'review' &&
      prior?.nativeId &&
      prior.adapter === adapter &&
      JSON.stringify(prior.inputs) === JSON.stringify(inputs) &&
      adapter.canReuse(prior.inputs, inputs)
    );
    const timeout = duration(timeoutMs, host.agentTimeoutMs);
    const admission = {
      id: randomUUID(),
      invocationId: host.invocationId,
      operationKey: key,
      kind: 'agent' as const,
      intent,
      ...(priorAttemptId ? { priorAttemptId } : {}),
      ...(loopKey ? { loopKey } : {}),
    };
    let attempt;
    while (!attempt) {
      if (host.dispatchStopped) throw new ShutdownInterrupted('shutdown cancelled agent capacity wait');
      try {
        attempt = await host.store.admitAttempt(admission);
      } catch (error) {
        if (error instanceof Error && /agent capacity exhausted/.test(error.message)) {
          await Promise.race([delay(100), host.stopped]);
          continue;
        }
        throw error;
      }
    }
    // Reassociate the immutable supplied-input capture with this exact admitted attempt.
    const supplied = await host.recorder.openCapture({ channel: 'context', attemptId: attempt.id });
    await supplied.write(JSON.stringify({ inputs, purpose, context, sourceCaptureId: inputCapture.id }));
    await supplied.finish();
    const stdout = await host.recorder.openCapture({
      channel: adapter.finalChannel === 'stdout' ? 'result' : 'stdout',
      attemptId: attempt.id,
    });
    const stderr = await host.recorder.openCapture({
      channel: adapter.finalChannel === 'stderr' ? 'result' : 'stderr',
      attemptId: attempt.id,
    });
    await host.store.saveAgentMetadata(attempt.id, {
      inputsCaptureId: supplied.id,
      resultCaptureId: adapter.finalChannel === 'stdout' ? stdout.id : stderr.id,
      outputCaptureId: adapter.eventChannel === 'stdout' ? stdout.id : stderr.id,
      adapter: adapter.id,
      sessionMode: compatible ? 'reuse' : 'fresh',
      context: compatible ? 'same-invocation correction' : 'explicit supplied context',
      ...(compatible ? { reusedAttemptId: priorAttemptId! } : {}),
      validator: effectiveOutput?.name ?? null,
    });
    this.sessions.set(attempt.id, { inputs, adapter });
    if (effectiveOutput) this.outputContracts.set(attempt.id, effectiveOutput);
    if (correction && priorAttemptId) this.correctionParents.set(attempt.id, priorAttemptId);
    let launch;
    try {
      launch = adapter.start({
        attemptId: attempt.id,
        invocationId: host.invocationId,
        worktree: host.worktree,
        inputs,
        context,
        ...(compatible ? { reuseNativeId: prior!.nativeId! } : {}),
      });
      if (
        !launch.argv.length ||
        launch.argv.some((v) => typeof v !== 'string' || v.includes('\0')) ||
        !launch.argv[0] ||
        !['process-group', 'unknown'].includes(launch.childScope) ||
        !launch.env ||
        Object.entries(launch.env).some(
          ([k, v]) => !k || k.includes('=') || k.includes('\0') || typeof v !== 'string' || v.includes('\0'),
        )
      )
        throw new Error('invalid adapter launch');
    } catch (error) {
      await stdout.finish();
      await stderr.finish();
      await host.store.settleAttempt({
        id: attempt.id,
        launch: 'not_started',
        outcome: 'failed',
        quiescent: true,
        evidence: 'adapter launch construction rejected',
      });
      throw error;
    }
    if (host.dispatchStopped) {
      await stdout.finish();
      await stderr.finish();
      await host.store.settleAttempt({
        id: attempt.id,
        launch: 'not_started',
        outcome: 'interrupted',
        quiescent: true,
        evidence: 'shutdown before agent spawn',
      });
      throw new ShutdownInterrupted('shutdown stopped agent launch');
    }
    let child;
    try {
      child = spawn(launch.argv[0]!, launch.argv.slice(1), {
        cwd: host.worktree,
        env: launch.env,
        shell: false,
        detached: process.platform !== 'win32',
        stdio: ['ignore', 'pipe', 'pipe'],
      });
    } catch (error) {
      await stdout.finish();
      await stderr.finish();
      await host.store.settleAttempt({
        id: attempt.id,
        launch: 'not_started',
        outcome: 'failed',
        quiescent: true,
        evidence: 'agent spawn rejected',
      });
      throw error;
    }
    const scope = new LiveProcessScope(child, launch.childScope === 'unknown');
    let receivedQuestion = false;
    host.registerAgent(attempt.id, scope, () => {
      // A completed authoritative question need not signal its already-exited owner.
      // Descendant absence still comes from the unchanged native scope checks.
      if (receivedQuestion)
        return Promise.race([scope.exited, delay(Math.min(10, host.grace))]).then(() => {
          if (child.exitCode !== null || child.signalCode !== null) return;
          return adapter.requestStop(() => scope.stop(host.grace));
        });
      return adapter.requestStop(() => scope.stop(host.grace));
    });
    const launched = child.pid !== undefined;
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      host.requestShutdown('timeout', `agent timeout: ${key}`);
    }, timeout);
    const machine = async (source: AsyncIterable<Buffer>, writer: typeof stdout) => {
      const decoder = new StringDecoder('utf8');
      let pending = '';
      try {
        for await (const chunk of source) {
          await writer.write(chunk);
          await host.recorder.barrier();
          pending += decoder.write(chunk as Buffer);
          while (pending.includes('\n')) {
            const i = pending.indexOf('\n'),
              line = pending.slice(0, i);
            pending = pending.slice(i + 1);
            if (Buffer.byteLength(line) > 1048576) throw new Error('adapter machine event exceeds size limit');
            if (line) await event(line);
          }
          if (Buffer.byteLength(pending) > 1048576) throw new Error('adapter machine event exceeds size limit');
        }
        pending += decoder.end();
        if (Buffer.byteLength(pending) > 1048576) throw new Error('adapter machine event exceeds size limit');
        if (pending) await event(pending);
        await writer.finish();
      } catch (error) {
        if (!host.recorder.failed) await writer.finish('partial');
        throw error;
      }
      async function event(line: string) {
        const value = adapter!.mapEvent(line);
        if (value) {
          const saved = await host.store.saveSession(attempt!.id, value);
          if (saved.parentNativeId === null) {
            const info = thisInfo();
            info.nativeId = saved.nativeId;
          }
        }
      }
    };
    const thisInfo = () => this.sessions.get(attempt.id)!;
    const stopOnStreamFailure = (promise: Promise<void>) =>
      promise.catch((error) => {
        host.requestShutdown(host.recorder.failed ? 'recording' : 'failure', 'agent stream failed');
        throw error;
      });
    const finalCapture = adapter.finalChannel === 'stdout' ? stdout : stderr;
    let envelope: Record<string, unknown> | undefined;
    let invalid: string | undefined;
    const receiveFinal = async () => {
      try {
        envelope = adapter.decodeFinal(await finalCapture.readText()) as Record<string, unknown> | undefined;
      } catch (error) {
        invalid = error instanceof Error ? error.message : 'invalid result';
      }
      if (
        !invalid &&
        envelope &&
        typeof envelope === 'object' &&
        !Array.isArray(envelope) &&
        envelope['kind'] === 'needs_input' &&
        typeof envelope['question'] === 'string' &&
        envelope['question'].trim() &&
        typeof envelope['context'] === 'string' &&
        envelope['context'].trim() &&
        (envelope['suggestions'] === undefined ||
          (Array.isArray(envelope['suggestions']) && envelope['suggestions'].every((s) => typeof s === 'string')))
      ) {
        await host.block();
        const question = await host.recorder.openCapture({ channel: 'request', attemptId: attempt.id });
        await question.write(
          JSON.stringify({
            question: envelope['question'],
            context: envelope['context'],
            suggestions: envelope['suggestions'],
            sourceAttemptId: attempt.id,
          }),
        );
        await question.finish();
        receivedQuestion = true;
        // The authoritative channel is closed and saved. Stop peers before waiting for process cleanup.
        host.requestShutdown('needs_input', 'agent needs input');
      }
    };
    const stdoutStream =
      adapter.eventChannel === 'stdout' ? machine(child.stdout!, stdout) : stdout.consume(child.stdout!);
    const stderrStream =
      adapter.eventChannel === 'stderr' ? machine(child.stderr!, stderr) : stderr.consume(child.stderr!);
    const outputStreams = Promise.allSettled([
      stopOnStreamFailure(adapter.finalChannel === 'stdout' ? stdoutStream.then(receiveFinal) : stdoutStream),
      stopOnStreamFailure(adapter.finalChannel === 'stderr' ? stderrStream.then(receiveFinal) : stderrStream),
    ]).then((results) => {
      const bad = results.find((r) => r.status === 'rejected');
      if (bad?.status === 'rejected') throw bad.reason;
    });
    void outputStreams.catch(() => {});
    try {
      if (launched) await host.store.markStarted({ id: attempt.id, owner: currentOwner(child.pid!) });
      // Let native exit/pipe-close observations arrive after authoritative-channel recording.
      // The same scope still requires actual group absence and preserves inherited-pipe uncertainty.
      await Promise.race([outputStreams, scope.exited]);
      await nextTurn();
      const processResult = await scope.result(host.grace);
      await outputStreams;
      await host.recorder.barrier();
      const interrupted = scope.interrupted && (processResult.signal !== null || processResult.code !== 0);
      if (
        receivedQuestion &&
        !processResult.error &&
        !timedOut &&
        (processResult.code === 0 || adapter.questionExitCodes.includes(processResult.code ?? -1) || interrupted)
      ) {
        await host.store.settleAttempt({
          id: attempt.id,
          launch: 'started',
          outcome: 'needs_input',
          quiescent: processResult.quiescent,
          evidence: `validated authoritative question; exit=${processResult.code}; signal=${processResult.signal}; uncertain=${scope.uncertain}; interrupted=${scope.interrupted}; groupAbsent=${scope.groupAbsent()}`,
        });
        throw new NeedsInput('agent needs input');
      }
      if (processResult.error || timedOut || interrupted || processResult.code !== 0 || !processResult.quiescent) {
        await host.store.settleAttempt({
          id: attempt.id,
          launch: launched ? 'started' : 'not_started',
          outcome: interrupted && !timedOut ? 'interrupted' : 'failed',
          quiescent: processResult.quiescent || !launched,
          evidence: `exit=${processResult.code}; signal=${processResult.signal}; ${timedOut ? 'timeout' : processResult.quiescent ? 'owned group absent' : 'cleanup unknown'}`,
        });
        if (processResult.error) throw processResult.error;
        if (timedOut) throw new Error(`agent timeout: ${key}`);
        if (interrupted) throw new ShutdownInterrupted(`agent interrupted: ${key}`);
        throw new Error(`agent failed or cleanup unknown: ${key}`);
      }
      if (processResult.code !== 0) throw new Error(`agent nonzero exit did not return a valid question: ${key}`);
      if (
        !invalid &&
        (!envelope ||
          typeof envelope !== 'object' ||
          Array.isArray(envelope) ||
          envelope['kind'] !== 'result' ||
          !Object.hasOwn(envelope, 'payload'))
      )
        invalid = 'missing or malformed authoritative result envelope';
      if (
        !invalid &&
        envelope!['artifacts'] !== undefined &&
        (!Array.isArray(envelope!['artifacts']) ||
          (envelope!['artifacts'] as unknown[]).some((v) => typeof v !== 'string' || !v))
      )
        invalid = 'invalid artifact references';
      if (!invalid && effectiveOutput) {
        try {
          if (!effectiveOutput.validate(envelope!['payload'])) invalid = `payload rejected by validator: ${effectiveOutput.name}`;
        } catch {
          invalid = `payload validator failed: ${effectiveOutput.name}`;
        }
      }
      await host.store.settleAttempt({
        id: attempt.id,
        launch: 'started',
        outcome: invalid ? 'failed' : 'succeeded',
        quiescent: true,
        evidence: invalid ? 'invalid authoritative result; raw capture retained' : 'validated authoritative result',
      });
      if (invalid) {
        this.invalid.set(attempt.id, invalid);
        return { attemptId: attempt.id, status: 'invalid', diagnostic: invalid, resultCaptureId: finalCapture.id };
      }
      if (correction && priorAttemptId) {
        let ancestor: string | undefined = priorAttemptId;
        while (ancestor) {
          this.invalid.delete(ancestor);
          ancestor = this.correctionParents.get(ancestor);
        }
      }
      return {
        attemptId: attempt.id,
        status: 'succeeded',
        value: envelope!['payload'] as T,
        artifacts: (envelope!['artifacts'] as string[]) ?? { state: 'unknown' },
        resultCaptureId: finalCapture.id,
      };
    } catch (error) {
      if (!(error instanceof NeedsInput) && !(error instanceof ShutdownInterrupted))
        host.requestShutdown(
          host.recorder.failed ? 'recording' : 'failure',
          error instanceof Error ? error.message : 'agent failed',
        );
      await scope.stop(host.grace);
      await outputStreams.catch(() => {});
      if (!host.recorder.failed) {
        const pending = host.store.readAttempt(attempt.id);
        if (pending.launch === 'started' && pending.outcome === null) {
          const cleanup = await scope.result(host.grace);
          await host.store.settleAttempt({
            id: attempt.id,
            launch: 'started',
            outcome: 'failed',
            quiescent: cleanup.quiescent,
            evidence: `agent processing failed; exit=${cleanup.code}; signal=${cleanup.signal}; ${cleanup.quiescent ? 'owned group absent' : 'cleanup unknown'}`,
          });
        }
      }
      throw error;
    } finally {
      clearTimeout(timer);
      host.unregisterAgent(attempt.id);
    }
  }
}
