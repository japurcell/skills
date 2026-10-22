import type { CaptureChunk, RepositoryStore } from './store.js';
import { RedactionPolicy } from './redaction.js';

const CHUNK = 65536, BATCH = 262144, MEMORY = 4194304;
type OpenCapture = { channel: string; attemptId?: string };
type EndState = 'complete' | 'partial' | 'unknown';

/** One recorder per invocation. Await writes, or use consume to propagate readable backpressure. */
export class InvocationRecorder {
  private readonly policy: RedactionPolicy;
  private readonly writers = new Set<CaptureWriter>();
  private serial: Promise<unknown> = Promise.resolve();
  private queue: { writer: CaptureWriter; chunk: CaptureChunk }[] = [];
  private queueBytes = 0;
  private timer: ReturnType<typeof setTimeout> | undefined;
  private failure: Error | undefined;
  private peak = 0;
  constructor(private readonly options: { store: RepositoryStore; invocationId: string; secrets?: readonly string[];
    requestShutdown: (reason: string) => void; fallback?: (safeText: string) => void }) {
    this.policy = new RedactionPolicy(options.secrets);
  }
  get failed() { return this.failure !== undefined; }
  /** Conservatively includes UTF-16 staging, decoder/filter tails and one bounded processing slice. */
  get bufferedBytes() { return this.queue.reduce((sum, item) => sum + item.chunk.text.length * 2, 0)
    + [...this.writers].reduce((sum, writer) => sum + writer.retainedBytes, 0) + 262144; }
  get peakBufferedBytes() { return this.peak; }
  private measure() {
    this.peak = Math.max(this.peak, this.bufferedBytes);
    if (this.peak > MEMORY) throw new Error('recorder memory limit');
  }
  async openCapture(input: OpenCapture) {
    return this.run(async () => {
      if (this.writers.size >= 32) throw new Error('recorder open capture limit');
      const saved = await this.options.store.createCapture({ ...input, invocationId: this.options.invocationId });
      const writer = new CaptureWriter(this, saved.id, this.policy.stream());
      this.writers.add(writer); this.measure();
      return writer;
    });
  }
  /** Internal serialization keeps input decoding and batch memory shared, never one queue per stream. */
  run<T>(action: () => Promise<T>): Promise<T> {
    const operation = this.serial.then(async () => {
      if (this.failure) throw this.failure;
      try { return await action(); }
      catch { await this.fail(); throw this.failure; }
    });
    this.serial = operation.catch(() => {});
    return operation;
  }
  private async fail() {
    if (this.failure) return;
    this.failure = new Error('capture recording failed; admission stopped and shutdown required');
    if (this.timer) clearTimeout(this.timer);
    // Fail closed locally even when disk-full prevents saving the shutdown transition.
    this.options.store.blockAdmissions(this.options.invocationId);
    try { this.options.requestShutdown(this.failure.message); } catch { /* Fallback must still run. */ }
    try { (this.options.fallback ?? (text => { process.stderr.write(text); }))(this.failure.message + '\n'); } catch { /* No recursive recording. */ }
    try { await this.flush(); } catch { /* Uncommitted bytes remain explicitly incomplete. */ }
    for (const writer of this.writers) {
      try { await this.options.store.appendCapture({ id: writer.id, chunks: [], state: 'partial' }); } catch { /* Disk failure may prevent even the partial marker. */ }
    }
    try { await this.options.store.stopAdmissions(this.options.invocationId); } catch { /* Preserve all committed evidence. */ }
  }
  async enqueue(writer: CaptureWriter, text: string) {
    if (!text) return;
    // Bound by encoded bytes, and never split a Unicode scalar across saved chunks.
    for (let offset = 0; offset < text.length;) {
      let end = Math.min(text.length, offset + 16384);
      if (end < text.length && /[\uD800-\uDBFF]/.test(text[end - 1]!)) end--;
      const part = text.slice(offset, end), bytes = Buffer.byteLength(part);
      if (this.queueBytes + bytes > BATCH || this.queue.length >= 200) await this.flush();
      this.queue.push({ writer, chunk: { sequence: writer.nextSequence(), text: part } }); this.queueBytes += bytes;
      offset = end; this.measure();
      if (!this.timer) this.timer = setTimeout(() => {
        this.timer = undefined;
        void this.run(() => this.flush()).catch(() => {});
      }, 100);
      if (this.queueBytes >= BATCH) await this.flush();
    }
  }
  private async flush() {
    if (this.timer) { clearTimeout(this.timer); this.timer = undefined; }
    while (this.queue.length) {
      const writer = this.queue[0]!.writer;
      const selected = this.queue.filter(item => item.writer === writer);
      await this.options.store.appendCapture({ id: writer.id, chunks: selected.map(item => item.chunk) });
      const selectedSet = new Set(selected);
      this.queue = this.queue.filter(item => !selectedSet.has(item));
      this.queueBytes -= selected.reduce((sum, item) => sum + Buffer.byteLength(item.chunk.text), 0);
    }
  }
  /** Flushes saved text before a caller records terminal results, questions or ownership transitions. */
  async barrier() { return this.run(() => this.flush()); }
  async end(writer: CaptureWriter, state: EndState) {
    await this.flush();
    await this.options.store.appendCapture({ id: writer.id, chunks: [], state });
    this.writers.delete(writer);
  }
  readCapture(id: string, after: number) { return this.options.store.readCapture({ id, after }); }
}

