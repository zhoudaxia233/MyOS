"""Read-only static HTML views of a store and of saved traces. No scripts or external resources."""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import tempfile

from .store import TYPES, asset_type, is_core

MAP_NAME = 'myos-view.html'
PIPELINE_NAME = 'pipeline.html'
PREFIX = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="generator" content="myos-{kind}">'

MEANING = {
    'boundary': 'Limits and conditions on what agents do for the owner. A boundary can restrict an action; it never grants permission for an external one.',
    'context': 'Facts, values and stable preferences about the owner.',
    'principle': "How the owner judges and acts. The default; the owner's current explicit intent overrides it.",
    'method': 'How to think about or carry out a recurring kind of task.',
    'pattern': "A known tendency of the owner. Used to understand and anticipate the owner, and pointed out when it works against the owner's own interests; never a rule to follow or a preference to satisfy. Behavior, never a diagnosis.",
    'unclassified': 'Assets without a known type, usually legacy records. Hosts rely on their status and basis.',
}

STYLE = """
:root { --bg:#fbfaf8; --fg:#1d1d1f; --muted:#62626a; --card:#fff; --line:#e5e5ea; --accent:#0058d6; --core:#b3261e; --warn:#8a5a00; }
@media (prefers-color-scheme: dark) { :root { --bg:#141416; --fg:#f2f2f7; --muted:#a1a1a6; --card:#1f1f23; --line:#333338; --accent:#5aa2ff; --core:#ff8a80; --warn:#f0b35a; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); overflow-wrap:anywhere; font:15px/1.55 -apple-system, "PingFang SC", "Noto Sans CJK SC", "Segoe UI", sans-serif; }
main { max-width:980px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:26px; margin:0 0 4px; } h2 { font-size:19px; margin:32px 0 4px; } h3.request { font-size:17px; margin:24px 0 4px; }
.meaning, .meta { color:var(--muted); margin:0 0 8px; }
.note { border-left:3px solid var(--accent); padding:8px 12px; background:var(--card); margin:12px 0; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 14px; margin:10px 0; }
.card h3 { font-size:16px; margin:0 0 6px; }
.badge { display:inline-block; max-width:100%; font-size:12px; border:1px solid var(--line); border-radius:999px; padding:0 8px; margin:0 6px 4px 0; color:var(--muted); }
.badge.core, .badge.failed { color:var(--core); border-color:var(--core); }
.badge.pending { color:var(--warn); border-color:var(--warn); }
.applies { margin:6px 0 0; }
summary { cursor:pointer; color:var(--accent); margin-top:8px; }
.text { white-space:pre-wrap; }
pre { white-space:pre-wrap; font-size:12px; background:var(--bg); border:1px solid var(--line); border-radius:8px; padding:8px; }
ol.steps { padding-left:20px; } ol.steps li { margin:10px 0; }
.failed { color:var(--core); }
"""


def page(kind, title, body):
    return (f'{PREFIX.format(kind=kind)}<meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title>'
            f'<style>{STYLE}</style></head><body><main>{body}</main></body></html>\n')


def plural(n, word, words=None):
    return f'{n} {word}' if n == 1 else f'{n} {words or word + "s"}'


def inside(directory: Path, root: Path) -> bool:
    """Compare file identity, not spelling: case-insensitive file systems accept other spellings."""
    return root.exists() and any(d.exists() and os.path.samefile(d, root) for d in (directory, *directory.parents))


def write_private(path, html, *, kind, private_root, default_name):
    """Replace only an earlier MyOS page of the same kind; never write into store files or through a symlink."""
    path = Path(path).expanduser()
    if not path.parent.is_dir():
        raise ValueError(f'Output directory does not exist: {path.parent}')
    path = path.parent.resolve() / path.name
    root = Path(private_root).expanduser().resolve()
    if inside(path.parent, root) and not (os.path.samefile(path.parent, root) and path.name == default_name):
        raise ValueError(f'Write the page outside {root}, or use the default {root / default_name}')
    if path.is_symlink():
        raise ValueError(f'Refusing to write through a symlink: {path}')
    if path.exists():
        if not path.is_file():
            raise ValueError(f'Output path is not a regular file: {path}')
        prefix = PREFIX.format(kind=kind).encode()
        with open(path, 'rb') as f:
            if f.read(len(prefix)) != prefix:
                raise ValueError(f'Refusing to overwrite a file that is not an earlier MyOS {kind} page: {path}')
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.myos-page-', suffix='.html')  # created 0600
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    return path


