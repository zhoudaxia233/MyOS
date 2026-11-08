"""Asset type, core set and examples tell hosts how to use the owner's self-model."""
import asyncio
import json
import os
import re
import subprocess
import sys

import pytest

from myos.personal import tracing
from myos.personal.store import CORE_LIMIT, EXPORT_BEGIN, EXPORT_END, REPLAY, Store
from myos.personal.view import render_map, render_pipeline
from tests.test_personal_store import AUTH, asset, record_migration


def typed(**updates):
    return {**asset(), **updates}


def adopted_core(n, kind='boundary'):
    return typed(id=f'core-{n}', title=f'Core {n}', type=kind, status='adopted', core=True)


def cli(root, *args):
    return subprocess.run([sys.executable, '-m', 'myos', '--data', str(root), *args], capture_output=True, text=True)


def test_judgment_entries_require_a_type_even_before_adoption(tmp_path):
    s = Store(tmp_path)
    untyped = typed()
    untyped.pop('type')
    for status in ('candidate', 'adopted', 'uncertain'):
        with pytest.raises(ValueError, match='Type is required'):
            s.put(dict(untyped, status=status), expected_revision=0, authorization=AUTH)
    assert not s.path.exists()
    s.put(dict(untyped, id='kept', status='reference'), expected_revision=0, authorization=AUTH)
    s.put(dict(untyped, id='retired', status='inactive'), expected_revision=0, authorization=AUTH)
    s.put(dict(untyped, id='legacy', status='uncertain'), expected_revision=0, authorization=dict(AUTH, mode='migration'), migration=REPLAY)
    assert {a['id']: a['type'] for a in s.catalog()['index']} == {'kept': 'unclassified', 'legacy': 'unclassified'}


@pytest.mark.parametrize('change, message', [
    ({'type': 'rule'}, 'Type must be one of'),
    ({'core': 'yes'}, 'Core must be true or false'),
    ({'core': True}, 'Only adopted assets can be core'),
    ({'examples': [{'text': 'An instance'}]}, 'Examples must be'),
    ({'examples': [{'text': ' ', 'source': 'owner-message:3'}]}, 'Examples must be'),
    ({'examples': 'not a list'}, 'Examples must be'),
])
def test_invalid_use_fields_are_refused(tmp_path, change, message):
    with pytest.raises(ValueError, match=message):
        Store(tmp_path).put(typed(**change), expected_revision=0, authorization=AUTH)
    assert not (tmp_path / 'cognition.sqlite3').exists()


def test_core_budget_counts_current_assets_only(tmp_path):
    s = Store(tmp_path)
    for n in range(CORE_LIMIT):
        s.put(adopted_core(n), expected_revision=0, authorization=AUTH)
    with pytest.raises(ValueError, match=f'limited to {CORE_LIMIT} assets; ask the owner'):
        s.put(adopted_core(CORE_LIMIT), expected_revision=0, authorization=AUTH)
    # Revising a core asset keeps its own slot.
    revised = adopted_core(0)
    revised['content'] = 'Revised'
    s.put(revised, expected_revision=1, authorization=AUTH)
    # Leaving the core frees a slot for another asset.
    s.put(dict(adopted_core(1), core=False), expected_revision=1, authorization=AUTH)
    s.put(adopted_core(CORE_LIMIT), expected_revision=0, authorization=AUTH)
    assert len(s.catalog()['core']) == CORE_LIMIT
    assert s.check(strict=True)['errors'] == []