export class CaptureWriter {
  private readonly decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
  private sequence = 0;
  private ended = false;
  private originalBytes = 0;
  constructor(private readonly recorder: InvocationRecorder, readonly id: string,
    private readonly redactor: ReturnType<RedactionPolicy['stream']>) {}
  get retainedBytes() { return this.redactor.retainedBytes + 4; }
  nextSequence() { return ++this.sequence; }
  async write(input: Uint8Array | string) {
    return this.recorder.run(async () => {
      if (this.ended) throw new Error('capture closed');
      if (typeof input === 'string') {
        for (let offset = 0; offset < input.length;) {
          let end = Math.min(input.length, offset + 4096);
          if (end < input.length && /[\uD800-\uDBFF]/.test(input[end - 1]!)) end++;
          const part = input.slice(offset, end);
          if (Buffer.from(part).toString('utf8') !== part) throw new Error('unsupported text encoding');
          this.originalBytes = Math.min(1048577, this.originalBytes + Buffer.byteLength(part));
          await this.recorder.enqueue(this, this.redactor.push(this.decoder.decode(Buffer.from(part), { stream: true })));
          offset = end;
        }
      } else {
        if (!(input instanceof Uint8Array)) throw new Error('unsupported capture input');
        for (let offset = 0; offset < input.byteLength; offset += 4096) {
          const part = input.subarray(offset, offset + 4096);
          this.originalBytes = Math.min(1048577, this.originalBytes + part.byteLength);
          await this.recorder.enqueue(this, this.redactor.push(this.decoder.decode(part, { stream: true })));
        }
      }
    });
  }
  async consume(source: AsyncIterable<Uint8Array | string>) {
    try { for await (const chunk of source) await this.write(chunk); await this.finish(); }
    catch (error) { if (!this.recorder.failed) await this.finish('partial'); throw error; }
  }
  async finish(state: EndState = 'complete') {
    return this.recorder.run(async () => {
      if (this.ended) return;
      if (!['complete','partial','unknown'].includes(state)) throw new Error('invalid capture terminal state');
      await this.recorder.enqueue(this, this.redactor.push(this.decoder.decode(), true));
      await this.recorder.end(this, state); this.ended = true;
    });
  }
  /** Parses only an ended complete result. Oversize remains fully saved as raw filtered text. */
  async readResult(limit = 1048576): Promise<unknown> {
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 1048576) throw new Error('invalid structured result limit');
    if (!this.ended) throw new Error('result capture is still open');
    if (this.originalBytes > limit) throw new Error('structured result exceeds size limit; raw capture preserved');
    let after = 0, bytes = 0;
    const parts: string[] = [];
    do {
      const page = this.recorder.readCapture(this.id, after);
      if (page.state !== 'complete') throw new Error('result capture is not complete');
      for (const chunk of page.chunks) {
        bytes += Buffer.byteLength(chunk.text);
        if (bytes > limit) throw new Error('structured result exceeds size limit; raw capture preserved');
        parts.push(chunk.text);
      }
      after = page.nextSequence;
      if (!page.hasMore) break;
    } while (true);
    try { return JSON.parse(parts.join('')); } catch { throw new Error('invalid structured result JSON; raw capture preserved'); }
  }
}
