// Public diagnostic wire boundary. Raw native/build output never passes through.
import { cases } from './windows-owned-image.mjs';

export const buildCategories = Object.freeze(['host', 'path', 'existing-build', 'missing-msvc', 'tool-signature',
  'compiler-version', 'source', 'compile', 'build-cap', 'source-changed', 'binary', 'report', 'unexpected']);
const empty = () => ({ category: 'unexpected', code: 'none', source: 'none', line: 0 });
const validCompiler = (category, code, source, line) => {
  if (code === 'none') return source === 'none' && line === 0;
  if (category !== 'compile' || typeof code !== 'string') return false;
  if (code.length === 7 && /^LNK[1-9][0-9]{3}$/.test(code)) return source === 'none' && line === 0;
  if (code.length !== 5 || !/^C[1-9][0-9]{3}$/.test(code)) return false;
  return source === 'none' ? line === 0 : ['probe', 'shared', 'fixture', 'fixture-dll'].includes(source) &&
    Number.isInteger(line) && line >= 1 && line <= 4096;
};

export function parseBuildDiagnostic(text) {
  if (typeof text !== 'string' || Buffer.byteLength(text) > 512) return empty();
  const match = /^OWNED_IMAGE_BUILD\t1\t([a-z-]+)\t(none|C[1-9][0-9]{3}|LNK[1-9][0-9]{3})\t(none|probe|shared|fixture|fixture-dll)\t(0|[1-9][0-9]{0,3})\r?\n$/.exec(text);
  if (!match || match[0] !== text || !buildCategories.includes(match[1])) return empty();
  const [, category, code, source, number] = match;
  const line = Number(number);
  return validCompiler(category, code, source, line) ? { category, code, source, line } : empty();
}

const unexpected = 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0\n';
const phaseCategories = {
  host: ['host', 'unexpected'],
  build: [...buildCategories, 'launch', 'timeout', 'cap', 'interrupted'],
  pin: ['pin', 'interrupted', 'unexpected'],
  case: ['native', 'receipt', 'cleanup', 'timeout', 'cap', 'signal', 'interrupted', 'unexpected'],
};
export function formatFailure(value) {
  try {
    if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).some(key => !['phase', 'name', 'category', 'code', 'source', 'line'].includes(key))) return unexpected;
    const { phase, category, name = 'none', code = 'none', source = 'none', line = 0 } = value;
    if (typeof phase !== 'string' || typeof category !== 'string' || typeof name !== 'string' ||
      !Object.hasOwn(phaseCategories, phase) || !phaseCategories[phase].includes(category) ||
      (phase === 'case' ? !cases.includes(name) : phase === 'pin' ? name !== 'none' && !cases.includes(name) : name !== 'none') ||
      !validCompiler(category, code, source, line) || code !== 'none' && phase !== 'build') return unexpected;
    return `Owned image native qualification failed phase=${phase} case=${name} category=${category} code=${code} source=${source} line=${line}\n`;
  } catch { return unexpected; }
}