def status_badge(status):
    kind = '' if status == 'adopted' else ' pending'
    return f'<span class="badge{kind}">{escape(str(status))}</span>'


def example_line(e):
    if isinstance(e, dict):
        return f'<li>{escape(str(e.get("text")))} <span class="badge">{escape(str(e.get("source")))}</span></li>'
    return f'<li>{escape(str(e))}</li>'


def card(store, a):
    badges = [f'<span class="badge">{escape(asset_type(a))}</span>', status_badge(a['status'])]
    if is_core(a):
        badges.insert(0, '<span class="badge core">core</span>')
    details = [f'<div class="text">{escape(str(a["content"]))}</div>']
    if a.get('boundaries'):
        details.append('<p><strong>Limits</strong></p><ul>' + ''.join(f'<li>{escape(str(b))}</li>' for b in a['boundaries']) + '</ul>')
    details.append(f'<p><strong>Basis</strong> {escape(str(a["basis"]))}</p>')
    if isinstance(a.get('examples'), list) and a['examples']:
        details.append('<p><strong>Examples</strong></p><ul>' + ''.join(example_line(e) for e in a['examples']) + '</ul>')
    details.append('<p><strong>Sources</strong></p><ul>' + ''.join(
        f'<li>{escape(str(s.get("ref") if isinstance(s, dict) else s))}</li>' for s in a['sources']) + '</ul>')
    history = store.read(a['id'], history=True)
    details.append('<p><strong>History</strong></p><ol>' + ''.join(
        f'<li>r{h["revision"]} · {escape(h["recorded_at"])} · {escape(str(h.get("status")))} · {escape(str(h["authorization"].get("request")))}</li>'
        for h in history) + '</ol>')
    return (f'<div class="card"><h3>{escape(str(a["title"]))}</h3>{"".join(badges)}<span class="badge">{escape(a["id"])} · r{a["revision"]}</span>'
            f'<p class="applies"><strong>Applies</strong> {escape(str(a["applicability"]))}</p>'
            f'<details><summary>Details</summary>{"".join(details)}</details></div>')


def render_map(store):
    if not store.path.exists():
        raise ValueError('No cognition store; initialize through an authorized write or migration')
    assets = store.current()
    active = [a for a in assets if a['status'] != 'inactive']
    core = [a for a in active if is_core(a)]
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    body = [f'<h1>MyOS map</h1><p class="meta">{escape(str(store.root))} · generated {escape(now)} · '
            f'{len(active)} active · {len(core)} core · {len(assets) - len(active)} inactive</p>',
            '<p class="note">How a host uses this store: one catalog call returns every core asset in full and an index of the rest. '
            "Core assets are always visible to the host; any asset, core or not, applies only when its applicability fits the request, and when unsure whether a boundary covers an action, it applies. Conflicts resolve in this order: "
            "the owner's current explicit instruction, then boundary, then principle and method, then pattern to anticipate the owner. "
            'Only adopted assets act as rules. Candidates are never used in answers: a first correction is saved quietly, '
            'a later matching correction prompts one question after the answer, and only the owner can adopt it. '
            'One-off means inactive; a retired idea that returns starts as a new candidate and needs a fresh repeat before a proposal. '
            'No answer leaves it a candidate without another question that session. '
            'Uncertain assets are material to weigh; reference assets are evidence.</p>',
            '<h2>Core</h2><p class="meaning">Adopted assets the owner marked core, returned in full on every catalog call so that they are never missed; they apply only where they fit.</p>']
    body += [card(store, a) for a in core] or ['<p class="meaning">No core assets yet.</p>']
    for kind in (*TYPES, 'unclassified'):
        group = [a for a in active if not is_core(a) and asset_type(a) == kind]
        if group:
            body.append(f'<h2>{escape(kind)}</h2><p class="meaning">{escape(MEANING[kind])}</p>')
            body += [card(store, a) for a in group]
    inactive = [a for a in assets if a['status'] == 'inactive']
    if inactive:
        body.append(f'<h2>Inactive</h2><details><summary>{plural(len(inactive), "asset")} kept for history, not used by hosts</summary>'
                    + ''.join(card(store, a) for a in inactive) + '</details>')
    return page('map', 'MyOS map', ''.join(body))


def event(call, phase):
    return next((e for e in call.get('events', []) if e.get('phase') == phase), {})


