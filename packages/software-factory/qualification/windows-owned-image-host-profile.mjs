// Qualification-only explicit Windows PowerShell inbox profile boundary.
import { win32 } from 'node:path';

export function inboxEnvironment(inherited, canonicalHost, selectedHost) {
  if (!inherited || typeof inherited !== 'object' || Array.isArray(inherited) || typeof canonicalHost !== 'string' ||
      typeof selectedHost !== 'string' || !/^[a-z]:\\/i.test(canonicalHost) ||
      /[;*?\[\]\x00-\x1f\x7f]/.test(canonicalHost) ||
      !/\\System32\\WindowsPowerShell\\v1\.0\\powershell\.exe$/i.test(canonicalHost) ||
      win32.normalize(canonicalHost).toLowerCase() !== win32.normalize(selectedHost).toLowerCase()) throw new Error('host-profile');
  const environment = {};
  const replaced = ['psmodulepath', 'winpsmodulepath', 'factory_owned_image_inbox', 'factory_owned_image_profile'];
  for (const [key, value] of Object.entries(inherited)) if (!replaced.includes(key.toLowerCase())) environment[key] = value;
  environment.PSModulePath = win32.join(win32.dirname(canonicalHost), 'Modules');
  environment.FACTORY_OWNED_IMAGE_INBOX = environment.PSModulePath;
  environment.FACTORY_OWNED_IMAGE_PROFILE = 'winps-inbox-only';
  return environment;
}

const checks = { environment: ['path', 'profile', 'inbox', 'assignment', 'reparse'],
  'management-import': ['manifest', 'reparse', 'import'], 'utility-import': ['manifest', 'reparse', 'import'],
  'security-import': ['manifest', 'reparse', 'import'], 'management-origin': ['count', 'capture', 'name', 'kind', 'manifest', 'base'],
  'utility-origin': ['count', 'capture', 'name', 'kind', 'manifest', 'base'], 'security-origin': ['count', 'capture', 'name', 'kind', 'manifest', 'base', 'authority'],
  'cmdlet-resolution': ['resolution', 'count'], 'cmdlet-origin': ['path', 'capture', 'authority', 'cmdlet-name', 'cmdlet-type', 'module-name', 'module-kind', 'manifest', 'base'],
  ready: ['none'], unknown: ['unknown'] };
function valid(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const hasRelation = Object.hasOwn(value, 'relation');
  if ('relation' in value && !hasRelation) return false;
  if (Object.keys(value).length !== (hasRelation ? 6 : 5) ||
      !Object.keys(value).every(key => ['profile', 'origin', 'availability', 'stage', 'field', 'relation'].includes(key)) ||
      value.profile !== 'winps-inbox-only' || !['inbox', 'refused', 'unverified'].includes(value.origin) ||
      !['available', 'unavailable'].includes(value.availability) ||
      typeof value.stage !== 'string' || typeof value.field !== 'string' ||
      !Object.hasOwn(checks, value.stage) || !checks[value.stage].includes(value.field)) return false;
  if (hasRelation) {
    const relation = value.relation;
    if (value.origin !== 'refused' || value.availability !== 'unavailable' || value.stage !== 'management-origin' || value.field !== 'base' ||
        !relation || typeof relation !== 'object' || Array.isArray(relation) || Object.keys(relation).length !== 4 ||
        !Object.keys(relation).every(key => ['kind', 'base', 'path', 'baseType'].includes(key)) ||
        !['manifest', 'binary', 'script', 'unknown'].includes(relation.kind) ||
        !['selected-manifest-directory', 'selected-WinPS-host-directory', 'inbox-root', 'other'].includes(relation.base) ||
        !['exact-selected-manifest', 'known-fixed-Management-binary-under-selected-host', 'other'].includes(relation.path) ||
        !['string', 'null', 'single-string-array', 'other'].includes(relation.baseType) ||
        (relation.baseType !== 'string' && relation.base !== 'other')) return false;
  }
  if (value.stage === 'ready') return value.origin === 'inbox' && value.availability === 'available';
  if (value.stage === 'unknown') return value.origin === 'unverified' && value.availability === 'unavailable';
  if (value.stage === 'cmdlet-origin') return value.origin === 'refused' && value.availability === 'available';
  if (value.availability !== 'unavailable') return false;
  if (value.origin === 'unverified') return true;
  return value.origin === 'refused' && !['assignment', 'import', 'resolution'].includes(value.field);
}
export function parseProfile(text) {
  if (typeof text !== 'string' || Buffer.byteLength(text) > 512) return null;
  const match = /^OWNED_IMAGE_PROFILE\t2\twinps-inbox-only\t(inbox|refused|unverified)\t(available|unavailable)\t([a-z-]+)\t([a-z-]+)\r?\n(?:OWNED_IMAGE_RELATION\t1\t([a-z]+)\t([A-Za-z-]+)\t([A-Za-z-]+)\t([a-z-]+)\r?\n)?$/.exec(text);
  if (!match || match[0] !== text) return null;
  const value = { profile: 'winps-inbox-only', origin: match[1], availability: match[2], stage: match[3], field: match[4] };
  if (match[5] !== undefined) value.relation = { kind: match[5], base: match[6], path: match[7], baseType: match[8] };
  return valid(value) ? value : null;
}
export function formatProfile(value) {
  if (!valid(value)) return 'Owned image host profile=winps-inbox-only origin=unverified availability=unavailable stage=unknown field=unknown\n';
  const relation = value.relation ? ` kind=${value.relation.kind} base=${value.relation.base} path=${value.relation.path} baseType=${value.relation.baseType}` : '';
  return `Owned image host profile=winps-inbox-only origin=${value.origin} availability=${value.availability} stage=${value.stage} field=${value.field}${relation}\n`;
}
