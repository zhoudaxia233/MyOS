"""Refresh the MyOS block in host instruction files; nothing outside the markers changes.

Targets come from `--target` or `MYOS_SYNC_TARGETS` (paths separated by the OS path separator). Every target is
checked before any is written, so one bad file leaves all of them untouched. Each changed file is backed up in the
data directory first, and `revert` restores the latest backup.
"""
from __future__ import annotations

import difflib
import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .store import EXPORT_END

MARKERS = (('<!-- BEGIN MYOS BRIEF', EXPORT_END), ('<!-- BEGIN MYOS CORE', '<!-- END MYOS CORE -->'))  # current, then legacy
BACKUP_DIR = 'sync-backups'
KEEP_BACKUPS = 5


def env_targets():
    return [Path(p).expanduser() for p in os.environ.get('MYOS_SYNC_TARGETS', '').split(os.pathsep) if p.strip()]


def block_span(text, path):
    """Start and end offsets of the one MyOS block, markers included."""
    found = [(text.find(begin), begin, end) for begin, end in MARKERS if begin in text]
    if len(found) != 1 or any(text.count(begin) != 1 or text.count(end) != 1 for _, begin, end in found):
        raise ValueError(f'{path}: expected exactly one MyOS block between BEGIN and END markers')
    start, _, end = found[0]
    stop = text.find(end)
    if stop < start:
        raise ValueError(f'{path}: the MyOS END marker comes before BEGIN')
    return start, stop + len(end)


def target_file(path):
    path = Path(path).expanduser()
    if path.is_symlink():
        raise ValueError(f'Refusing to write through a symlink: {path}')
    if not path.is_file():
        raise ValueError(f'Target is not an existing regular file: {path}')
    return path.parent.resolve() / path.name


def backup_prefix(path):
    return f"{path.name}.{hashlib.sha256(str(path).encode()).hexdigest()[:12]}."


def plan(store, targets):
    if not targets:
        raise ValueError('No sync targets; pass --target or set MYOS_SYNC_TARGETS')
    block = store.compile().rstrip('\n')
    planned = []
    for raw in targets:
        path = target_file(raw)
        text = read_exact(path)
        start, stop = block_span(text, path)
        # Keep the file's line endings: a CRLF file gets a CRLF block and nothing outside the markers changes.
        block_lf = block.replace('\r\n', '\n')
        inserted = block_lf.replace('\n', '\r\n') if '\r\n' in text else block_lf
        planned.append((path, text, text[:start] + inserted + text[stop:]))
    return planned


def read_exact(path):
    """Text with line endings as stored; read_text would turn CRLF into LF."""
    return Path(path).read_bytes().decode('utf-8')


def list_targets(store, targets):
    rows = []
    for raw in targets:
        try:
            path, text, new = plan(store, [raw])[0]
            rows.append({'path': str(path), 'ready': True, 'up_to_date': new == text})
        except (ValueError, OSError) as exc:
            rows.append({'path': str(Path(raw).expanduser()), 'ready': False, 'problem': str(exc)})
    return {'targets': rows}


def sync(store, targets, *, dry_run=False):
    planned = plan(store, targets)  # all targets are validated before any is written
    results = []
    for path, text, new in planned:
        if new == text:
            results.append({'path': str(path), 'status': 'unchanged'})
        elif dry_run:
            diff = ''.join(difflib.unified_diff(text.splitlines(True), new.splitlines(True), str(path), f'{path} (compiled)'))
            results.append({'path': str(path), 'status': 'would update', 'diff': diff})
        else:
            backup = save_backup(store, path, text)
            replace(path, new)
            results.append({'path': str(path), 'status': 'updated', 'backup': str(backup)})
    return {'targets': results, 'dry_run': dry_run}


def save_backup(store, path, text):
    folder = store.root / BACKUP_DIR
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = folder / f'{backup_prefix(path)}{stamp}'
    fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    for old in sorted(folder.glob(f'{backup_prefix(path)}*'))[:-KEEP_BACKUPS]:
        old.unlink()
    return backup


def replace(path, text):
    mode = path.stat().st_mode & 0o777
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.myos-sync-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def revert(store, targets):
    if not targets:
        raise ValueError('No sync targets; pass --target or set MYOS_SYNC_TARGETS')
    restores = []
    for raw in targets:
        path = target_file(raw)
        backups = sorted((store.root / BACKUP_DIR).glob(f'{backup_prefix(path)}*'))
        if not backups:
            raise ValueError(f'No backup to restore for {path}')
        restores.append((path, backups[-1]))
    for path, backup in restores:
        replace(path, read_exact(backup))
    return {'targets': [{'path': str(p), 'status': 'restored', 'backup': str(b)} for p, b in restores]}


def after_put(store):
    """Refresh env-configured targets after a successful write; report problems instead of failing the write."""
    targets = env_targets()
    if not targets:
        return None
    try:
        return sync(store, targets)
    except (ValueError, OSError) as exc:
        return {'error': str(exc)}