def test_catalog_returns_core_in_full_and_a_compact_ordered_index(tmp_path):
    s = Store(tmp_path)
    example = [{'text': 'Show the draft, then wait for the click', 'source': 'owner-message:4'}]
    s.put(typed(id='send', title='Final click is mine', type='boundary', status='adopted', core=True, examples=example), expected_revision=0, authorization=AUTH)
    s.put(typed(id='side', title='Take my side', type='principle', status='adopted'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='habit', title='Relief is not judgment', type='pattern'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='who', title='Who I am', type='context', status='adopted'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='gone', status='inactive'), expected_revision=0, authorization=AUTH)
    catalog = s.catalog()
    assert catalog['core'] == [dict(id='send', title='Final click is mine', type='boundary', content='Owner interpretation', applicability='When deciding',
                                    boundaries=['Not a universal rule'], basis='Assistant synthesis', examples=example, status='adopted', revision=1)]
    assert [(e['id'], e['type']) for e in catalog['index']] == [('who', 'context'), ('side', 'principle'), ('habit', 'pattern')]
    assert set(catalog['index'][0]) == {'id', 'title', 'type', 'status', 'applicability', 'revision'}


def test_check_accepts_legacy_revisions_and_reports_invalid_new_fields(tmp_path):
    s = Store(tmp_path)
    legacy = typed(id='legacy', status='uncertain')
    legacy.pop('type')
    s.put(legacy, expected_revision=0, authorization=dict(AUTH, mode='migration'), migration=REPLAY)
    record_migration(s, ('legacy', 1))
    assert s.check(strict=True)['errors'] == []
    rows = [(f'raw-{n}', 1, '2026-01-01T00:00:00+00:00', json.dumps(dict(adopted_core(n), id=f'raw-{n}')), json.dumps(AUTH)) for n in range(CORE_LIMIT + 1)]
    rows.append(('bad', 1, '2026-01-01T00:00:00+00:00', json.dumps(typed(id='bad', type='rule', core=True)), json.dumps(AUTH)))
    with s.connect(write=True) as db:
        db.executemany('INSERT INTO revisions VALUES (?, ?, ?, ?, ?)', rows)
    errors = s.check()['errors']
    assert any('bad:1' in e and 'Type must be one of' in e for e in errors)
    assert any('bad:1' in e and 'Only adopted assets can be core' in e for e in errors)
    assert f'Core has {CORE_LIMIT + 1} assets; the limit is {CORE_LIMIT}' in errors
    with pytest.raises(ValueError, match='the limit is'):
        s.check(strict=True)


def test_compile_shows_core_in_full_and_lists_other_adopted_assets(tmp_path):
    s = Store(tmp_path)
    with pytest.raises(ValueError, match='No cognition store'):
        s.compile()
    missing = cli(tmp_path / 'missing', 'compile')
    assert missing.returncode == 2 and missing.stdout == '' and 'Traceback' not in missing.stderr
    s.put(typed(id='plain', title='Still a candidate', type='principle'), expected_revision=0, authorization=AUTH)
    assert s.compile().splitlines()[0] == EXPORT_BEGIN
    assert 'No adopted assets yet.' in s.compile()
    s.put(typed(id='send', title='Final click is mine', type='boundary', status='adopted', core=True,
                examples=[{'text': 'Stop before Send', 'source': 'owner-message:5'}]), expected_revision=0, authorization=AUTH)
    s.put(typed(id='who', title='Who I am', type='context', status='adopted', core=True), expected_revision=0, authorization=AUTH)
    s.put(typed(id='side', title='Take my side', type='principle', status='adopted', core=True), expected_revision=0, authorization=AUTH)
    s.put(typed(id='step', title='Bound the risk', type='method', status='adopted', applicability='Before a risky step'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='habit', title='Relief is not judgment', type='pattern', status='adopted'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='unsure', title='Maybe so', type='principle', status='uncertain'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='kept', title='Evidence only', status='reference'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='gone', title='Retired rule', type='boundary', status='adopted'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='gone', title='Retired rule', type='boundary', status='inactive'), expected_revision=1, authorization=AUTH)
    block = s.compile()
    assert block == s.compile()
    assert block.startswith(EXPORT_BEGIN) and block.rstrip().endswith(EXPORT_END)
    # Core assets of every type in full, in catalog type order.
    headings = [line for line in block.splitlines() if line.startswith('### ')]
    assert headings == ['### Final click is mine (boundary)', '### Who I am (context)', '### Take my side (principle)']
    assert '- Limits: Not a universal rule' in block
    # Examples are evidence (often verbatim corrections), returned by catalog and read, never loaded every session.
    assert 'Stop before Send' not in block and '- Example:' not in block
    # Every other adopted asset says when to read it; unadopted statuses stay out of the block.
    others = block.split('## Other entries')[1]
    assert '- Bound the risk (method, id `step`): Before a risky step' in others
    assert '- Relief is not judgment (pattern, id `habit`): When deciding' in others
    assert 'Owner interpretation' not in others
    for absent in ('Still a candidate', 'Maybe so', 'Evidence only', 'Retired rule'):
        assert absent not in block
    for metadata in ('Assistant synthesis', 'owner-message:1', 'owner-message:5', 'r1', 'revision', 'recorded_at'):
        assert metadata not in block
    assert 'never a rule to follow' in block and 'never grant permission for an external action' in block
    assert "read that entry's full text with the MyOS tools" in block
    result = cli(tmp_path, 'compile')
    assert result.returncode == 0 and result.stdout == block


