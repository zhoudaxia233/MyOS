"""Opt-in local snapshots. No database access, host context or model calls."""
from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
import hashlib
import inspect
from importlib.metadata import version, PackageNotFoundError
import json
import os
from pathlib import Path
import subprocess
import stat
import sys
import time
from uuid import uuid4

FORMAT_VERSION = 1
_PROCESS_NONCE = uuid4().hex
_current = ContextVar('myos_trace', default=None)
LIMITS = {
    'network_raw_response': 'not_collected',
    'mcp_final_protocol_response': 'not_collected',
    'cli_argument_parser_rejections': 'not_collected',
    'mcp_transport_and_lowlevel_protocol_events': 'not_collected',
    'direct_store_calls_migration_and_check': 'not_collected',
    'host_final_model_request': 'not_collected',
    'skill_loading_and_influence': 'not_observable',
    'authorization': 'caller assertion; actual consent is not verified by tracing',
}


def trace_dir():
    return Path(os.environ.get('MYOS_TRACE_DIR', Path.home() / '.local/state/myos/traces')).expanduser()


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _snapshot(value):
    # Pydantic objects only occur at the explicitly labelled SDK conversion layer.
    if hasattr(value, 'model_dump'):
        return value.model_dump(mode='json', by_alias=True)
    if isinstance(value, (tuple, list)):
        return [_snapshot(v) for v in value]
    if isinstance(value, dict):
        return {k: _snapshot(v) for k, v in value.items()}
    return value


def code_version():
    root = Path(__file__).resolve().parents[3]
    result = {'git_commit': None, 'git_dirty': None, 'source_sha256': {},
              'source_boundary': 'files on disk at call start; not proof of loaded bytecode identity',
              'python': sys.version, 'packages': {}}
    for package in ('personal-core-os', 'mcp'):
        try:
            result['packages'][package] = version(package)
        except PackageNotFoundError:
            result['packages'][package] = None
    for name in ('tracing.py', 'cli.py', 'mcp.py', 'store.py'):
        try:
            result['source_sha256'][name] = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        except OSError:
            result['source_sha256'][name] = None
    # Only this checkout, never git discovery in an unrelated installed cwd.
    if (root / '.git').exists():
        for key, args in [('git_commit', ['rev-parse', 'HEAD']), ('git_dirty', ['status', '--porcelain', '--untracked-files=normal'])]:
            try:
                p = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=2)
                if p.returncode == 0:
                    result[key] = bool(p.stdout.strip()) if key == 'git_dirty' else p.stdout.strip()
            except (OSError, subprocess.TimeoutExpired):
                pass
    return result


def category(operation, parameters):
    operation = operation.removeprefix('myos_')
    if operation == 'catalog':
        return 'catalog'
    if operation == 'read':
        return 'revision_history' if parameters.get('history') else 'full_record'
    if operation == 'references':
        path = parameters.get('path')
        return 'source_list' if path is None else 'source_line' if isinstance(path, str) and '#L' in path else 'source_full_text'
    return 'write_attempt' if operation == 'put' else operation


class Trace:
    def __init__(self, enabled, entry, operation, parameters):
        self.fd = None
        self.finished = False
        self.started = time.monotonic()
        self.base = dict(format_version=FORMAT_VERSION, run_id=f'{os.getpid()}-{_PROCESS_NONCE}',
                         call_id=uuid4().hex, pid=os.getpid(), entry=entry, operation=operation)
        if not enabled:
            return
        try:
            directory = trace_dir()
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            if directory.is_symlink():
                raise OSError('Trace directory must not be a symlink')
            if os.name == 'posix' and stat.S_IMODE(directory.stat().st_mode) != 0o700:
                raise OSError('Use a dedicated private trace directory with mode 0700')
            self.path = directory / f"{self.base['run_id']}-{self.base['call_id']}.pending.jsonl"
            self.fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            self.emit('started', input=parameters, group_id=os.environ.get('MYOS_TRACE_GROUP'),
                      category=category(operation, parameters), code_version=code_version(), limits=LIMITS,
                      capture_boundary='CLI parsed invocation' if entry == 'cli' else 'FastMCP.call_tool arguments')
        except Exception as exc:
            self._failed(exc)

    def _failed(self, exc):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None
        # Do not turn a completed business write into a failure or retry it.
        try:
            print(f'MyOS trace INCOMPLETE ({self.base["call_id"]}): {type(exc).__name__}: {exc}; business operation is not retried or reversed.', file=sys.stderr)
        except (OSError, ValueError):
            # A closed stderr must not turn a trace failure into a failed put.
            pass

    def emit(self, phase, **data):
        if self.fd is None:
            return
        try:
            snapshot = _snapshot(data)
            record = dict(self.base, phase=phase, time=datetime.now(timezone.utc).isoformat(),
                          elapsed_ms=(time.monotonic() - self.started) * 1000, **snapshot,
                          snapshot_utf8_bytes=len(_json(snapshot).encode('utf-8')))
            raw = (_json(record) + '\n').encode('utf-8')
            while raw:
                count = os.write(self.fd, raw)
                if count <= 0:
                    raise OSError('Trace write made no progress')
                raw = raw[count:]
            os.fsync(self.fd)
            if phase == 'completed':
                self.finished = True
        except Exception as exc:
            self._failed(exc)

    def invoke(self, function, parameters):
        self.emit('handler_input', input=parameters, category=category(self.base['operation'], parameters))
        try:
            result = function(**parameters)
        except BaseException as exc:
            self.emit('handler_error', status='failed', error_type=type(exc).__name__, error=str(exc))
            raise
        self.emit('handler_result', status='success', result=result,
                  write_outcome='committed_revision_returned' if self.base['operation'].removeprefix('myos_') == 'put' else 'not_a_write')
        return result

    def close(self):
        if self.fd is not None:
            try:
                os.close(self.fd)
                self.fd = None
                # Publish completion only after the final event was flushed and
                # the file closed. A flush/close failure leaves a pending file,
                # even if its completed event happens to be readable.
                if self.finished:
                    self.path = self.path.rename(self.path.with_name(self.path.name.removesuffix('.pending.jsonl') + '.jsonl'))
            except OSError as exc:
                self._failed(exc)
            finally:
                self.fd = None


