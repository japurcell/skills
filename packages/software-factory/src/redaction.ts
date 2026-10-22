/** Literal-only configuration avoids user-supplied regex backtracking and has bounded lookbehind. */
export class RedactionPolicy {
  readonly secrets: readonly string[];
  readonly lookbehind: number;
  constructor(secrets: readonly string[] = []) {
    if (!Array.isArray(secrets) || secrets.length > 128) throw new Error('invalid secret filter configuration');
    let total = 0;
    for (const value of secrets) {
      if (typeof value !== 'string' || !value.length || Buffer.byteLength(value) > 4096 || Buffer.from(value).toString('utf8') !== value) throw new Error('invalid secret filter configuration');
      total += Buffer.byteLength(value);
    }
    if (total > 65536) throw new Error('secret filter configuration exceeds limit');
    this.secrets = [...new Set(secrets)].sort((a, b) => b.length - a.length);
    this.lookbehind = Math.max(0, ...this.secrets.map(value => value.length - 1));
  }
  stream() { return new StreamingRedactor(this); }
}

const sensitive = /^(?:password|passwd|secret|token|access[_-]?token|refresh[_-]?token|api[_-]?key|authorization|credential|credentials|client[_-]?secret|private[_-]?key)$/i;

/** Masks JSON sensitive-field values, including nested values, without retaining those values. */
class StructuredFilter {
  private mode: 'normal' | 'candidate' | 'string' | 'afterKey' | 'value' | 'skip' = 'normal';
  private candidate = '';
  private escaped = false;
  private quoted = false;
  private depth = 0;
  private compound = false;
  get retainedBytes() { return this.candidate.length * 2; }
  push(input: string, final = false) {
    let output = '';
    for (let i = 0; i < input.length; i++) {
      const c = input[i]!;
      if (this.mode === 'skip') {
        if (this.quoted) {
          if (this.escaped) this.escaped = false;
          else if (c === '\\') this.escaped = true;
          else if (c === '"') { this.quoted = false; if (!this.compound) this.mode = 'normal'; }
        } else if (c === '"') this.quoted = true;
        else if (c === '{' || c === '[') this.depth++;
        else if (c === '}' || c === ']') {
          if (this.compound) { if (--this.depth === 0) this.mode = 'normal'; }
          else { this.mode = 'normal'; i--; }
        } else if (!this.compound && /[\s,]/.test(c)) { this.mode = 'normal'; i--; }
        continue;
      }
      if (this.mode === 'value') {
        if (/\s/.test(c)) { output += c; continue; }
        output += '"[REDACTED]"';
        this.mode = 'skip'; this.escaped = false; this.quoted = false;
        this.compound = c === '{' || c === '['; this.depth = 0;
        if (c === '"') this.quoted = true;
        else if (this.compound) this.depth = 1;
        else if (c === '}' || c === ']' || c === ',') { this.mode = 'normal'; i--; }
        continue;
      }
      if (this.mode === 'afterKey') {
        output += c;
        if (c === ':') this.mode = 'value';
        else if (!/\s/.test(c)) { this.mode = 'normal'; if (c === '"') { output = output.slice(0, -1); i--; } }
        continue;
      }
      if (this.mode === 'candidate') {
        this.candidate += c;
        if (this.escaped) this.escaped = false;
        else if (c === '\\') this.escaped = true;
        else if (c === '"') {
          let key: unknown;
          try { key = JSON.parse(this.candidate); } catch { key = null; }
          output += this.candidate; this.candidate = '';
          this.mode = typeof key === 'string' && sensitive.test(key) ? 'afterKey' : 'normal';
        }
        if (this.candidate.length > 2048) { output += this.candidate; this.candidate = ''; this.mode = 'string'; }
        continue;
      }
      if (this.mode === 'string') {
        output += c;
        if (this.escaped) this.escaped = false;
        else if (c === '\\') this.escaped = true;
        else if (c === '"') this.mode = 'normal';
        continue;
      }
      if (c === '"') { this.mode = 'candidate'; this.candidate = '"'; this.escaped = false; }
      else output += c;
    }
    if (final && this.candidate) { output += this.candidate; this.candidate = ''; }
    return output;
  }
}