def test_view_writes_an_escaped_private_map_and_nothing_else(tmp_path):
    root = tmp_path / 'store'
    s = Store(root)
    s.put(typed(id='send', title='<script>alert(1)</script>', type='boundary', status='adopted', core=True), expected_revision=0, authorization=AUTH)
    s.put(typed(id='side', title='站在我这边', type='principle'), expected_revision=0, authorization=AUTH)
    s.put(typed(id='gone', title='Retired', status='inactive'), expected_revision=0, authorization=AUTH)
    before = sorted(p.name for p in root.iterdir())
    out = tmp_path / 'map.html'
    result = cli(root, 'view', '--out', str(out))
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {'written': str(out.resolve())}
    html = out.read_text()
    assert '<script>alert' not in html and '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '站在我这边' in html and 'Retired' in html and 'kept for history' in html
    assert '<strong>Limits</strong>' in html and 'Not when' not in html  # boundaries are limits, not only exclusions
    assert '<script' not in html.replace('&lt;script', '') and 'http' not in html
    if os.name == 'posix':
        assert out.stat().st_mode & 0o777 == 0o600
    assert sorted(p.name for p in root.iterdir()) == before
    assert render_map(s).count('class="card"') == 3


def test_view_of_missing_store_writes_nothing(tmp_path):
    result = cli(tmp_path / 'missing', 'view', '--out', str(tmp_path / 'map.html'))
    assert result.returncode == 2 and 'No cognition store' in result.stderr
    assert not (tmp_path / 'map.html').exists() and not (tmp_path / 'missing').exists()


