#!/usr/bin/env python3
"""Install software only into explicit immutable bundles; never activate a repository."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/agent-brain/scripts"))
from agent_brain import __version__
from agent_brain.software import (ADAPTER_VERSION, checked_absolute, compatible_interpreter,
    inventory, inventory_revision, validate_software)
from agent_brain.history import replace_content
from agent_brain.state import LifecycleError


def checked_shipping_source(source, files):
    """Read metadata and syntax only, never import caller-supplied software."""
    trusted = Path(__file__).resolve().parents[1] / "skills/agent-brain"
    required = {name for name in inventory(trusted) if not name.startswith("evals/")}
    if not required.issubset(files):
        missing = sorted(required - set(files))
        raise LifecycleError("SOFTWARE_UNAVAILABLE", "shipping source is incomplete; restore required files: " + ", ".join(missing[:8]))
    expected = json.loads((trusted / "schemas/version.json").read_text(encoding="utf-8"))
    if json.loads((source / "schemas/version.json").read_text(encoding="utf-8")) != expected:
        raise LifecycleError("SOFTWARE_UNAVAILABLE", "shipping core/schema version identity is incompatible with the exact available installer")
    tree = ast.parse((source / "scripts/agent_brain/software.py").read_text(encoding="utf-8"))
    adapters = [node.value.value for node in tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "ADAPTER_VERSION" for target in node.targets)
        and isinstance(node.value, ast.Constant)]
    if adapters != [ADAPTER_VERSION]:
        raise LifecycleError("SOFTWARE_UNAVAILABLE", "shipping adapter identity does not match the exact pinned adapter")
    for name in required:
        path = source / name
        if name.endswith(".py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=name)
        elif name.startswith("schemas/") and name.endswith(".schema.json"):
            actual = json.loads(path.read_text(encoding="utf-8"))
            canonical = json.loads((trusted / name).read_text(encoding="utf-8"))
            if actual.get("$id") != canonical.get("$id") or actual.get("$schema") != canonical.get("$schema"):
                raise LifecycleError("SOFTWARE_UNAVAILABLE", "shipping schema identity is incompatible: " + name)


def install(args):
    source = checked_absolute(Path(args.source).absolute(), directory=True)
    destination = checked_absolute(Path(args.software_dir).absolute(), directory=True)
    bin_dir = checked_absolute(Path(args.bin_dir).absolute(), directory=True)
    runtime = compatible_interpreter(Path(args.python))
    files = inventory(source)
    checked_shipping_source(source, files)
    revision = inventory_revision(files)
    for name, requested, available in (("core", args.core_version, __version__), ("adapter", args.adapter_version, ADAPTER_VERSION),
            ("schema", args.schema_version, 1)):
        if requested is not None and requested != available:
            raise LifecycleError("SOFTWARE_UNAVAILABLE", f"requested pinned {name} version {requested} is unavailable; no substitution is allowed")
    bundle = destination / "versions" / f"{__version__}-{ADAPTER_VERSION}-s1" / revision
    checked_absolute(bundle, directory=True)
    windows = os.name == "nt" or args.platform == "windows"
    launcher = bin_dir / ("agent-brain.cmd" if windows else "agent-brain")
    bootstrap = bin_dir / "agent-brain-launch.py"
    launchers = {launcher: ('@echo off\r\nrem agent-brain immutable launcher\r\n"' + runtime["executable"] + '" "' + str(bootstrap) + '" %*\r\n') if windows
        else "#!/bin/sh\n# agent-brain immutable launcher\nexec " + __import__("shlex").join([runtime["executable"], str(bootstrap)]) + ' "$@"\n'}
    if windows:
        launchers[bin_dir / "agent-brain.ps1"] = "# agent-brain immutable launcher\n& '" + runtime["executable"].replace("'", "''") + "' '" + str(bootstrap).replace("'", "''") + "' @args\nexit $LASTEXITCODE\n"
    for path in launchers:
        checked_absolute(path)
        if path.exists() and "# agent-brain immutable launcher" not in path.read_text(encoding="utf-8") and "rem agent-brain immutable launcher" not in path.read_text(encoding="utf-8"):
            raise LifecycleError("LAUNCHER_CONFLICT", "an unrelated launcher occupies the destination; select another explicit bin directory")
    manifest = {"schema_version": 1, "core_version": __version__, "adapter_version": ADAPTER_VERSION,
        "inventory_revision": revision, "files": files, "interpreter": runtime,
        "launcher": str(launcher), "bundle_path": str(bundle)}
    launchers[bootstrap] = bootstrap_source(bundle, destination, manifest)
    checked_absolute(bootstrap)
    if bootstrap.exists() and "# agent-brain immutable launcher" not in bootstrap.read_text(encoding="utf-8"):
        raise LifecycleError("LAUNCHER_CONFLICT", "an unrelated bootstrap occupies the selected bin directory")
    if bundle.exists():
        raw = (bundle / "software.json").read_bytes()
        pin = {name: manifest[name] for name in ("bundle_path", "core_version", "adapter_version", "schema_version")}
        validate_software(pin | {"manifest_revision": hashlib.sha256(raw).hexdigest()})
        existing = json.loads(raw)
        if existing != manifest:
            raise LifecycleError("SOFTWARE_CONFLICT", "immutable bundle already pins another interpreter or launcher; select another software location")
    if not args.check:
        if not bundle.exists():
            bundle.parent.mkdir(parents=True, exist_ok=True)
            temporary = Path(tempfile.mkdtemp(prefix=".install-", dir=bundle.parent))
            try:
                for relative in files:
                    target = temporary / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source / relative, target)
                    os.chmod(target, 0o444)
                (temporary / "software.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True), encoding="utf-8")
                os.chmod(temporary / "software.json", 0o444)
                if inventory(temporary) != files:
                    raise LifecycleError("SOFTWARE_CHANGED", "source software changed during installation; retry after sources settle")
                os.rename(temporary, bundle)
            finally:
                if temporary.exists():
                    shutil.rmtree(temporary)
        for path, content in launchers.items():
            replace_content(path, content)
            if not windows:
                os.chmod(path, 0o755)
    return {"schema_version": 1, "operation_status": "ok", "command": "install", "checked_only": args.check,
        "core_version": __version__, "adapter_version": ADAPTER_VERSION, "bundle_path": str(bundle),
        "launcher": str(launcher), "path_action": f"Add {bin_dir} to PATH if absent; shell profiles are unchanged.",
        "activation": "disabled"}


def bootstrap_source(bundle, destination, manifest):
    """Validate code without importing bundle bytes; the launcher is the install trust anchor."""
    raw = json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode()
    prefix = "# agent-brain immutable launcher\nimport hashlib,json,os,runpy,sys\nfrom pathlib import Path\nsys.dont_write_bytecode=True\n"
    prefix += "DEFAULT=" + repr(str(bundle)) + "\nSOFTWARE=" + repr(str(destination / "versions")) + "\nREVISION=" + repr(hashlib.sha256(raw).hexdigest()) + "\n"
    return prefix + '''
def checked(path):
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('software path is ambiguous')
    current=Path(path.anchor)
    for part in path.parts[1:]:
        current/=part
        if current.is_symlink() or (current.exists() and getattr(current.lstat(),'st_file_attributes',0)&0x400):
            raise ValueError('linked software path')
    return path
try:
    bundle=checked(Path(DEFAULT))
    expected=REVISION
    config=Path('.agents/context/config.json')
    for index,word in enumerate(sys.argv[1:]):
        if word=='--config' and index+2<len(sys.argv):
            config=Path(sys.argv[index+2])
        elif word.startswith('--config='):
            config=Path(word.split('=',1)[1])
    # Help is always independent of active-context validation.
    if not any(word in ('--help','-h','help','--version','-V') for word in sys.argv[1:]) and config.is_file():
        pin=json.loads(config.read_text(encoding='utf-8')).get('software',{})
        if pin:
            bundle=checked(Path(pin['bundle_path']))
            if not bundle.is_relative_to(checked(Path(SOFTWARE))):
                raise ValueError('pinned software is outside this selected installation')
            expected=pin['manifest_revision']
    manifest_path=checked(bundle/'software.json')
    if not manifest_path.is_file() or manifest_path.stat().st_size>8*1024*1024:
        raise ValueError('software manifest is unavailable or oversized')
    raw=manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError('exact pinned software manifest is unavailable')
    manifest=json.loads(raw)
    if manifest['bundle_path']!=str(bundle):
        raise ValueError('software manifest was relocated')
    actual={}
    for path in bundle.rglob('*'):
        relative=path.relative_to(bundle).as_posix()
        if '__pycache__' in path.parts or path.suffix=='.pyc':
            raise ValueError('unpinned installed bytecode is unavailable')
        if relative=='software.json':
            continue
        checked(path)
        if path.is_file():
            if path.stat().st_size>8*1024*1024 or len(actual)>=2000:
                raise ValueError('installed inventory exceeds bounded size')
            actual[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError('software inventory is not ordinary files and directories')
    if actual!=manifest['files']:
        raise ValueError('immutable installed software bytes changed')
except (OSError,ValueError,KeyError,TypeError) as error:
    if '--json' in sys.argv:
        print(json.dumps({'schema_version':1,'operation_status':'error','error':{'code':'SOFTWARE_UNAVAILABLE','cause':str(error),'next_action':'Restore the exact pinned software bundle.'}}))
    print('agent-brain: SOFTWARE_UNAVAILABLE: '+str(error),file=sys.stderr)
    raise SystemExit(2)
sys.path.insert(0,str(bundle/'scripts'))
runpy.run_path(str(bundle/'scripts/agent-brain.py'),run_name='__main__')
'''


def main():
    parser = argparse.ArgumentParser(allow_abbrev=False, description=__doc__)
    parser.add_argument("--source", default=str(Path(__file__).resolve().parents[1] / "skills/agent-brain"))
    parser.add_argument("--software-dir", required=True)
    parser.add_argument("--bin-dir", required=True)
    parser.add_argument("--python", required=True, help="Explicit discovered compatible interpreter; nothing is downloaded.")
    parser.add_argument("--core-version")
    parser.add_argument("--adapter-version")
    parser.add_argument("--schema-version", type=int)
    parser.add_argument("--platform", choices=("posix", "windows"))
    parser.add_argument("--check", action="store_true", help="Preflight only; make no writes.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = install(args)
    except (LifecycleError, OSError, ValueError, SyntaxError) as exc:
        result = {"schema_version": 1, "operation_status": "error", "error": {"code": getattr(exc, "code", "INSTALL_INVALID"),
            "cause": str(exc), "next_action": "Correct the explicit destinations and exact software/runtime pins; retry preflight."}}
        print("agent-brain: " + result["error"]["cause"], file=sys.stderr)
        if args.json:
            print(json.dumps(result))
        return getattr(exc, "exit_code", 2)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Software: {result['bundle_path']}\nLauncher: {result['launcher']}\n{result['path_action']}\nRepository activation: disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