/** Decodes only the bounded matching window; raw non-secret JSON spelling is retained exactly. */
class EscapedLiteralFilter {
  private raw = '';
  private decoded = '';
  private widths = new Uint8Array(0);
  private quoted = false;
  private escape = '';
  constructor(private readonly policy: RedactionPolicy) {}
  get retainedBytes() { return (this.raw.length + this.decoded.length + this.escape.length) * 2 + this.widths.byteLength; }
  push(input: string, final = false) {
    if (!this.policy.secrets.length) return input;
    let raw = this.raw, decoded = this.decoded;
    const widths = Array.from(this.widths);
    const add = (spelling: string, value: string) => { raw += spelling; decoded += value; widths.push(spelling.length); };
    const literal = (spelling: string) => { for (const c of spelling.split('')) add(c, c); };
    for (const c of input.split('')) {
      if (this.escape) {
        this.escape += c;
        if (this.escape.length === 2 && c !== 'u') {
          const translations: Record<string, string> = { '"': '"', '\\': '\\', '/': '/', n: '\n', r: '\r', t: '\t', b: '\b', f: '\f' };
          const value = translations[c];
          if (value === undefined) literal(this.escape); else add(this.escape, value);
          this.escape = '';
        } else if (this.escape.length === 6) {
          if (/^\\u[0-9a-f]{4}$/i.test(this.escape)) add(this.escape, String.fromCharCode(parseInt(this.escape.slice(2), 16)));
          else literal(this.escape);
          this.escape = '';
        }
      } else if (this.quoted && c === '\\') this.escape = c;
      else {
        if (c === '"') this.quoted = !this.quoted;
        add(c, c);
      }
    }
    if (final && this.escape) { literal(this.escape); this.escape = ''; }
    let safe = final ? decoded.length : Math.max(0, decoded.length - this.policy.lookbehind);
    if (safe > 0 && safe < decoded.length && /[\uD800-\uDBFF]/.test(decoded[safe - 1]!)) safe--;
    let output = '', index = 0, offset = 0;
    while (index < safe) {
      const match = this.policy.secrets.find(secret => decoded.startsWith(secret, index));
      if (match) {
        for (let count = 0; count < match.length; count++) offset += widths[index++]!;
        output += '[REDACTED]';
      } else {
        const width = widths[index++]!;
        output += raw.slice(offset, offset + width); offset += width;
      }
    }
    this.raw = raw.slice(offset); this.decoded = decoded.slice(index); this.widths = Uint8Array.from(widths.slice(index));
    return output;
  }
}

export class StreamingRedactor {
  private tail = '';
  private readonly structured = new StructuredFilter();
  private readonly escaped: EscapedLiteralFilter;
  constructor(private readonly policy: RedactionPolicy) { this.escaped = new EscapedLiteralFilter(policy); }
  get retainedBytes() { return this.tail.length * 2 + this.structured.retainedBytes + this.escaped.retainedBytes; }
  push(input: string, final = false) {
    const text = this.tail + this.escaped.push(this.structured.push(input, final), final);
    let safe = final ? text.length : Math.max(0, text.length - this.policy.lookbehind);
    if (safe > 0 && safe < text.length && /[\uD800-\uDBFF]/.test(text[safe - 1]!)) safe--;
    let output = '', index = 0;
    while (index < safe) {
      const match = this.policy.secrets.find(secret => text.startsWith(secret, index));
      if (match) { output += '[REDACTED]'; index += match.length; }
      else { output += text[index]!; index++; }
    }
    this.tail = text.slice(index);
    return output;
  }
}
