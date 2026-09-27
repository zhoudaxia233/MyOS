"""Execution evidence uses isolated stores and real CLI/MCP boundaries."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from myos.personal.cli import main
from myos.personal.store import Store
from myos.personal import tracing
from tests.test_personal_store import asset, AUTH

EMPTY_CATALOG = json.dumps({'core': [], 'index': []}, indent=2) + '\n'


@pytest.fixture
def traced(tmp_path, monkeypatch):
    directory = tmp_path / 'traces'
    monkeypatch.setenv('MYOS_TRACE_DIR', str(directory))
    monkeypatch.setenv('MYOS_TRACE_GROUP', '案例一')
    return directory


def events(directory):
    return [json.loads(line) for path in sorted(directory.glob('*.jsonl')) for line in path.read_text().split('\n') if line]


def cli(root, *args, verbose=False):
    return subprocess.run([sys.executable, '-m', 'myos', '--data', str(root), *(['--verbose'] if verbose else []), *args], capture_output=True, text=True)


def test_disabled_and_empty_install_stdout_and_permissions(tmp_path, traced, monkeypatch):
    root = tmp_path / 'empty'
    monkeypatch.setenv('MYOS_TRACE', '1')  # MCP setting must not enable CLI tracing.
    off = cli(root, 'catalog')
    assert off.returncode == 0 and not traced.exists()
    on = cli(root, 'catalog', verbose=True)
    assert on.stdout == off.stdout == EMPTY_CATALOG
    assert on.returncode == 0 and on.stderr == ''
    assert not root.exists()
    rows = events(traced)
    assert next(e['result'] for e in rows if e['phase'] == 'handler_result') == {'core': [], 'index': []}
    assert next(e['text'] for e in rows if e['phase'] == 'cli_stdout') == on.stdout
    assert rows[0]['group_id'] == '案例一'
    if os.name == 'posix':
        assert traced.stat().st_mode & 0o777 == 0o700
        assert next(traced.iterdir()).stat().st_mode & 0o777 == 0o600


def test_complete_snapshots_categories_and_frozen_view(tmp_path, traced):
    root = tmp_path / 'store'
    a = asset()
    a['content'] = '中文第一行\n第二行\nUnicode分隔符：\u2028\u0085' * 8000
    a['sources'] = [{'ref': 'originals/source.txt#L2'}, {'ref': '消息:1'}]
    payload = dict(asset=a, expected_revision=0, authorization=AUTH)
    file = tmp_path / 'payload.json'
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    file.write_text(text)
    result = cli(root, 'put', str(file), verbose=True)
    assert result.returncode == 0
    written = json.loads(result.stdout)
    archive = root / 'originals'
    archive.mkdir()
    source = archive / 'source.txt'
    source.write_text('来源一\n来源二\n')
    (root / 'references.json').write_text(json.dumps([{'path': 'originals/source.txt'}]))
    Store(root).put(a, expected_revision=1, authorization=AUTH)
    saved_history = Store(root).read('model', history=True)
    commands = [('catalog',), ('read', 'model'), ('read', 'model', '--history'), ('references',), ('references', 'originals/source.txt'), ('references', 'originals/source.txt#L2')]
    for command in commands:
        off = cli(root, *command)
        on = cli(root, *command, verbose=True)
        assert (on.returncode, on.stdout, on.stderr) == (off.returncode, off.stdout, off.stderr)
        latest = tracing.show(traced)['calls'][-1]
        saved = tracing.show(traced, call=latest['call_id'])['calls'][0]['events']
        assert next(e['result'] for e in saved if e['phase'] == 'handler_result') == json.loads(on.stdout)
        assert next(e['text'] for e in saved if e['phase'] == 'cli_stdout') == on.stdout
    rows = events(traced)
    assert next(e['text'] for e in rows if e['phase'] == 'payload_file') == text
    assert next(e['input'] for e in rows if e['phase'] == 'handler_input' and e['operation'] == 'put') == payload
    assert next(e['result'] for e in rows if e['phase'] == 'handler_result' and e['operation'] == 'put') == written
    categories = {e['category'] for e in rows if e['phase'] == 'handler_input'}
    assert categories == {'write_attempt', 'catalog', 'full_record', 'revision_history', 'source_list', 'source_full_text', 'source_line'}
    results = [e for e in rows if e['phase'] == 'handler_result']
    assert next(e['result'] for e in results if e['operation'] == 'catalog')['index'][0]['applicability'] == a['applicability']
    assert all(e['result']['content'] == a['content'] for e in results if e['operation'] == 'read' and isinstance(e['result'], dict))
    assert next(e['result'] for e in results if e['operation'] == 'read' and isinstance(e['result'], list)) == saved_history
    before = tracing.show(traced)
    details = {c['call_id']: tracing.show(traced, call=c['call_id']) for c in before['calls']}
    a['content'] = '新的正文'
    Store(root).put(a, expected_revision=2, authorization=AUTH)
    source.write_text('changed')
    for call_id, saved in details.items():
        assert tracing.show(traced, call=call_id) == saved
        process = cli(root, 'trace', 'show', '--call', call_id)
        assert json.loads(process.stdout) == saved
    for event in rows:
        envelope = {'format_version', 'run_id', 'call_id', 'pid', 'entry', 'operation', 'phase', 'time', 'elapsed_ms', 'snapshot_utf8_bytes'}
        data = {k: v for k, v in event.items() if k not in envelope}
        assert event['snapshot_utf8_bytes'] == len(tracing._json(data).encode('utf-8'))


@pytest.mark.parametrize('command,expected', [
    (('put', 'PAYLOAD'), 'Revision conflict'),
    (('read', 'missing'), 'Unknown asset'),
    (('references', '../secret'), 'within this store'),
    (('references', 'originals/source#L0'), 'positive integer'),
])
def test_business_errors_preserved(tmp_path, traced, command, expected):
    root = tmp_path / 'store'
    Store(root).put(asset(), expected_revision=0, authorization=AUTH)
    payload = tmp_path / 'payload.json'
    payload.write_text(json.dumps(dict(asset=asset(), expected_revision=0, authorization=AUTH)))
    command = [str(payload) if part == 'PAYLOAD' else part for part in command]
    off, on = cli(root, *command), cli(root, *command, verbose=True)
    assert (on.returncode, on.stdout, on.stderr) == (off.returncode, off.stdout, off.stderr)
    assert on.returncode == 2 and expected in on.stderr
    rows = events(traced)
    assert rows[-1]['status'] == 'failed'
    assert expected in rows[-1]['error']
    assert not any(e['phase'] == 'handler_result' for e in rows)
    assert Store(root).read('model')['revision'] == 1


def test_malformed_payload_saved_before_decode(tmp_path, traced):
    payload = tmp_path / 'bad.json'
    payload.write_text('{中文\n')
    result = cli(tmp_path / 'store', 'put', str(payload), verbose=True)
    assert result.returncode == 2
    rows = events(traced)
    assert next(e['text'] for e in rows if e['phase'] == 'payload_file') == '{中文\n'
    assert rows[-1]['error_type'] == 'JSONDecodeError'
    assert rows[-1]['failure_stage'] == 'payload_json_decode'


@pytest.mark.parametrize('closed_stderr', [False, True])
def test_log_failure_after_commit_never_changes_result(tmp_path, traced, monkeypatch, capsys, closed_stderr):
    payload = tmp_path / 'payload.json'
    payload.write_text(json.dumps(dict(asset=asset(), expected_revision=0, authorization=AUTH)))
    original_write = tracing.os.write
    def fail_result(fd, data):
        if b'"phase":"handler_result"' in data:
            raise OSError('disk full')
        return original_write(fd, data)
    monkeypatch.setattr(tracing.os, 'write', fail_result)
    with monkeypatch.context() as diagnostics:
        if closed_stderr:
            stream = io.StringIO()
            stream.close()
            diagnostics.setattr(sys, 'stderr', stream)
        assert main(['--data', str(tmp_path / 'store'), '--verbose', 'put', str(payload)]) == 0
    output = capsys.readouterr()
    assert json.loads(output.out)['revision'] == 1
    if not closed_stderr:
        assert 'INCOMPLETE' in output.err and 'disk full' in output.err
    assert Store(tmp_path / 'store').read('model', history=True)[0]['revision'] == 1
    assert tracing.show(traced)['calls'][0]['status'] == 'incomplete/unknown'


def test_log_open_failure_is_visible_but_business_continues(tmp_path, traced):
    traced.write_text('not a directory')
    result = cli(tmp_path / 'empty', 'catalog', verbose=True)
    assert result.returncode == 0 and result.stdout == EMPTY_CATALOG
    assert 'INCOMPLETE' in result.stderr


@pytest.mark.parametrize('failure', ['flush', 'publish'])
def test_completion_log_failure_is_not_displayed_as_complete(tmp_path, traced, monkeypatch, capsys, failure):
    payload = tmp_path / 'payload.json'
    payload.write_text(json.dumps(dict(asset=asset(), expected_revision=0, authorization=AUTH)))
    original_write, original_fsync = tracing.os.write, tracing.os.fsync
    phase = None
    def track_write(fd, data):
        nonlocal phase
        phase = json.loads(data)['phase']
        return original_write(fd, data)
    def flush(fd):
        if phase == 'completed':
            raise OSError('completion flush failed')
        original_fsync(fd)
    def publish(*args):
        raise OSError('completion publish failed')
    if failure == 'flush':
        monkeypatch.setattr(tracing.os, 'write', track_write)
        monkeypatch.setattr(tracing.os, 'fsync', flush)
    else:
        monkeypatch.setattr(Path, 'rename', publish)
    assert main(['--data', str(tmp_path / 'store'), '--verbose', 'put', str(payload)]) == 0
    output = capsys.readouterr()
    assert json.loads(output.out)['revision'] == 1 and 'INCOMPLETE' in output.err
    call = tracing.show(traced)['calls'][0]
    assert call['status'] == call['capture_status'] == 'incomplete/unknown'
    assert call['handler_outcome'] == 'success'
    assert call['write_outcome'] == 'committed_revision_returned'
    assert len(Store(tmp_path / 'store').read('model', history=True)) == 1


@pytest.mark.skipif(os.name != 'posix', reason='POSIX private directory modes')
@pytest.mark.parametrize('unsafe', ['shared', 'symlink'])
def test_unsafe_log_directory_does_not_receive_private_snapshots(tmp_path, traced, unsafe):
    if unsafe == 'shared':
        traced.mkdir(mode=0o755)
        traced.chmod(0o755)
    else:
        target = tmp_path / 'private-target'
        target.mkdir(mode=0o700)
        traced.symlink_to(target, target_is_directory=True)
    result = cli(tmp_path / 'empty', 'catalog', verbose=True)
    assert result.returncode == 0 and result.stdout == EMPTY_CATALOG
    assert 'INCOMPLETE' in result.stderr and not list(traced.iterdir())
    assert not (tmp_path / 'empty').exists()


def test_multiple_processes_unique_calls(tmp_path, traced):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda n: cli(tmp_path / 'empty', 'read', f'id-{n}', verbose=True), range(8)))
    assert all(r.returncode == 2 for r in results)
    calls = tracing.show(traced)['calls']
    assert len({c['call_id'] for c in calls}) == len({c['run_id'] for c in calls}) == 8
    assert {next(e['input']['asset_id'] for e in tracing.show(traced, call=c['call_id'])['calls'][0]['events'] if e['phase'] == 'handler_input') for c in calls} == {f'id-{n}' for n in range(8)}
    for call in calls:
        assert call['elapsed_ms'] >= 0 and call['store_root'] == str((tmp_path / 'empty').resolve())
        assert tracing.show(traced, run=call['run_id'])['calls'] == [call]
        assert tracing.show(traced, file=Path(call['file']))['calls'] == [call]
    assert tracing.show(traced, group='案例一')['calls'] == calls
    assert tracing.show(traced, group='different-case')['calls'] == []
    assert json.loads(cli(tmp_path / 'empty', 'trace', 'show', '--group', '案例一').stdout)['calls'] == calls


def test_incomplete_and_truncated_log_and_viewer_never_reads_store(tmp_path, traced, monkeypatch):
    trace = tracing.Trace(True, 'cli', 'catalog', {})
    trace.close()
    with trace.path.open('ab') as stream:
        stream.write(b'{"partial":')
    def forbidden(*args, **kwargs):
        raise AssertionError('Viewer must not read a store')
    monkeypatch.setattr(Store, '__init__', forbidden)
    viewed = tracing.show(traced, file=trace.path)
    assert viewed['calls'][0]['status'] == 'incomplete/unknown'
    assert viewed['warnings']
    assert main(['trace', 'show', '--file', str(trace.path)]) == 0


def test_mcp_real_stdio_contract_results_and_validation(tmp_path, traced):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    root = tmp_path / 'store'
    a = asset()
    a['content'] = '中文第一行\n第二行\n' * 8000
    Store(root).put(a, expected_revision=0, authorization=AUTH)
    a['boundaries'].append('第二版限制')
    Store(root).put(a, expected_revision=1, authorization=AUTH)
    (root / 'originals').mkdir()
    (root / 'originals/source.txt').write_text(a['content'])
    (root / 'references.json').write_text(json.dumps([{'path': 'originals/source.txt'}]))
    cases = [
        ('myos_catalog', {}),
        ('myos_read', {'asset_id': 'model'}),
        ('myos_read', {'asset_id': 'model', 'history': True}),
        ('myos_references', {}),
        ('myos_references', {'path': 'originals/source.txt'}),
        ('myos_references', {'path': 'originals/source.txt#L2'}),
        ('myos_read', {'asset_id': 'missing'}),
        ('myos_read', {}),
        ('myos_references', {'path': {'invalid': 'type'}}),
        ('myos_references', {'path': '../secret'}),
        ('unknown', {}),
        ('myos_put', dict(asset=a, expected_revision=0, authorization=AUTH)),
        ('myos_put', dict(asset=a, expected_revision=2, authorization=AUTH)),
    ]
    async def run(enabled):
        selected = tmp_path / str(enabled)
        shutil.copytree(root, selected)
        config = StdioServerParameters(command=sys.executable, args=['-m', 'myos.personal.mcp'], env=dict(os.environ, MYOS_DATA_DIR=str(selected), MYOS_TRACE='1' if enabled else '0'))
        async with stdio_client(config) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                listing = (await session.list_tools()).model_dump()
                results = [(await session.call_tool(name, params)).model_dump(mode='json', by_alias=True) for name, params in cases]
                return listing, results
    off = asyncio.run(run(False))
    assert not traced.exists()
    on = asyncio.run(run(True))
    assert on[0] == off[0]
    assert on[1][:-1] == off[1][:-1]
    # Successful writes have their own real timestamps; all other fields match.
    for response in (on[1][-1], off[1][-1]):
        written = json.loads(response['content'][0]['text'])
        assert not response['isError'] and written['revision'] == 3
        assert {k: v for k, v in written.items() if k != 'recorded_at'} == dict(a, revision=3, authorization=AUTH)
    calls = tracing.show(traced)['calls']
    assert len(calls) == len(cases) and len({c['run_id'] for c in calls}) == 1
    for call, (name, parameters), response in zip(calls, cases, on[1], strict=True):
        rows = tracing.show(traced, call=call['call_id'])['calls'][0]['events']
        assert rows[0]['operation'] == name and rows[0]['input'] == parameters
        if response['isError']:
            assert call['status'] == 'failed' and call['errors']
            continue
        handler = next(e['result'] for e in rows if e['phase'] == 'handler_result')
        converted = next(e['result'] for e in rows if e['phase'] == 'fastmcp_converted_result')
        if response['structuredContent'] is not None:
            assert handler == response['structuredContent'].get('result', response['structuredContent'])
            assert converted == [response['content'], response['structuredContent']]
        else:
            decoded = [json.loads(block['text']) for block in response['content']]
            assert handler == (decoded if isinstance(handler, list) else decoded[0])
            assert converted == response['content']
        assert call['store_root'] == str((tmp_path / 'True').resolve())
    invalid = next(c for c in calls if c['operation'] == 'myos_read' and c['handler_outcome'] == 'not_observed')
    assert invalid['status'] == 'failed' and invalid['errors']
    rows = events(traced)
    assert any(e['phase'] == 'fastmcp_converted_result' for e in rows)
    assert all(e['limits']['host_final_model_request'] == 'not_collected' for e in rows if e['phase'] == 'started')


def test_mcp_concurrency_and_write_failure(tmp_path, traced, monkeypatch, capsys):
    from myos.personal.mcp import mcp
    monkeypatch.setenv('MYOS_TRACE', '1')
    monkeypatch.setenv('MYOS_DATA_DIR', str(tmp_path / 'store'))
    def concurrent(n):
        return asyncio.run(mcp.call_tool('myos_put', dict(asset=dict(asset(), id=f'id-{n}'), expected_revision=0, authorization=AUTH)))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(concurrent, range(6)))
    calls = tracing.show(traced)['calls']
    assert len(calls) == 6 and len({c['run_id'] for c in calls}) == 1
    for c in calls:
        rows = tracing.show(traced, call=c['call_id'])['calls'][0]['events']
        inputs = next(e['input'] for e in rows if e['phase'] == 'handler_input')
        output = next(e['result'] for e in rows if e['phase'] == 'handler_result')
        assert output['id'] == inputs['asset']['id'] and output['revision'] == 1
    original_write = tracing.os.write
    def fail_result(fd, data):
        if b'"phase":"handler_result"' in data:
            raise OSError('disk full')
        return original_write(fd, data)
    monkeypatch.setattr(tracing.os, 'write', fail_result)
    asyncio.run(mcp.call_tool('myos_put', dict(asset=asset(), expected_revision=0, authorization=AUTH)))
    assert Store(tmp_path / 'store').read('model')['revision'] == 1
    assert 'INCOMPLETE' in capsys.readouterr().err


def test_mcp_schemas_match_unwrapped_handlers():
    from mcp.server.fastmcp import FastMCP
    from myos.personal import mcp as adapter
    async def compare():
        baseline = FastMCP('Untraced schema comparison')
        current = await adapter.mcp.list_tools()
        for tool in current:
            handler = getattr(adapter, tool.name)
            baseline.add_tool(handler.__wrapped__, annotations=tool.annotations)
        assert [t.model_dump() for t in await baseline.list_tools()] == [t.model_dump() for t in current]
    asyncio.run(compare())
