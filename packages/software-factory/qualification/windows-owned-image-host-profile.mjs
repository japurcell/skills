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

function valid(value) {
  return value && typeof value === 'object' && !Array.isArray(value) && Object.keys(value).length === 3 &&
    Object.keys(value).every(key => ['profile', 'origin', 'availability'].includes(key)) && value.profile === 'winps-inbox-only' &&
    ['inbox', 'refused', 'unverified'].includes(value.origin) && ['available', 'unavailable'].includes(value.availability) &&
    (value.origin !== 'inbox' || value.availability === 'available') &&
    (value.origin !== 'unverified' || value.availability === 'unavailable');
}
export function parseProfile(text) {
  if (typeof text !== 'string' || Buffer.byteLength(text) > 512) return null;
  const match = /^OWNED_IMAGE_PROFILE\t1\twinps-inbox-only\t(inbox|refused|unverified)\t(available|unavailable)\r?\n$/.exec(text);
  if (!match || match[0] !== text) return null;
  const value = { profile: 'winps-inbox-only', origin: match[1], availability: match[2] };
  return valid(value) ? value : null;
}
export function formatProfile(value) {
  if (!valid(value)) return 'Owned image host profile=winps-inbox-only origin=unverified availability=unavailable\n';
  return `Owned image host profile=winps-inbox-only origin=${value.origin} availability=${value.availability}\n`;
}
