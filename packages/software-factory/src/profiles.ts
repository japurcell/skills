import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
export type PromptInput = string | { file: string };
export interface SkillInput {
  name: string;
  file: string;
  resources?: string[];
}
export interface ProfileFields {
  harness?: string;
  model?: string;
  reasoning?: string;
  permissions?: 'read-only' | 'workspace-write';
  prompt?: PromptInput;
  skills?: SkillInput[];
  skillDelivery?: 'native' | 'instructions';
  requiredCapabilities?: string[];
}
export interface EffectiveInputs {
  layers: { source: string; fields: ProfileFields }[];
  profile: string | null;
  harness: string;
  model?: string;
  reasoning?: string;
  permissions: 'read-only' | 'workspace-write';
  prompt: string;
  skills: { name: string; file: string; instructions: string; resources: { file: string; content: string }[] }[];
  skillDelivery: 'native' | 'instructions';
  requiredCapabilities: string[];
  provenance: Record<string, string>;
}
const fields = [
  'harness',
  'model',
  'reasoning',
  'permissions',
  'prompt',
  'skills',
  'skillDelivery',
  'requiredCapabilities',
] as const;
function object(value: unknown): asserts value is Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('profile fields must be an object');
}
function named(value: unknown): asserts value is string {
  if (typeof value !== 'string' || !value.trim() || value.includes('\0'))
    throw new Error('profile requires nonempty text');
}
function validate(value: unknown): asserts value is ProfileFields {
  object(value);
  if (Object.keys(value).some((k) => !(fields as readonly string[]).includes(k)))
    throw new Error('unknown profile field; fallback chains are unsupported');
  for (const k of ['harness', 'model', 'reasoning'] as const) if (k in value) named(value[k]);
  if ('permissions' in value && !['read-only', 'workspace-write'].includes(String(value['permissions'])))
    throw new Error('unsupported permissions');
  if ('skillDelivery' in value && !['native', 'instructions'].includes(String(value['skillDelivery'])))
    throw new Error('invalid skill delivery');
  if ('prompt' in value && typeof value['prompt'] !== 'string') {
    object(value['prompt']);
    if (Object.keys(value['prompt']).join() !== 'file') throw new Error('invalid prompt reference');
    named(value['prompt']['file']);
  }
  for (const k of ['skills', 'requiredCapabilities'] as const)
    if (k in value && !Array.isArray(value[k])) throw new Error(`invalid ${k}`);
  for (const capability of (value['requiredCapabilities'] as unknown[]) ?? []) named(capability);
  for (const skill of (value['skills'] as unknown[]) ?? []) {
    object(skill);
    if (Object.keys(skill).some((k) => !['name', 'file', 'resources'].includes(k)))
      throw new Error('invalid skill field');
    named(skill['name']);
    named(skill['file']);
    if (
      'resources' in skill &&
      (!Array.isArray(skill['resources']) || skill['resources'].some((r) => typeof r !== 'string' || !r))
    )
      throw new Error('invalid skill resources');
  }
}
/** Each layer replaces only supplied fields. Composition is ordinary explicit workflow code. */
export function resolveStepInputs(
  worktree: string,
  profile: string | undefined,
  step: ProfileFields,
  override?: ProfileFields,
): EffectiveInputs {
  const path = resolve(worktree, '.factory/agents.json');
  const config: unknown = existsSync(path) ? JSON.parse(readFileSync(path, 'utf8')) : {};
  object(config);
  if (Object.keys(config).some((k) => !['defaults', 'profiles'].includes(k)))
    throw new Error('unknown agent configuration field');
  const values: Record<string, unknown> = {};
  const provenance: Record<string, string> = {};
  const layers: { source: string; fields: ProfileFields }[] = [];
  const apply = (source: string, layer: unknown) => {
    validate(layer);
    layers.push({ source, fields: structuredClone(layer) });
    for (const key of fields)
      if (Object.hasOwn(layer, key)) {
        values[key] = layer[key];
        provenance[key] = source;
      }
  };
  if (config['defaults'] !== undefined) apply('repository defaults', config['defaults']);
  if (profile !== undefined) {
    named(profile);
    object(config['profiles']);
    if (!Object.hasOwn(config['profiles'], profile)) throw new Error(`unknown profile: ${profile}`);
    apply(`profile:${profile}`, config['profiles'][profile]);
  }
  apply('step', step);
  if (override !== undefined) apply('invocation override', override);
  named(values['harness']);
  if (!['read-only', 'workspace-write'].includes(String(values['permissions'])))
    throw new Error('explicit permissions required');
  if (!['native', 'instructions'].includes(String(values['skillDelivery'])))
    throw new Error('explicit skill delivery required');
  const read = (file: string) => readFileSync(resolve(worktree, file), 'utf8');
  const prompt = values['prompt'] as PromptInput | undefined;
  if (prompt === undefined) throw new Error('prompt required');
  const skills = ((values['skills'] as SkillInput[]) ?? []).map((s) => ({
    name: s.name,
    file: s.file,
    instructions: read(s.file),
    resources: (s.resources ?? []).map((file) => ({ file, content: read(file) })),
  }));
  return structuredClone({
    layers,
    profile: profile ?? null,
    harness: values['harness'],
    ...(values['model'] !== undefined ? { model: String(values['model']) } : {}),
    ...(values['reasoning'] !== undefined ? { reasoning: String(values['reasoning']) } : {}),
    permissions: values['permissions'] as EffectiveInputs['permissions'],
    skillDelivery: values['skillDelivery'] as EffectiveInputs['skillDelivery'],
    prompt: typeof prompt === 'string' ? prompt : read(prompt.file),
    skills,
    requiredCapabilities: (values['requiredCapabilities'] as string[]) ?? [],
    provenance,
  });
}
