"""Self-contained source for later embedding into generated scanner hooks."""

from __future__ import annotations


SOURCE = r'''import codecs
import re
import sys
import unicodedata

_STREAM_SEPARATORS = re.compile(r"[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]+")
_STREAM_BINARY_TABLE = bytes(value if value in (9, 10, 13) or 32 <= value <= 126
                             else 32 for value in range(256))


def _stream_check():
    pass


def full_line_events(chunks, classification, check_budget=_stream_check):
    """Yield start/data/end tuples, omitting token-free empty full lines.

    Input is verified replay of at most 65536 bytes per chunk. Classification
    must already cover the entire snapshot. Empty lines advance numbering.
    """
    if classification not in ("text", "binary"):
        raise ValueError("invalid stream classification")
    decoder = codecs.getincrementaldecoder("utf-8")("replace")
    line_number = 1
    active = False
    pending_cr = False

    def decoded():
        for chunk in chunks:
            check_budget()
            if not isinstance(chunk, bytes) or len(chunk) > 65536:
                raise ValueError("invalid stream chunk")
            if classification == "binary":
                text = chunk.translate(_STREAM_BINARY_TABLE).decode("ascii")
            else:
                text = decoder.decode(chunk)
            for offset in range(0, len(text), 65536):
                yield text[offset:offset + 65536]
        if classification == "text":
            yield decoder.decode(b"", final=True)

    for text in decoded():
        check_budget()
        if not text:
            continue
        if pending_cr and text.startswith("\n"):
            text = text[1:]
        pending_cr = text.endswith("\r") if text else False
        position = 0
        for separator in _STREAM_SEPARATORS.finditer(text):
            if separator.start() > position:
                if not active:
                    yield ("start", line_number)
                    active = True
                yield ("data", text[position:separator.start()])
            if active:
                yield ("end", None)
                active = False
            run = separator.group()
            line_number += len(run) - run.count("\r\n")
            position = separator.end()
        if position < len(text):
            if not active:
                yield ("start", line_number)
                active = True
            yield ("data", text[position:])
    if active:
        yield ("end", None)


class StreamDiffError(ValueError):
    """Malformed verified diff; caller maps to git_output_invalid/git_diff."""


_STREAM_BYTE_SEPARATOR = re.compile(rb"\r\n|[\r\n]")
_STREAM_HUNK_START = re.compile(rb"\+[0-9]")
_STREAM_DIGITS = re.compile(rb"[0-9]*")


def _diff_byte_parts(chunks, check_budget):
    pending_cr = False
    first = bytearray()
    last = None
    for chunk in chunks:
        check_budget()
        if not isinstance(chunk, bytes) or len(chunk) > 65536:
            raise ValueError("invalid stream chunk")
        if not chunk:
            continue
        if len(first) < 11:
            first.extend(chunk[:11 - len(first)])
        last = chunk[-1]
        if pending_cr and chunk.startswith(b"\n"):
            chunk = chunk[1:]
        pending_cr = chunk.endswith(b"\r") if chunk else False
        position = 0
        for separator in _STREAM_BYTE_SEPARATOR.finditer(chunk):
            if separator.start() > position:
                yield ("data", chunk[position:separator.start()])
            yield ("end", None)
            position = separator.end()
        if position < len(chunk):
            yield ("data", chunk[position:])
    if last is not None and (bytes(first) != b"diff --git " or last != 10):
        raise StreamDiffError("invalid diff framing")


class _DiffLine:
    def __init__(self):
        self.prefix = b""
        self.kind = None
        self.decoder = None
        self.digits = b""
        self.hunk_state = "seek"
        self.plus = b""

    def hunk_data(self, data):
        if self.hunk_state == "done":
            return
        if self.hunk_state == "seek":
            data = self.plus + data
            match = _STREAM_HUNK_START.search(data)
            if match is None:
                self.plus = b"+" if data.endswith(b"+") else b""
                return
            data = data[match.start() + 1:]
            self.hunk_state = "digits"
        count = _STREAM_DIGITS.match(data).end()
        if len(self.digits) + count > 20:
            raise StreamDiffError("invalid diff hunk number")
        self.digits += data[:count]
        if count < len(data):
            self.hunk_state = "done"


def diff_added_line_events(chunks, check_budget=_stream_check):
    """Parse verified Git capture chunks, yielding only numbered added lines.

    CR/LF splitting precedes filesystem decoding with surrogateescape. Headers
    are discarded after an 11-byte discriminator; hunk numbers retain <=20
    decimal digits. This function never acquires or executes Git itself.
    """
    current_line = None
    line = _DiffLine()
    first_line = True
    for part, data in _diff_byte_parts(chunks, check_budget):
        check_budget()
        if part == "data" and line.kind is None:
            needed = 11 - len(line.prefix)
            line.prefix += data[:needed]
            data = data[needed:]
            if len(line.prefix) < 11:
                continue
        if line.kind is None:
            prefix = line.prefix
            line.prefix = b""
            if first_line and not prefix.startswith(b"diff --git "):
                raise StreamDiffError("invalid diff framing")
            first_line = False
            if prefix.startswith(b"diff --git "):
                current_line = None
                line.kind = "ignore"
            elif prefix.startswith(b"@@"):
                line.kind = "hunk"
            elif current_line is None:
                line.kind = "ignore"
            elif prefix.startswith(b"+"):
                line.kind = "added"
                line.decoder = codecs.getincrementaldecoder(sys.getfilesystemencoding())("surrogateescape")
                yield ("start", current_line)
                prefix = prefix[1:]
            elif prefix.startswith((b"-", b"\\")):
                line.kind = "ignore"
            elif prefix.startswith(b" "):
                line.kind = "context"
            else:
                raise StreamDiffError("invalid diff hunk content")
            if part == "data":
                data = prefix + data
            else:
                data = prefix
        if data:
            if line.kind == "hunk":
                line.hunk_data(data)
            elif line.kind == "added":
                # Prefix replay can add at most 11 bytes to a full fragment.
                # Keep every exported text event within the chunk contract.
                for offset in range(0, len(data), 65536):
                    text = line.decoder.decode(data[offset:offset + 65536])
                    for start in range(0, len(text), 65536):
                        yield ("data", text[start:start + 65536])
        if part == "end":
            if line.kind == "hunk":
                if not line.digits:
                    raise StreamDiffError("invalid diff hunk number")
                current_line = int(line.digits)
            elif line.kind == "added":
                text = line.decoder.decode(b"", final=True)
                if text:
                    yield ("data", text)
                yield ("end", None)
                current_line += 1
            elif line.kind == "context":
                current_line += 1
            line = _DiffLine()


# Every supported regex has an independent search cursor. The bounded regex
# search proves a minimum candidate in C; only a greedy span persists between
# fragments. Future patterns require an explicit entry and oracle fixtures.
_STREAM_PATTERNS = (
    ("github_classic_pat", "high", r"gh[pousr]_[A-Za-z0-9]{36}", 40, None),
    ("github_fine_grained_pat", "high", r"github_pat_[A-Za-z0-9_]{20,}", 31, r"[A-Za-z0-9_]*"),
    ("aws_access_key", "high", r"AKIA[0-9A-Z]{16}", 20, None),
    ("stripe_live_key", "high", r"sk_live_[0-9A-Za-z]{16,}", 24, r"[0-9A-Za-z]*"),
    ("slack_token", "medium", r"xox[baprs]-[0-9A-Za-z-]{10,}", 15, r"[0-9A-Za-z-]*"),
)
_STREAM_COMPILED = tuple((name, severity, re.compile(pattern), minimum,
                          re.compile(tail) if tail else None)
                         for name, severity, pattern, minimum, tail in _STREAM_PATTERNS)
_STREAM_FORBIDDEN_ESCAPE = re.compile(r"\\(?:n|r|t|x0[9ad]|u000[9ad])", re.IGNORECASE)
_STREAM_NONSPACE = re.compile(r"[^ ]")


class StreamReport:
    """Caller-owned report shared across candidates, including path findings."""

    def __init__(self, findings=None, processed=0):
        self.findings = findings if findings is not None else []
        self.processed = processed
        self.stopped = processed >= 1000


class _StreamPattern:
    def __init__(self, definition, path, line, is_allowlisted, redact, check_budget):
        self.name, self.severity, self.regex, self.minimum, self.tail = definition
        suffix = f":{line}:{self.name}:"
        first = _STREAM_NONSPACE.search(path)
        offset = first.start() if first else len(path)
        self.capacity = max(0, 8192 - (len(path) - offset + len(suffix)))
        self.key = path[offset:] + suffix if self.capacity else ""
        if (_STREAM_FORBIDDEN_ESCAPE.search(self.key)
                or any(unicodedata.category(char) == "Cc" for char in self.key)):
            self.capacity = 0
            self.key = ""
        self.is_allowlisted = is_allowlisted
        self.redact = redact
        self.check_budget = check_budget
        self.carry = ""
        self.length = 0
        self.first = ""
        self.last = ""
        self.value = ""
        self.count = 0
        self.matches = []

    def extend(self, text):
        if not text:
            return
        if not self.length:
            self.first = text[:4]
        self.length += len(text)
        self.last = (self.last + text[-4:])[-4:]
        if self.value is not None:
            if self.length <= self.capacity:
                self.value += text
            else:
                self.value = None

    def finish_match(self):
        if self.length:
            self.check_budget()
            if self.value is None or not self.is_allowlisted(self.key + self.value):
                self.count = min(1000, self.count + 1)
                if len(self.matches) < 100:
                    # Existing redaction keeps the first/last four for every
                    # supported token. The spacer preserves its length > 8 rule.
                    self.matches.append(self.redact(self.first + ":" + self.last))
            self.length = 0
            self.first = self.last = self.value = ""

    def feed(self, fragment):
        if self.count >= 1000:
            return
        text = self.carry + fragment
        self.carry = ""
        position = 0
        if self.length:
            end = self.tail.match(text).end()
            self.extend(text[:end])
            if end == len(text):
                return
            self.finish_match()
            position = end
        while position < len(text) and self.count < 1000:
            match = self.regex.search(text, position)
            if match is None:
                # Failed minimum candidates can contain later starts. Replaying
                # this bounded suffix preserves regex.search/finditer restart.
                self.carry = text[max(position, len(text) - self.minimum + 1):]
                return
            self.extend(match.group())
            position = match.end()
            if self.tail is not None and position == len(text):
                return
            self.finish_match()


def scan_line_events(path, events, report, is_allowlisted, redact,
                     check_budget=_stream_check):
    """Consume bounded events and update report in legacy line/pattern order.

    is_allowlisted(key) delegates to allowlist_contains('scan_secrets', key,
    entries); redact(value) is the existing redact_match helper. Credential-path
    findings must be inserted into the same report before this call. Events are
    drained after the cap to preserve late diff validation and deadline checks.
    The caller owns source/Git error mapping; failures are never hidden.
    """
    machines = None
    line = None
    for kind, value in events:
        check_budget()
        if report.stopped:
            continue
        if kind == "start":
            if machines is not None:
                raise ValueError("nested stream line")
            line = value
            machines = [_StreamPattern(definition, path, line, is_allowlisted, redact, check_budget)
                        for definition in _STREAM_COMPILED]
        elif kind == "data":
            if machines is None or not isinstance(value, str) or len(value) > 65536:
                raise ValueError("invalid stream data")
            for machine in machines:
                machine.feed(value)
        elif kind == "end":
            if machines is None:
                raise ValueError("unopened stream line")
            for machine in machines:
                machine.finish_match()
                accepted = min(machine.count, 1000 - report.processed)
                for redacted in machine.matches[:min(accepted, max(0, 100 - len(report.findings)))]:
                    report.findings.append((machine.name, machine.severity, path, line, redacted))
                report.processed += accepted
                if report.processed == 1000:
                    report.stopped = True
                    break
            machines = None
        else:
            raise ValueError("invalid stream event")
    if machines is not None and not report.stopped:
        raise ValueError("unterminated stream line")
'''
