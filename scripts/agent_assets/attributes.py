"""Preserve Git checkout policy and own only exact new path rules."""

from pathlib import Path
import tempfile

from .sources import AssetError, git


def observed(root: Path, paths):
    values = {}
    attributes = ("text", "eol", "filter", "working-tree-encoding", "ident", "crlf")
    output = git(root, "check-attr", "-z", *attributes, "--", *paths).split(b"\0")
    for index in range(0, len(output) - 1, 3):
        path, name, value = (part.decode("utf-8") for part in output[index:index + 3])
        values.setdefault(path, {})[name] = value
    return values


def plan(root: Path, files, existing):
    path = root / ".gitattributes"
    original = path.read_bytes() if path.exists() else b""
    policy = {name: ["-text"] if value[3]["content"] == "binary" else ["text", "eol=" + value[3]["line_endings"]]
              for name, value in files.items()}
    current = observed(root, list(policy))
    owned = existing[1]["attributes"] if existing else []
    owned_names = {entry["destination"] for entry in owned}
    for name, values in current.items():
        if any(values[key] != "unspecified" for key in ("filter", "working-tree-encoding", "ident", "crlf")):
            raise AssetError("ASSET_CONFLICT", f"Unsupported checkout transform: {name}. Resolve Git attributes first.", 1)
        if name in owned_names:
            continue
        expected = policy[name]
        if values["text"] not in (("unspecified", "unset") if expected == ["-text"] else ("unspecified", "set", "auto")) or (
            values["eol"] not in (("unspecified",) if expected == ["-text"] else ("unspecified", expected[1].split("=")[1]))
        ):
            raise AssetError("ASSET_CONFLICT", f"Incompatible checkout policy: {name}. Resolve Git attributes first.", 1)
    if existing:
        begin, end = b"# agent-assets begin\n", b"# agent-assets end\n"
        if owned and (original.count(begin) != 1 or original.count(end) != 1 or original.index(begin) > original.index(end)):
            raise AssetError("ASSET_CONFLICT", "Owned checkout rule markers changed; restore recorded rules and rerun.", 1)
        block = original.split(begin, 1)[1].split(end, 1)[0] if owned else b""
        for entry in owned:
            line = ('"' + entry["destination"] + '" ' + " ".join(entry["values"]) + "\n").encode()
            if original.count(line) != 1 or block.count(line) != 1:
                raise AssetError("ASSET_CONFLICT", "Owned checkout rules changed; restore recorded rules and rerun.", 1)
        for entry in owned:
            original = original.replace(('"' + entry["destination"] + '" ' + " ".join(entry["values"]) + "\n").encode(), b"")
        if owned:
            original = original.replace(begin, b"").replace(end, b"")
    new = [{"destination": name, "values": values} for name, values in sorted(policy.items())
           if name in owned_names or not compatible(values, current[name])]
    if not new:
        return original, []
    # The owned block is byte-exact too. Protect its LF markers from autocrlf
    # without claiming a preexisting compatible metadata rule.
    policy[".gitattributes"] = ["text", "eol=lf"]
    metadata = observed(root, [".gitattributes"])[".gitattributes"]
    if any(metadata[key] != "unspecified" for key in ("filter", "working-tree-encoding", "ident", "crlf")) or (
        metadata["text"] not in ("unspecified", "set", "auto") or metadata["eol"] not in ("unspecified", "lf")
    ):
        raise AssetError("ASSET_CONFLICT", "Incompatible checkout policy: .gitattributes. Resolve Git attributes first.", 1)
    if ".gitattributes" in owned_names or not compatible(policy[".gitattributes"], metadata):
        new.insert(0, {"destination": ".gitattributes", "values": policy[".gitattributes"]})
    if b"# agent-assets begin" in original or b"# agent-assets end" in original:
        raise AssetError("ASSET_CONFLICT", "Unowned agent-assets checkout block exists; resolve its ownership first.", 1)
    block = b"# agent-assets begin\n" + b"".join(
        ('"' + entry["destination"] + '" ' + " ".join(entry["values"]) + "\n").encode() for entry in new
    ) + b"# agent-assets end\n"
    proposed = original + (b"\n" if original and not original.endswith(b"\n") else b"") + block
    with tempfile.TemporaryDirectory(prefix="agent-assets-attributes-") as temporary:
        mirror = Path(temporary)
        git(mirror, "init", "-q")
        paths = {parent / ".gitattributes" for name in policy for parent in Path(name).parents if parent != Path(".")}
        for relative in paths:
            source = root / relative
            if source.is_symlink():
                raise AssetError("ASSET_CONFLICT", "Linked Git attribute policy refused; resolve it before installing.", 1)
            if source.exists():
                destination = mirror / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
        (mirror / ".gitattributes").write_bytes(proposed)
        info = Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "info/attributes").decode().strip())
        if info.exists():
            (mirror / ".git/info/attributes").write_bytes(info.read_bytes())
        for entry in git(root, "config", "--null", "--list").split(b"\0"):
            key, _, value = entry.partition(b"\n")
            if key == b"core.attributesfile":
                configured = value.decode()
                absolute = str((root / configured).resolve()) if not Path(configured).is_absolute() else configured
                git(mirror, "config", "core.attributesFile", absolute)
        resulting = observed(mirror, list(policy))
        if any(not compatible(policy[name], values)
               or any(values[key] != "unspecified" for key in ("filter", "working-tree-encoding", "ident", "crlf"))
               for name, values in resulting.items()):
            raise AssetError("ASSET_CONFLICT", "Higher-precedence Git attributes prevent declared checkout bytes; resolve the rules first.", 1)
    return proposed, new


def compatible(policy, values):
    if policy == ["-text"]:
        return values["text"] == "unset" and values["eol"] == "unspecified"
    return values["text"] in ("set", "auto") and values["eol"] == policy[1].split("=")[1]


def verify(root, lock):
    original = root.joinpath(".gitattributes").read_bytes() if root.joinpath(".gitattributes").exists() else b""
    begin, end = b"# agent-assets begin\n", b"# agent-assets end\n"
    owned = lock["attributes"]
    if owned:
        if original.count(begin) != 1 or original.count(end) != 1 or original.index(begin) > original.index(end):
            raise AssetError("ASSET_DRIFT", "Owned checkout markers changed.", 1)
        block = original.split(begin, 1)[1].split(end, 1)[0]
        for entry in owned:
            line = ('"' + entry["destination"] + '" ' + " ".join(entry["values"]) + "\n").encode()
            if original.count(line) != 1 or block.count(line) != 1:
                raise AssetError("ASSET_DRIFT", "Owned checkout rule changed: " + entry["destination"], 1)
    paths = [item["destination"] for item in lock["items"]]
    if lock.get("attribute_file_policy") or any(entry["destination"] == ".gitattributes" for entry in owned):
        paths.append(".gitattributes")
    current = observed(root, paths)
    if ".gitattributes" in paths and (not compatible(["text", "eol=lf"], current[".gitattributes"])
            or any(current[".gitattributes"][key] != "unspecified" for key in ("filter", "working-tree-encoding", "ident", "crlf"))):
        raise AssetError("ASSET_DRIFT", "Effective checkout policy changed: .gitattributes", 1)
    for item in lock["items"]:
        policy = ["-text"] if item["content"] == "binary" else ["text", "eol=" + item["line_endings"]]
        values = current[item["destination"]]
        if not compatible(policy, values) or any(values[key] != "unspecified" for key in ("filter", "working-tree-encoding", "ident", "crlf")):
            raise AssetError("ASSET_DRIFT", "Effective checkout policy changed: " + item["destination"], 1)
