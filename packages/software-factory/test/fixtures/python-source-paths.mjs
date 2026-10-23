import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';

// The verifier requires Python's canonical spelling, which can differ from
// Node's realpath spelling on Windows. Resolve only existing fixture inputs.
export function pythonSourcePaths(python, bundle, archive) {
  const result = spawnSync(python, ['-I', '-c', 'import json,sys; from pathlib import Path; print(json.dumps([str(Path(p).resolve(strict=True)) for p in sys.argv[1:]]))', bundle, archive], { encoding: 'utf8', timeout: 5000, maxBuffer: 16 * 1024 });
  assert.equal(result.status, 0, result.stderr);
  const [pythonBundle, pythonArchive] = JSON.parse(result.stdout);
  return { pythonBundle, pythonArchive };
}
