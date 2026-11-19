#!/usr/bin/env python3
"""Exercise the experimental copier's public process on a disposable tree."""
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    source, dest = root / 'source [x]', root / 'destination [x]'
    (source / 'nested').mkdir(parents=True)
    (source / '__pycache__').mkdir()
    (source / '__pycache__' / 'ignored').write_text('excluded')
    (source / 'nested' / 'odd [x].txt').write_text('fixture')
    (source / 'nested' / 'odd [x].txt').chmod(0o451)
    os.symlink('nested/odd [x].txt', source / 'link')
    os.symlink('nested', source / 'dir-link')
    os.symlink('missing', source / 'dangling-link')
    dest.mkdir()
    external = root / 'external'
    external.write_text('untouched')
    external.chmod(0o444)
    os.symlink(str(external), dest / 'nested-link-placeholder')
    (dest / 'note').write_text('keep')
    trace = root / 'scan.jsonl'
    env = dict(os.environ, ADAPTER_SCAN_TRACE=str(trace))
    (source / 'nested-link-placeholder').write_text('replacement')
    for _ in range(2):
        subprocess.run(['python3', str(HERE / 'copy.py'), str(source), str(dest)], check=True, env=env)
        assert (dest / 'nested' / 'odd [x].txt').read_text() == 'fixture'
        assert (dest / 'nested' / 'odd [x].txt').stat().st_mode & 0o777 == 0o451
        assert os.readlink(dest / 'link') == 'nested/odd [x].txt'
        assert not (dest / '__pycache__').exists()
        assert (dest / 'note').read_text() == 'keep'
        assert external.read_text() == 'untouched'
        assert external.stat().st_mode & 0o777 == 0o444
        assert (dest / 'nested-link-placeholder').read_text() == 'replacement'
    assert '__pycache__' not in trace.read_text()
print('PASS: prototype repeat, literal paths, modes, link and exclusion')