def traced_handler(function):
    """Preserve FastMCP's original signature/schema; capture validated arguments."""
    signature = inspect.signature(function)

    @wraps(function)
    def wrapped(*args, **kwargs):
        trace = _current.get()
        if trace is None:
            return function(*args, **kwargs)
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return trace.invoke(function, bound.arguments)
    return wrapped


def show(directory, *, file=None, run=None, call=None, group=None, include_events=False):
    """Render saved evidence only; tolerate partial final lines after interruption."""
    paths = [file] if file else sorted(directory.glob('*.jsonl'))
    calls = []
    warnings = [] if file or directory.is_dir() else [f'{directory}: trace directory does not exist']
    for path in paths:
        events = []
        damaged = False
        try:
            lines = path.read_bytes().split(b'\n')
        except OSError as exc:
            if file:
                raise
            warnings.append(f'{path}: could not read ({exc}); timeline may be incomplete')
            continue
        if lines[-1] == b'':
            lines.pop()
        for n, line in enumerate(lines, 1):
            try:
                event = json.loads(line)
                if not isinstance(event, dict) or event.get('format_version') != FORMAT_VERSION or not {'call_id', 'run_id', 'phase', 'time', 'operation'} <= event.keys():
                    raise ValueError('Unsupported or invalid trace event')
                if events and any(event[key] != events[0][key] for key in ('call_id', 'run_id')):
                    raise ValueError('Mixed call identities')
                if event['phase'] in ('completed', 'handler_result', 'handler_error') and event.get('status') not in ('success', 'failed'):
                    raise ValueError('Missing or invalid status')
                events.append(event)
            except (ValueError, TypeError):
                damaged = True
                warnings.append(f'{path}:{n}: unreadable/unsupported event; trace incomplete')
        if not events:
            warnings.append(f'{path}: no readable events; incomplete/unknown')
            continue
        first = events[0]
        if (run and first['run_id'] != run or call and first['call_id'] != call
                or group and first.get('group_id') != group):
            continue
        completed = next((e for e in reversed(events) if e['phase'] == 'completed'), None)
        finalized = not path.name.endswith('.pending.jsonl') and not damaged and completed is not None
        result = dict(file=str(path), run_id=first['run_id'], call_id=first['call_id'],
                      group_id=first.get('group_id'), time=first['time'], entry=first.get('entry'), operation=first['operation'],
                      elapsed_ms=events[-1].get('elapsed_ms'),
                      duration_boundary='start to last saved event; not host or transport latency',
                      store_root=next((e['root'] for e in events if e['phase'] == 'store_selected'), None),
                      completion_boundary=completed.get('completion_boundary', 'see error events') if completed else 'not_observed',
                      write_outcome=next((e['write_outcome'] for e in reversed(events) if 'write_outcome' in e), 'not_observed'),
                      category=next((e['category'] for e in reversed(events) if 'category' in e), 'unknown'),
                      status=completed['status'] if finalized else 'incomplete/unknown',
                      capture_status='finalized' if finalized else 'incomplete/unknown',
                      errors=[e for e in events if 'error' in e],
                      handler_outcome=next((e['status'] for e in reversed(events) if e['phase'] in ('handler_result', 'handler_error')), 'not_observed'))
        if call or include_events:
            result['events'] = events
        calls.append(result)
    return dict(limits=LIMITS, size_measure='snapshot_utf8_bytes counts compact ensure_ascii=False JSON bytes of event data, excluding envelope; not tokens',
                warnings=warnings, calls=sorted(calls, key=lambda c: (str(c['time']), str(c['call_id']))))
