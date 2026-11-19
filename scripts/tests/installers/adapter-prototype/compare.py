#!/usr/bin/env python3
"""Compare the experimental copy plus existing prune against both public installers."""
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
run = Path(tempfile.mkdtemp(prefix='adapter-compare-', dir='/private/tmp'))
repo = run / 'repo'
shutil.copytree(ROOT, repo, symlinks=True, ignore=shutil.ignore_patterns('.git', '__pycache__', '.pytest_cache'))
source = repo / 'skills/default/adapter-fixture'
(source / 'nested').mkdir(parents=True)
(source / '__pycache__').mkdir()
(source / 'evals').mkdir()
(source / 'SKILL.md').write_text('---\nname: adapter-fixture\ndescription: Fixture.\n---\nFixture.\n')
(source / 'nested/odd [x].txt').write_text('fixture')
(source / 'nested/odd [x].txt').chmod(0o451)
(source / '__pycache__/ignored').write_text('excluded')
(source / 'README.md').write_text('excluded')
(source / 'evals/data').write_text('excluded')
(source / 'test_sample.py').write_text('excluded')
os.symlink('nested/odd [x].txt', source / 'link')
os.symlink('nested', source / 'dir-link')
os.symlink('missing', source / 'dangling-link')

def invoke(label, command, env=None, expected=0):
    result = subprocess.run(command, cwd=repo, env=env, capture_output=True, text=True)
    (run / (label + '.stdout')).write_text(result.stdout)
    (run / (label + '.stderr')).write_text(result.stderr)
    (run / (label + '.exit')).write_text(str(result.returncode))
    if result.returncode != expected:
        raise RuntimeError(f'{label}: {result.returncode}, expected {expected}: {result.stderr}')

def snapshot(path):
    result = {}
    for item in sorted(path.rglob('*')):
        key = str(item.relative_to(path))
        if item.is_symlink(): result[key] = {'link': os.readlink(item)}
        elif item.is_file(): result[key] = {'mode': oct(stat.S_IMODE(item.stat().st_mode)), 'content': item.read_text()}
        else: result[key] = {'mode': oct(stat.S_IMODE(item.stat().st_mode)), 'directory': True}
    return result

homes = {name: run / name for name in ('bash', 'powershell', 'prototype')}
for name, home in homes.items():
    dest = home / '.agents/skills/adapter-fixture'
    dest.mkdir(parents=True)
    (dest / 'destination-only.txt').write_text('keep')
    for iteration in (1, 2):
        if name == 'prototype':
            invoke(f'{name}-{iteration}', ['python3', str(HERE / 'copy.py'), str(source), str(dest)])
            invoke(f'{name}-prune-{iteration}', ['python3', 'scripts/rebase-skill-references.py', '--source-dir', str(source), '--destination-dir', str(dest), '--prune'])
        else:
            env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / '.codex'), INSTALL_FOREST_SERVICE_SKILLS='0')
            command = ['bash', 'scripts/install.sh'] if name == 'bash' else ['pwsh', '-NoProfile', '-File', 'scripts/install.ps1']
            invoke(f'{name}-{iteration}', command, env)
        manifest = snapshot(dest)
        (run / f'{name}-{iteration}.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
        assert manifest == snapshot(homes['bash'] / '.agents/skills/adapter-fixture'), (name, iteration, manifest)
print(f'PASS: both public installers and prototype agree after install and refresh; evidence: {run}')
# A read-only destination hard link must fail without changing the external inode.
for name, home in homes.items():
    dest = home / '.agents/skills/adapter-fixture'
    external = run / (name + '-external')
    external.write_text('do not modify')
    external.chmod(0o444)
    target = dest / 'nested/odd [x].txt'
    target.unlink()
    os.link(external, target)
    dest.chmod(0o555)
    if name == 'prototype':
        command = ['python3', str(HERE / 'copy.py'), str(source), str(dest)]
        env = None
    else:
        command = ['bash', 'scripts/install.sh'] if name == 'bash' else ['pwsh', '-NoProfile', '-File', 'scripts/install.ps1']
        env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / '.codex'), INSTALL_FOREST_SERVICE_SKILLS='0')
    invoke(name + '-failure', command, env, expected=1)
    assert external.read_text() == 'do not modify'
    assert os.path.samefile(external, target)
    assert stat.S_IMODE(external.stat().st_mode) == 0o444
    assert stat.S_IMODE(dest.stat().st_mode) == 0o555
    (run / (name + '-failure-readback.json')).write_text(json.dumps({'external': external.read_text(), 'external_mode': oct(stat.S_IMODE(external.stat().st_mode)), 'destination_mode': oct(stat.S_IMODE(dest.stat().st_mode)), 'same_inode': os.path.samefile(external, target)}, indent=2) + '\n')
print(f'PASS: read-only hard-link failure and directory mode restoration; evidence: {run}')
