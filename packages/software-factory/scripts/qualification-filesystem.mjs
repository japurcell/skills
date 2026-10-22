import { spawnSync } from 'node:child_process';
import { statfsSync } from 'node:fs';
import { tmpdir } from 'node:os';

if (process.env.GITHUB_ACTIONS !== 'true' || process.platform !== 'darwin') {
  process.stderr.write('filesystem diagnostic requires ephemeral GitHub Actions on macOS\n');
  process.exitCode = 1;
} else {
  const locations = [...new Set([process.cwd(), tmpdir(), process.env.RUNNER_TEMP].filter(Boolean))];
  const filesystems = locations.map(path => {
    try { return { path, nativeType: statfsSync(path).type }; }
    catch { return { path, error: 'statfs unavailable' }; }
  });
  const commands = [
    { file: '/sbin/mount', args: [] },
    { file: '/bin/df', args: ['-h', ...locations] },
    ...locations.map(path => ({ file: '/usr/sbin/diskutil', args: ['info', '-plist', path] })),
  ];
  const observations = commands.map(({ file, args }) => {
    const result = spawnSync(file, args, { encoding: 'utf8', timeout: 2000, maxBuffer: 65536, stdio: ['ignore', 'pipe', 'pipe'] });
    return { file, args, exitCode: result.status, signal: result.signal, output: result.stdout ?? '',
      error: result.error ? 'native diagnostic unavailable' : result.stderr ?? '' };
  });
  process.stdout.write(JSON.stringify({ scope: 'diagnostic-only', filesystems, observations }) + '\n');
}