def operation(call):
    return str(call['operation']).removeprefix('myos_')


def purpose(call):
    for phase in ('handler_input', 'started'):
        inputs = event(call, phase).get('input')
        value = inputs.get('purpose') if isinstance(inputs, dict) else None
        if isinstance(value, str) and value.strip():
            return value
    return None


def summary(call):
    operation_name = operation(call)
    result = event(call, 'handler_result').get('result')
    if call.get('handler_outcome') == 'failed' or result is None:
        # Adapters wrap the handler's error again; the handler's own message is the specific one.
        errors = call.get('errors', [])
        first = next((e for e in errors if e.get('phase') == 'handler_error'), errors[0] if errors else {})
        return f'<span class="failed">{escape(str(first.get("error", "no result saved")))}</span>'
    try:
        if operation_name == 'catalog' and isinstance(result, list):
            return f'Catalog in the older list format: {plural(len(result), "entry", "entries")}'
        if operation_name == 'catalog':
            titles = ', '.join(f'{a["title"]} ({a.get("type", "unclassified")})' for a in result['core']) or 'none'
            return f'Core loaded: {escape(titles)} · index: {plural(len(result["index"]), "entry", "entries")}'
        if operation_name == 'read' and isinstance(result, list):
            return f'Read history of {escape(str(result[-1]["id"]))}: {plural(len(result), "revision")}'
        if operation_name == 'read':
            return f'Read {escape(str(result["id"]))} · {escape(str(result["title"]))} · r{escape(str(result["revision"]))}'
        if operation_name == 'put':
            return f'Wrote {escape(str(result["id"]))} · r{escape(str(result["revision"]))} · {escape(str(result["status"]))}'
        if operation_name == 'references':
            return f'Source: {escape(str((event(call, "handler_input").get("input") or {}).get("path") or "list"))}'
    except (KeyError, IndexError, TypeError, AttributeError):
        return '<span class="failed">Unreadable result; see saved events</span>'
    return escape(operation_name)


def step(call):
    state = {'success': '', 'failed': 'failed'}.get(call['status'], 'pending')
    label = f'<br><span class="meta">Purpose: {escape(p)}</span>' if operation(call) == 'catalog' and (p := purpose(call)) else ''
    return (f'<li><strong>{escape(str(call["operation"]))}</strong> <span class="badge">{escape(str(call.get("entry")))}</span>'
            f'<span class="badge {state}">{escape(str(call["status"]))}</span><span class="meta">{escape(str(call["time"]))}</span>{label}'
            f'<br>{summary(call)}<details><summary>Saved events</summary>'
            f'<pre>{escape(json.dumps(call.get("events", []), ensure_ascii=False, indent=2))}</pre></details></li>')


def stream(call):
    """One trace group, one MCP server process (one host session), or all ungrouped CLI calls."""
    if call.get('group_id'):
        return f'Group: {call["group_id"]}'
    if call.get('entry') == 'mcp':
        return f'MCP session {str(call["run_id"])[:18]}'
    return 'CLI calls'


def requests(calls):
    """Split one chronological stream into requests: each catalog call starts one."""
    sections = []
    for call in calls:
        if operation(call) == 'catalog':
            p = purpose(call)
            sections.append((f'Request: {p}' if p else 'Request without a recorded purpose', []))
        elif not sections:
            sections.append(('Calls before any catalog', []))
        sections[-1][1].append(call)
    return sections


def render_pipeline(timeline):
    streams = {}
    for call in sorted(timeline['calls'], key=lambda c: (str(c['time']), str(c['call_id']))):
        streams.setdefault(stream(call), []).append(call)
    body = ['<h1>MyOS pipeline</h1>',
            '<p class="note">These are saved MyOS tool calls in time order, separated by trace group or MCP session. '
            'Each catalog call starts a new request. Reading an asset does not prove it was applied, '
            "and the host's reasoning and final answer are not captured here.</p>"]
    body += [f'<p class="meta">{escape(w)}</p>' for w in timeline['warnings']]
    for name, calls in streams.items():
        if len(streams) > 1:
            body.append(f'<h2>{escape(name)}</h2>')
        for heading, section in requests(calls):
            body.append(f'<h3 class="request">{escape(heading)}</h3><ol class="steps">{"".join(step(c) for c in section)}</ol>')
    if not streams:
        body.append('<p class="meaning">No saved calls.</p>')
    return page('pipeline', 'MyOS pipeline', ''.join(body))