def test_purpose_is_traced_and_rendered_as_a_pipeline(tmp_path, monkeypatch):
    root, traces = tmp_path / 'store', tmp_path / 'traces'
    Store(root).put(typed(id='send', title='Final click is mine', type='boundary', status='adopted', core=True), expected_revision=0, authorization=AUTH)
    monkeypatch.setenv('MYOS_TRACE_DIR', str(traces))
    monkeypatch.setenv('MYOS_TRACE_GROUP', 'case-1')
    assert subprocess.run([sys.executable, '-m', 'myos', '--data', str(root), '--verbose', 'catalog', '--purpose', '回复房东的邮件'], capture_output=True).returncode == 0
    assert subprocess.run([sys.executable, '-m', 'myos', '--data', str(root), '--verbose', 'read', 'send'], capture_output=True).returncode == 0
    (root / 'cognition.sqlite3').unlink()  # Rendering reads saved traces only.
    out = tmp_path / 'pipeline.html'
    result = subprocess.run([sys.executable, '-m', 'myos', 'trace', 'show', '--dir', str(traces), '--html', '--out', str(out)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['calls'] == 2
    html = out.read_text()
    assert 'Request: 回复房东的邮件' in html
    assert 'Core loaded: Final click is mine (boundary)' in html
    assert 'Read send · Final click is mine · r1' in html
    assert 'does not prove it was applied' in html and '<details>' in html
    if os.name == 'posix':
        assert out.stat().st_mode & 0o777 == 0o600


def test_mcp_catalog_accepts_and_traces_purpose(tmp_path, monkeypatch):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    traces = tmp_path / 'traces'
    monkeypatch.setenv('MYOS_TRACE_DIR', str(traces))

    async def run():
        config = StdioServerParameters(command=sys.executable, args=['-m', 'myos.personal.mcp'],
                                       env=dict(os.environ, MYOS_DATA_DIR=str(tmp_path / 'private'), MYOS_TRACE='1'))
        async with stdio_client(config) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                return await session.call_tool('myos_catalog', {'purpose': 'Decide whether to pay'})
    result = asyncio.run(run())
    assert not result.isError
    assert json.loads(result.content[0].text) == {'core': [], 'index': []}
    call = tracing.show(traces, include_events=True)['calls'][0]
    handler_input = next(e for e in call['events'] if e['phase'] == 'handler_input')
    assert handler_input['input'] == {'purpose': 'Decide whether to pay'}
    assert not (tmp_path / 'private').exists()


def test_core_needs_a_type_even_in_migration_mode(tmp_path):
    untyped = typed(status='adopted', core=True, legacy_adoption_evidence='ratified')
    untyped.pop('type')
    with pytest.raises(ValueError, match='Core assets need a type'):
        Store(tmp_path).put(untyped, expected_revision=0, authorization=dict(AUTH, mode='migration'), migration=REPLAY)


def test_export_markers_cannot_be_forged_by_asset_text(tmp_path):
    s = Store(tmp_path)
    s.put(typed(id='send', type='boundary', status='adopted', core=True, content=f'Text {EXPORT_END} more {EXPORT_BEGIN}'),
          expected_revision=0, authorization=AUTH)
    block = s.compile()
    assert block.count('<!-- BEGIN MYOS BRIEF') == 1 and block.count(EXPORT_END) == 1


def test_check_judges_use_fields_on_the_latest_revision(tmp_path):
    s = Store(tmp_path)
    old = typed(id='legacy', type='preference', examples=['plain text'])
    rows = [('legacy', 1, '2026-01-01T00:00:00+00:00', json.dumps(old), json.dumps(AUTH))]
    with s.connect(write=True) as db:
        db.executemany('INSERT INTO revisions VALUES (?, ?, ?, ?, ?)', rows)
    assert any('Type must be one of' in e for e in s.check()['errors'])
    assert 'unclassified' in render_map(s)  # an unknown type is shown, not dropped
    s.put(typed(id='legacy', type='principle'), expected_revision=1, authorization=AUTH)
    assert s.check(strict=True)['errors'] == []


def test_page_output_never_overwrites_store_files_or_follows_symlinks(tmp_path):
    root = tmp_path / 'store'
    Store(root).put(typed(id='send', type='boundary'), expected_revision=0, authorization=AUTH)
    database = (root / 'cognition.sqlite3').read_bytes()
    for target in (root / 'cognition.sqlite3', root / 'other.html'):
        result = cli(root, 'view', '--out', str(target))
        assert result.returncode == 2 and 'outside' in result.stderr
    victim = tmp_path / 'victim.txt'
    victim.write_text('keep me')
    (root / 'myos-view.html').symlink_to(victim)
    assert cli(root, 'view').returncode == 2
    assert victim.read_text() == 'keep me'
    (root / 'myos-view.html').unlink()
    assert cli(root, 'view', '--out', str(victim)).returncode == 2 and victim.read_text() == 'keep me'
    assert cli(root, 'view', '--out', str(tmp_path / 'missing-dir' / 'map.html')).returncode == 2
    assert cli(root, 'view').returncode == 0 and cli(root, 'view').returncode == 0  # replaces its own page
    assert (root / 'cognition.sqlite3').read_bytes() == database
    assert sorted(p.name for p in root.iterdir()) == ['cognition.sqlite3', 'myos-view.html']


def test_pipeline_for_a_missing_trace_directory_creates_nothing(tmp_path):
    traces = tmp_path / 'new-traces'
    result = subprocess.run([sys.executable, '-m', 'myos', 'trace', 'show', '--dir', str(traces), '--html'], capture_output=True, text=True)
    assert result.returncode == 2 and not traces.exists()
    listing = subprocess.run([sys.executable, '-m', 'myos', 'trace', 'show', '--dir', str(traces)], capture_output=True, text=True)
    assert 'trace directory does not exist' in json.loads(listing.stdout)['warnings'][0]


def test_pipeline_starts_a_request_at_each_purpose_in_one_mcp_session(tmp_path, monkeypatch):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    root, traces = tmp_path / 'store', tmp_path / 'traces'
    Store(root).put(typed(id='side', title='Take my side', type='principle'), expected_revision=0, authorization=AUTH)
    monkeypatch.setenv('MYOS_TRACE_DIR', str(traces))

    async def run():
        config = StdioServerParameters(command=sys.executable, args=['-m', 'myos.personal.mcp'],
                                       env=dict(os.environ, MYOS_DATA_DIR=str(root), MYOS_TRACE='1'))
        async with stdio_client(config) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                await session.call_tool('myos_catalog', {'purpose': 'Plan next week'})
                await session.call_tool('myos_read', {'asset_id': 'side'})
                await session.call_tool('myos_catalog', {'purpose': 'Reply to the landlord'})
                await session.call_tool('myos_read', {'asset_id': 'missing'})
    asyncio.run(run())
    html = render_pipeline(tracing.show(traces, include_events=True))
    first, second = html.index('Request: Plan next week'), html.index('Request: Reply to the landlord')
    assert first < html.index('Read side · Take my side') < second < html.index('Unknown asset: missing')
    failure = re.search(r'<br><span class="failed">(.*?)</span>', html).group(1)
    assert failure.count('Unknown asset: missing') == 1


def test_ungrouped_cli_calls_follow_the_last_purpose(tmp_path, monkeypatch):
    root, traces = tmp_path / 'store', tmp_path / 'traces'
    Store(root).put(typed(id='side', title='Take my side', type='principle'), expected_revision=0, authorization=AUTH)
    monkeypatch.setenv('MYOS_TRACE_DIR', str(traces))
    for args in (['read', 'side'], ['catalog', '--purpose', 'Decide whether to pay'], ['read', 'side']):
        assert cli(root, '--verbose', *args).returncode == 0
    html = render_pipeline(tracing.show(traces, include_events=True))
    assert html.index('Calls before any catalog') < html.index('Request: Decide whether to pay')
    assert html.count('Read side · Take my side') == 2
    assert html.rindex('Read side · Take my side') > html.index('Request: Decide whether to pay')


def test_pipeline_escapes_crafted_trace_values(tmp_path):
    calls = [{'call_id': 'c', 'run_id': 'r', 'group_id': None, 'time': 1, 'entry': 'cli', 'operation': 'read', 'status': 'success',
              'handler_outcome': 'success', 'errors': [],
              'events': [{'phase': 'handler_result', 'result': {'id': 'x', 'title': 't', 'revision': '<script>alert(1)</script>'}}]},
             {'call_id': 'd', 'run_id': 'r', 'group_id': None, 'time': 2, 'entry': 'cli', 'operation': 'read', 'status': 'success',
              'handler_outcome': 'success', 'errors': [], 'events': [{'phase': 'handler_result', 'result': []}]}]
    html = render_pipeline({'calls': calls, 'warnings': []})
    assert '<script' not in html and 'Unreadable result' in html


def call(call_id, time, operation, *, run='run-a', entry='mcp', group=None, purpose=None, result=None):
    events = [{'phase': 'handler_input', 'input': {'purpose': purpose} if purpose else {}},
              {'phase': 'handler_result', 'result': result if result is not None else {'core': [], 'index': []}}]
    return {'call_id': call_id, 'run_id': run, 'group_id': group, 'time': time, 'entry': entry, 'operation': operation,
            'status': 'success', 'handler_outcome': 'success', 'errors': [], 'events': events}


def test_concurrent_mcp_sessions_stay_separate_and_every_catalog_starts_a_request():
    def read(n, run):
        return call(f'r{n}', f'2026-01-01T00:00:0{n}', 'myos_read', run=run, result={'id': f'asset-{run}', 'title': 't', 'revision': 1})

    calls = [call('a', '2026-01-01T00:00:01', 'myos_catalog', run='codex', purpose='Codex request'),
             call('b', '2026-01-01T00:00:02', 'myos_catalog', run='claude', purpose='Claude request'),
             read(3, 'codex'), read(4, 'claude'),
             call('c', '2026-01-01T00:00:05', 'myos_catalog', run='codex'), read(6, 'codex')]
    html = render_pipeline({'calls': calls, 'warnings': []})
    codex, claude = html.index('MCP session codex'), html.index('MCP session claude')
    assert codex < html.index('Read asset-codex') < claude < html.index('Read asset-claude')
    assert html.index('Request: Codex request') < html.index('Request without a recorded purpose') < claude
    assert html.rindex('Read asset-codex') > html.index('Request without a recorded purpose')


def test_damaged_or_older_traces_render_without_crashing():
    calls = [call('a', 1, 'catalog', entry='cli', result=[{'id': 'x'}, {'id': 'y'}]),
             dict(call('b', '2', 123, entry='cli'), events=[{'phase': 'handler_input', 'input': 'not a dict'}]),
             dict(call('c', 3, 'catalog', entry='cli'), status='incomplete/unknown')]
    html = render_pipeline({'calls': calls, 'warnings': []})
    assert 'Catalog in the older list format: 2 entries' in html
    assert 'badge pending' in html


@pytest.mark.parametrize('kind', ['directory', 'fifo', 'quoted-marker', 'other-page-kind'])
def test_page_output_refuses_non_pages_and_other_page_kinds(tmp_path, kind):
    root = tmp_path / 'store'
    Store(root).put(typed(id='send', type='boundary'), expected_revision=0, authorization=AUTH)
    target = tmp_path / 'out.html'
    if kind == 'directory':
        target.mkdir()
    elif kind == 'fifo':
        if not hasattr(os, 'mkfifo'):
            pytest.skip('no FIFOs on this platform')
        os.mkfifo(target)
    elif kind == 'quoted-marker':
        target.write_text('notes\n<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="generator" content="myos-map">\n')
    else:
        traces = tmp_path / 'traces'
        traces.mkdir(mode=0o700)
        assert subprocess.run([sys.executable, '-m', 'myos', 'trace', 'show', '--dir', str(traces), '--html', '--out', str(target)], capture_output=True).returncode == 0
    before = target.read_bytes() if target.is_file() else None
    result = subprocess.run([sys.executable, '-m', 'myos', '--data', str(root), 'view', '--out', str(target)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 2 and 'Traceback' not in result.stderr
    if before is not None:
        assert target.read_bytes() == before


def test_other_spellings_of_the_store_directory_are_refused(tmp_path):
    root = tmp_path / 'store'
    Store(root).put(typed(id='send', type='boundary'), expected_revision=0, authorization=AUTH)
    other = tmp_path / 'STORE'
    if not other.exists():
        pytest.skip('case-sensitive file system')
    result = cli(root, 'view', '--out', str(other / 'inside.html'))
    assert result.returncode == 2 and 'outside' in result.stderr
    assert sorted(p.name for p in root.iterdir()) == ['cognition.sqlite3']
