"""Synthetic reactivation regressions reconstructed from the PR review request.

The referenced attachment was unavailable on this host; these cases reproduce
its three described inputs without claiming to be a copy of that file.
"""
import json

import pytest

from myos.personal.migrate import migrate
from myos.personal.store import Store


KEY = 'legacy:model:example'


def migration_case(root, *, undated_snapshot=False, undated_retirement=False, ratified=True):
    snapshot = {'id': 'snapshot', 'schema_id': 'example', 'object_type': 'schema_version', 'status': 'active', 'summary': 'Historical snapshot without a date'}
    retired = dict(snapshot, id='retirement', status='inactive', change_type='retired', created_at='2026-01-01T00:00:00Z')
    if undated_retirement:
        retired.pop('created_at')
    current = dict(snapshot, id='reactivation', change_type='materialize', created_at='2026-02-01T00:00:00Z', summary='Later materialization', proposal_id='proposal-reactivate', ratification_id='rat-reactivate')
    rows = ([snapshot] if undated_snapshot else []) + [retired, current]
    p = root / 'modules/cognition/logs/schema_versions.jsonl'
    p.parent.mkdir(parents=True)
    p.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    if ratified:
        rat = {'id': 'rat-reactivate', 'object_type': 'ratification', 'judgment': 'ratify', 'proposal_id': 'proposal-reactivate', 'applied_effects': ['materialized:cognition:example:proposal-reactivate']}
        r = root / 'var/logs/ratifications.jsonl'
        r.parent.mkdir(parents=True)
        r.write_text(json.dumps(rat) + '\n')
    return rows


def test_undated_non_retirement_does_not_block_ratified_reactivation(tmp_path):
    rows = migration_case(tmp_path / 'old', undated_snapshot=True)
    migrate([tmp_path / 'old'], tmp_path / 'new')
    s = Store(tmp_path / 'new')
    current = s.read(KEY)
    assert current['status'] == 'adopted'
    assert current['chronology_unknown'] is True
    assert current['legacy_adoption_evidence']['proposal_id'] == 'proposal-reactivate'
    assert [a['id'] for a in s.catalog()['index']] == [KEY]
    assert [r['legacy_record'] for r in s.read(KEY, history=True)] == rows
    assert s.check(strict=True)['errors'] == []


def test_fully_dated_retirement_and_ratified_reactivation(tmp_path):
    rows = migration_case(tmp_path / 'old')
    migrate([tmp_path / 'old'], tmp_path / 'new')
    s = Store(tmp_path / 'new')
    assert s.read(KEY)['status'] == 'adopted'
    assert [a['id'] for a in s.catalog()['index']] == [KEY]
    assert [r['legacy_record'] for r in s.read(KEY, history=True)] == rows
    assert s.check(strict=True)['errors'] == []


def test_undated_retirement_still_blocks_dated_ratified_materialization(tmp_path):
    rows = migration_case(tmp_path / 'old', undated_retirement=True)
    migrate([tmp_path / 'old'], tmp_path / 'new')
    s = Store(tmp_path / 'new')
    assert s.read(KEY)['status'] == 'inactive'
    assert s.catalog()['index'] == []
    assert [r['legacy_record'] for r in s.read(KEY, history=True)] == rows
    assert s.check(strict=True)['errors'] == []


def test_unratified_materialization_is_not_promoted(tmp_path):
    migration_case(tmp_path / 'old', undated_snapshot=True, ratified=False)
    migrate([tmp_path / 'old'], tmp_path / 'new')
    s = Store(tmp_path / 'new')
    assert s.read(KEY)['status'] == 'uncertain'
    assert s.read(KEY)['chronology_unknown'] is True
    assert 'legacy_adoption_evidence' not in s.read(KEY)
    assert s.check(strict=True)['errors'] == []


@pytest.mark.parametrize('reverse_roots', [False, True])
def test_root_order_does_not_decide_reactivation(tmp_path, reverse_roots):
    root = tmp_path / 'old'
    rows = migration_case(root, undated_snapshot=True)
    p = root / 'modules/cognition/logs/schema_versions.jsonl'
    p.write_text(''.join(json.dumps(r) + '\n' for r in rows[1:]))
    other = tmp_path / 'snapshot-source'
    q = other / p.relative_to(root)
    q.parent.mkdir(parents=True)
    q.write_text(json.dumps(rows[0]) + '\n')
    roots = [root, other]
    if reverse_roots:
        roots.reverse()
    migrate(roots, tmp_path / 'new')
    s = Store(tmp_path / 'new')
    assert s.read(KEY)['status'] == 'adopted'
    assert s.read(KEY)['chronology_unknown'] is True
    assert len(s.read(KEY, history=True)) == 3
    assert s.check(strict=True)['errors'] == []


def test_same_timestamp_is_not_proof_of_later_reactivation(tmp_path):
    root = tmp_path / 'old'
    rows = migration_case(root, undated_snapshot=True)
    rows[-1]['created_at'] = rows[-2]['created_at']
    p = root / 'modules/cognition/logs/schema_versions.jsonl'
    p.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    migrate([root], tmp_path / 'new')
    s = Store(tmp_path / 'new')
    assert s.read(KEY)['status'] == 'inactive'
    assert s.catalog()['index'] == []
    assert [r['legacy_record'] for r in s.read(KEY, history=True)] == rows
    assert s.check(strict=True)['errors'] == []


@pytest.mark.parametrize('materialized_at,expected', [
    ('2025-12-01T00:00:00Z', 'inactive'),
    ('2026-01-01T00:00:00Z', 'inactive'),
    ('2026-02-01T00:00:00Z', 'adopted'),
])
@pytest.mark.parametrize('undated_snapshot', [False, True])
@pytest.mark.parametrize('reverse_records', [False, True])
@pytest.mark.parametrize('layout', ['same-file', 'separate-files', 'separate-roots', 'reversed-roots'])
def test_retirement_boundary_independent_of_storage_order(
    tmp_path, materialized_at, expected, undated_snapshot, reverse_records, layout,
):
    root = tmp_path / 'old'
    rows = migration_case(root, undated_snapshot=undated_snapshot)
    rows[-1]['created_at'] = materialized_at
    ordered = list(reversed(rows)) if reverse_records else rows
    p = root / 'modules/cognition/logs/schema_versions.jsonl'
    roots = [root]
    if layout == 'same-file':
        p.write_text(''.join(json.dumps(r) + '\n' for r in ordered))
    else:
        p.unlink()
        for n, row in enumerate(ordered):
            source_root = root if layout == 'separate-files' else tmp_path / f'source-{n}'
            q = source_root / f'modules/cognition/logs/versions-{n}.jsonl'
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_text(json.dumps(row) + '\n')
            if source_root not in roots:
                roots.append(source_root)
        if layout == 'reversed-roots':
            roots.reverse()
    migrate(roots, tmp_path / 'new')
    s = Store(tmp_path / 'new')
    assert s.read(KEY)['status'] == expected
    assert [a['id'] for a in s.catalog()['index']] == ([KEY] if expected == 'adopted' else [])
    history = s.read(KEY, history=True)
    assert sorted((r['legacy_record'] for r in history), key=lambda r: r['id']) == sorted(rows, key=lambda r: r['id'])
    for revision in history:
        source = s.references(revision['sources'][0]['ref'])
        assert json.loads(source['content']) == revision['legacy_record']
    assert s.check(strict=True)['errors'] == []
