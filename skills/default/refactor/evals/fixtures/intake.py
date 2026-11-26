from labels import display


def lookup(text):
    return text.strip().casefold()


def caption(text):
    return text.strip() or "(untitled)"
