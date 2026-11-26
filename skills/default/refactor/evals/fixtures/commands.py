import importlib


def dispatch(command, value):
    return importlib.import_module(f"command_{command}").run(value)
