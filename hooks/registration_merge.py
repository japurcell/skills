"""Merge the brain-owned registrations into mixed provider documents."""
import copy
import json
import re
import shlex

from hooks.families.brain import registrations


DOCUMENTS = {
    ".github/hooks/hooks.json": "copilot",
    ".gemini/settings.json": "gemini",
    ".codex/hooks.json": "codex",
    "skills/default/brain-install/assets/hooks/copilot.json": "copilot",
    "skills/default/brain-install/assets/hooks/gemini.json": "gemini",
    "skills/default/brain-install/assets/hooks/codex.json": "codex",
}
FIELDS = ("command", "commandWindows", "bash", "powershell")


def normalize(handler):
    result = copy.deepcopy(handler)
    for field in FIELDS:
        command = result.get(field)
        if not isinstance(command, str) or " -I -S -B -c " not in command:
            continue
        prefix, suffix = command.split(" -I -S -B -c ", 1)
        try:
            words = shlex.split(prefix.removeprefix("& "), posix=True)
        except ValueError:
            continue
        if words == ["py", "-3"]:
            words = ["py"]
        if len(words) != 1:
            continue
        path = words[0].replace("\\", "/")
        if (any(c in path for c in "$`;&|<>%!\r\n") or
            ("/" in path and not (path.startswith("/") or re.match(r"^[A-Za-z]:/", path)))):
            continue
        if re.fullmatch(r"(?:python(?:3(?:\.\d+)?)?|py)(?:\.exe)?", path.rsplit("/", 1)[-1]):
            result[field] = "python -I -S -B -c " + suffix
    return result


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def merge(data, provider):
    document = json.loads(data, object_pairs_hook=_object)
    if not isinstance(document, dict) or not isinstance(document.get("hooks"), dict):
        raise ValueError("hooks must be an object")
    if document.get("disableAllHooks") is True:
        raise ValueError("hooks are disabled")
    if provider == "copilot" and document.get("version", 1) != 1:
        raise ValueError("unsupported Copilot hooks version")
    hooks = document["hooks"]
    for event, (name, wanted) in registrations(provider).items():
        matches = []
        for old_event, entries in hooks.items():
            if provider == "gemini" and old_event == "disabled":
                if not isinstance(entries, list) or name in entries:
                    raise ValueError(f"disabled or invalid {name}")
                continue
            if not isinstance(entries, list):
                raise ValueError(f"invalid event {old_event}")
            for wrapper in entries:
                if not isinstance(wrapper, dict):
                    raise ValueError(f"invalid handler wrapper in {old_event}")
                handlers = [wrapper] if provider == "copilot" else wrapper.get("hooks")
                if not isinstance(handlers, list) or not all(isinstance(item, dict) for item in handlers):
                    raise ValueError(f"invalid handlers in {old_event}")
                for index, handler in enumerate(handlers):
                    if any(name in handler.get(field, "") for field in (*FIELDS, "exec") if isinstance(handler.get(field), str)) or handler.get("name") == name:
                        matches.append((old_event, wrapper, handlers, index, handler))
        if len(matches) > 1:
            raise ValueError(f"ambiguous {name} registration")
        if matches:
            old_event, wrapper, handlers, index, handler = matches[0]
            wanted_handler = wanted if provider == "copilot" else wanted["hooks"][0]
            outer = {} if provider == "copilot" else {k: v for k, v in wrapper.items() if k != "hooks"}
            expected_outer = {} if provider == "copilot" else {k: v for k, v in wanted.items() if k != "hooks"}
            if old_event != event or outer != expected_outer or normalize(handler) != normalize(wanted_handler):
                raise ValueError(f"customized {name} registration")
            if handler != wanted_handler:
                if provider == "copilot":
                    entries = hooks[event]
                    entries[entries.index(wrapper)] = wanted_handler
                else:
                    handlers[index] = wanted_handler
        else:
            hooks.setdefault(event, []).append(wanted)
    return document


def render(data, provider):
    merged = merge(data, provider)
    if merged == json.loads(data):
        return data
    return (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
