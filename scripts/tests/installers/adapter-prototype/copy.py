#!/usr/bin/env python3
"""Experimental traversal; one PowerShell process executes one skill's operations."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('policy', ROOT / 'scripts/rebase-skill-references.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
source, destination = map(lambda p: Path(p).absolute(), sys.argv[1:3])
operations = []
# Optional evidence of actual enumeration, not just the resulting destination.
trace = os.environ.get('ADAPTER_SCAN_TRACE')
if trace:
    def audit(event, args):
        if event == 'os.scandir':
            with open(trace, 'a', encoding='utf-8') as stream:
                stream.write(json.dumps(os.fspath(args[0])) + '\n')
    sys.addaudithook(audit)

def walk(src, dst):
    operations.append({'kind': 'enter', 'source': str(src), 'destination': str(dst)})
    for entry in sorted(policy.filtered_entries(src), key=lambda item: item.name):
        child = Path(entry.path)
        target = dst / entry.name
        if policy.is_link_or_junction(child):
            kind = 'link'
        elif entry.is_dir(follow_symlinks=False):
            walk(child, target)
            continue
        else:
            kind = 'file'
        operations.append({'kind': kind, 'source': str(child), 'destination': str(target)})
    operations.append({'kind': 'leave', 'source': str(src), 'destination': str(dst)})

walk(source, destination)
result = subprocess.run(['pwsh', '-NoProfile', '-File', str(HERE / 'adapter.ps1'), str(ROOT / 'scripts/install.ps1')], input=json.dumps(operations), text=True)
sys.exit(result.returncode)
