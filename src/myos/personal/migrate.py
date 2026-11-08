"""Lossless, conservative one-time import. Originals are never modified."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unicodedata
from datetime import datetime, timezone

from .store import REPLAY, Store


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    root = root.resolve()
    paths = set()
    for pattern in ('modules/*/logs/*.jsonl', 'modules/*/data/**/*', 'var/logs/*.jsonl', 'orchestrator/logs/output_artifacts.jsonl', 'core/PERSONA.md'):
        paths.update(p for p in root.glob(pattern) if p.is_file())
    # Transport traces are not cognition; keep their original location only.
    return [p for p in sorted(paths) if p.name not in {'mcp_invocations.jsonl', 'cognitive_traces.jsonl'}]


def migrate(roots, destination):
    roots = [Path(r).resolve() for r in roots]
    destination = Path(destination).resolve()
    sources = [(i, p, p.relative_to(root)) for i, root in enumerate(roots) for p in inventory(root)]
    manifest = {f'{i}/{rel}': {'original': str(p), 'sha256': digest(p)} for i, p, rel in sources}
    if not sources:
        raise ValueError('No legacy sources found')
    if destination.exists():
        saved = destination / 'migration.json'
        if not saved.exists() or json.loads(saved.read_text())['sources'] != manifest:
            raise ValueError('Destination exists with a different migration; choose a new destination')
        for name, item in manifest.items():
            if digest(destination / 'originals' / name) != item['sha256']:
                raise ValueError(f'Archived source changed: {name}')
        Store(destination).check(strict=True)
        reference_paths = {entry['path'] for entry in json.loads((destination / 'references.json').read_text())}
        if reference_paths != {str(Path('originals') / name) for name in manifest}:
            raise ValueError('Incomplete source reference index')
        return {'destination': str(destination), 'unchanged': True, 'sources': len(sources)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.myos-migrate-', dir=destination.parent))
    try:
        store = Store(staging)
        # A source-only archive is a valid store with zero cognition revisions.
        store.connect(write=True).close()
        records = []
        for i, p, rel in sources:
            target = staging / 'originals' / str(i) / rel
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(p, target)
            target.chmod(0o600)
            if digest(target) != manifest[f'{i}/{rel}']['sha256']:
                raise ValueError('Source changed during migration')
            if p.suffix == '.jsonl':
                for line, text in enumerate(target.read_text().splitlines(), 1):
                    if not text.strip():
                        continue
                    row = json.loads(text)
                    if not isinstance(row, dict):
                        raise ValueError(f'Invalid record: {p}:{line}')
                    if '_schema' not in row:
                        records.append((i, rel, line, row))
        def recorded(item):
            value = item[3].get('created_at')
            try:
                parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
            except (ValueError, TypeError, AttributeError):
                return datetime.min.replace(tzinfo=timezone.utc)
        records.sort(key=lambda item: (recorded(item), str(roots[item[0]] / item[1]), item[2]))
        ratifications = {r.get('id'): r for _, _, _, r in records if r.get('object_type') == 'ratification'}
        count = 0
        imported = []
        seen = set()
        for i, rel, line, row in records:
            # Events and state remain accessible; transport / governance records
            # are archived evidence, not automatically personal mental models.
            if not str(rel).startswith('modules/') or rel.name in {'constitution_amendment_requests.jsonl', 'constitution_amendment_request_resolutions.jsonl', 'decision_gate_checks.jsonl', 'precommit_checks.jsonl'}:
                continue
            original = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if original in seen:
                continue
            seen.add(original)
            key = row.get('principle_id') or row.get('subject_id') or row.get('schema_id') or row.get('id')
            family = {'profile_event': 'profile', 'owner_principle_event': 'principle', 'schema_version': 'model'}.get(row.get('object_type'), str(rel))
            # Ids are printed in code spans and typed back to `read`: whitespace becomes '-', backticks and invisible
            # characters go. Ordinary legacy ids pass through unchanged.
            key = ''.join("'" if c == '`' else c for c in '-'.join(f'legacy:{family}:{key or line}'.split())
                          if unicodedata.category(c) not in ('Cc', 'Cf'))
            try:
                prior = store.read(key)
            except (ValueError, __import__('sqlite3').OperationalError):
                prior = None
            rat = ratifications.get(row.get('ratification_id'))
            if not rat and row.get('materialization_attempt_id'):
                rat = next((r for r in ratifications.values() if r.get('proposal_id') == row.get('proposal_id') and row['materialization_attempt_id'] in r.get('source_refs', [])), None)
            # Some schema records carry ratification only through source_refs.
            if not rat:
                rat = next((ratifications[r] for r in row.get('source_refs', []) if r in ratifications), None)
            proposal = row.get('proposal_id') or (rat.get('proposal_id') if rat and rat.get('proposal_id') in row.get('source_refs', []) else None)
            kind = row.get('object_type')
            target = (f"owner_principle:{row.get('principle_id')}" if kind == 'owner_principle_event' else
                      f"profile:{row.get('subject_id')}:{proposal}" if kind == 'profile_event' else
                      f"cognition:{row.get('schema_id')}:{proposal}" if kind == 'schema_version' else None)
            valid_rat = (rat and rat.get('judgment') == 'ratify' and proposal and rat.get('proposal_id') == proposal
                         and f'materialized:{target}' in rat.get('applied_effects', []))
            state = row.get('status', row.get('record_status', 'uncertain'))
            inactive = state in {'archived', 'superseded', 'inactive', 'retired', 'rejected'} or row.get('change_type') in {'merged_source', 'retire', 'retired', 'supersede', 'superseded'}
            adopted = bool(valid_rat and row.get('object_type') in {'owner_principle_event', 'profile_event', 'schema_version'})
            title = row.get('title') or row.get('schema_name') or row.get('subject_id') or row.get('topic') or row.get('domain') or row.get('id') or str(rel)
            content = row.get('statement') or row.get('summary') or row.get('content') or row.get('insight') or row.get('event') or row.get('observation') or row.get('decision') or row.get('change_summary') or original
            if not isinstance(content, str):
                content = json.dumps(content, ensure_ascii=False)
            # Single-line fields stay single lines (the store refuses breaks there); the legacy record keeps the original.
            flat = lambda value: ' '.join(part for part in str(value).splitlines() if part)
            asset = dict(id=key, title=flat(title), content=content,
                applicability=flat(row.get('topic') or row.get('domain') or row.get('subject_id') or 'Legacy record; applicability requires source inspection'),
                boundaries=[flat(b) if isinstance(b, str) else b for b in row['boundaries']] if isinstance(row.get('boundaries'), list) else [],
                status='inactive' if inactive else 'adopted' if adopted else 'candidate' if 'candidate' in str(rel) else 'uncertain',
                basis='Historical ratification record; personal statement, not independently verified fact' if adopted else 'Legacy record; endorsement and factual truth not inferred',
                sources=[{'ref': str(Path('originals') / str(i) / rel) + f'#L{line}', 'original': str(roots[i] / rel), 'timestamp': row.get('created_at'), 'sha256': manifest[f'{i}/{rel}']['sha256']}],
                legacy_record=row)
            undated = recorded((i, rel, line, row)) == datetime.min.replace(tzinfo=timezone.utc)
            chronology_unknown = undated or (prior and prior.get('chronology_unknown', False))
            retirement_chronology_unknown = (inactive and undated) or (prior and prior.get('retirement_chronology_unknown', False))
            if retirement_chronology_unknown:
                asset['retirement_chronology_unknown'] = True
            if chronology_unknown:
                asset['chronology_unknown'] = True
                # An undated snapshot leaves history incomplete, but only an
                # undated retirement prevents establishing its place in time.
                if inactive or retirement_chronology_unknown:
                    asset['status'] = 'inactive'
                else:
                    asset['status'] = 'adopted' if adopted and not undated else 'uncertain'
                if asset['status'] == 'adopted':
                    asset['basis'] += '; earlier chronology remains incomplete'
                else:
                    asset['basis'] = 'Legacy chronology unknown; inspect original evidence before treating this as current'
            # Equal timestamps do not prove later reactivation, even with fully
            # dated history in one file. Incidental storage order is not evidence.
            if prior and prior['status'] == 'inactive' and recorded((i, rel, line, row)) <= recorded((i, rel, line, prior['legacy_record'])):
                asset['status'] = 'inactive'
                asset['basis'] = 'Legacy materialization not proven later than inactive revision; inspect history before use'
            if prior and recorded((i, rel, line, prior.get('legacy_record', {}))) == recorded((i, rel, line, row)) and prior.get('legacy_record') != row and prior['sources'][0].get('original') != str(roots[i] / rel):
                asset['status'] = 'inactive' if inactive or prior['status'] == 'inactive' else 'uncertain'
                asset['basis'] = 'Conflicting legacy versions at the same timestamp; inspect revisions before use'
            if adopted:
                asset['legacy_adoption_evidence'] = rat
            written = store.put(asset, expected_revision=prior['revision'] if prior else 0,
                      authorization={'request': 'Lossless migration under architectural refactor authorization; no new adoption', 'source': 'migration.json', 'mode': 'migration'},
                      migration=REPLAY)
            imported.append({'id': asset['id'], 'revision': written['revision'], 'sha256': hashlib.sha256(json.dumps(asset, ensure_ascii=False, sort_keys=True).encode()).hexdigest()})
            count += 1
        # Non-ledger material is a source reference; projections are not imported twice.
        references = []
        for i, p, rel in sources:
            references.append({'path': str(Path('originals') / str(i) / rel), 'original': str(p), 'sha256': manifest[f'{i}/{rel}']['sha256'], 'role': 'legacy source or projection; not adoption evidence'})
        (staging / 'references.json').write_text(json.dumps(references, ensure_ascii=False, indent=2))
        (staging / 'migration.json').write_text(json.dumps({'format_version': 1, 'imported_revisions': imported, 'sources': manifest, 'revisions': count, 'roots': [str(r) for r in roots]}, ensure_ascii=False, indent=2))
        for p in staging.rglob('*'):
            p.chmod(0o700 if p.is_dir() else 0o600)
        store.check(strict=True)
        # Refuse replacement, including a concurrent migration.
        if destination.exists():
            raise ValueError('Destination appeared during migration')
        os.rename(staging, destination)
        return {'destination': str(destination), 'sources': len(sources), 'revisions': count, 'unchanged': False}
    finally:
        if staging.exists():
            shutil.rmtree(staging)
