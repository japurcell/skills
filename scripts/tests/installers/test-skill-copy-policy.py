#!/usr/bin/env python3
"""Exercise the shared skill traversal interface on disposable trees."""
import json
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[3]
helper = root / 'scripts/rebase-skill-references.py'
with tempfile.TemporaryDirectory() as temp:
    source = Path(temp) / 'source'
    dest = Path(temp) / 'dest'
    for path in ('SKILL.md', 'README.md', 'evals/data', 'tests/test.py', '__pycache__/bad.pyc', 'nested/keep'):
        target = source / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(path)
    for profile in ('overlay', 'replace'):
        trace = Path(temp) / f'{profile}-scan.jsonl'
        audit = "import json,os,runpy,sys; trace=sys.argv[1]; sys.argv=sys.argv[2:]; sys.addaudithook(lambda event,args: open(trace,'a').write(json.dumps(os.fspath(args[0]))+'\\n') if event=='os.scandir' else None); runpy.run_path(sys.argv[0],run_name='__main__')"
        result = subprocess.run(['python3', '-c', audit, str(trace), str(helper), '--source-dir', str(source), '--destination-dir', str(dest), '--emit-copy-operations', '--profile', profile], check=True, text=True, capture_output=True)
        operations = json.loads(result.stdout)
        paths = {Path(op['source']).relative_to(source).as_posix() for op in operations}
        assert '__pycache__' not in paths and 'tests' not in paths
        assert '__pycache__' not in trace.read_text()
        assert 'nested/keep' in paths
        assert ('README.md' in paths) == (profile == 'replace')
        assert ('evals/data' in paths) == (profile == 'replace')
print('PASS: shared traversal profiles')
