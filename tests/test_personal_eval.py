"""myos eval against a fake host: answers and reviews once, resumes, never writes the store, stops at a usage limit."""
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import sqlite3
import textwrap

import pytest

from myos.personal.mcp import mcp
from myos.personal.evaluate import evaluate, load_cases, verdict
from myos.personal.store import Store
from tests.test_personal_store import AUTH, asset

FAKE_HOST = textwrap.dedent('''\
    import json, os, pathlib, sys
    args = sys.argv[1:]
    prompt = sys.stdin.read()
    log = pathlib.Path(os.environ['FAKE_LOG'])
    if os.environ.get('FAKE_LIMIT'):
        print(json.dumps({'is_error': True, 'result': "You've hit your usage limit"}))
        sys.exit(1)
    if any('Output only the requested JSON object.' in a for a in args):
        log.open('a').write('review ' + args[args.index('--effort') + 1] + '\\n')
        items = json.JSONDecoder().raw_decode(prompt.split('PACKET:\\n', 1)[1])[0]['items']
        reviews = [{'id': i['id'], 'full_answer_checked': True, 'no_material_claims_reason': 'None.',
                    'support': [] if 'GOOD' in i['answer'] else [{'status': 'unsupported', 'answer_quote': 'plain', 'source_quote': '', 'reason': 'Invented.'}],
                    'coverage': [{'id': n['id'], 'status': 'covered' if 'GOOD' in i['answer'] else 'missing',
                                  'answer_quote': 'GOOD' if 'GOOD' in i['answer'] else '', 'reason': 'Checked.'}
                                 for n in i['needs']]} for i in items]
        flags = [{'id': 7 if os.environ.get('FAKE_BADIDS') else i['id'], 'boundary_violation': {'value': False, 'quote': '', 'reason': 'None.'},
                  'over_application': {'value': 'false' if os.environ.get('FAKE_BADFLAGS') else 'GOOD' in i['answer'],
                                       'quote': 'GOOD' if 'GOOD' in i['answer'] else '', 'reason': 'Test.'},
                  'mechanics_leak': {'value': False, 'quote': '', 'reason': 'None.'}} for i in items]
        print(json.dumps({'result': json.dumps({'reviews': reviews, 'flags': flags}), 'num_turns': 1}))
        sys.exit(0)
    daily = '--mcp-config' in args
    block = pathlib.Path('CLAUDE.md').read_text() if daily else ''
    leaked = sorted(k for k in os.environ if k.startswith('MYOS_'))
    log.open('a').write(f"{'daily' if daily else 'bare'} {'block' if 'BEGIN MYOS' in block else '-'} {leaked} {args[args.index('--effort') + 1]}\\n")
    answer = 'GOOD answer' if daily or 'neg' in prompt else 'plain answer'
    print(json.dumps({'result': answer, 'num_turns': 2 if daily else 1, 'total_cost_usd': 0.01}))
''')

NEED = {'id': 'N1', 'description': 'Covers the point.', 'rationale': 'Asked.', 'source_quote': 'the point', 'condition': ''}


def setup(tmp_path):
    store = Store(tmp_path / 'data')
    store.put(dict(asset(), id='send', title='Final click is mine', type='boundary', status='adopted'), expected_revision=0, authorization=AUTH)
    store.put(dict(asset(), id='other', title='Untested entry', status='adopted'), expected_revision=0, authorization=AUTH)
    cases = tmp_path / 'suite' / 'cases'
    cases.mkdir(parents=True)
    (cases / 'c1.json').write_text(json.dumps({'id': 'c1', 'date': '2026-01-02', 'prompt': 'Reply for me', 'source': 'Reply about the point',
                                               'needs': [dict(NEED, assets=['send'])]}))
    (cases / 'n1.json').write_text(json.dumps({'id': 'n1', 'date': '2026-01-02', 'prompt': 'neg question', 'source': 'Answer the point',
                                               'needs': [NEED], 'negative_control': True}))
    host = tmp_path / 'claude'
    host.write_text(f'#!{sys.executable}\n' + FAKE_HOST)
    host.chmod(0o755)
    skill = tmp_path / 'skill'
    skill.mkdir()
    (skill / 'SKILL.md').write_text('---\nname: myos\n---\n')
    return store, tmp_path / 'suite', host, skill


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_eval_answers_reviews_reports_and_resumes_without_writing_the_store(tmp_path, monkeypatch):
    store, suite, host, skill = setup(tmp_path)
    log = tmp_path / 'log'
    monkeypatch.setenv('FAKE_LOG', str(log))
    monkeypatch.setenv('MYOS_SYNC_TARGETS', str(tmp_path / 'CLAUDE.md'))
    before = digest(store.path)
    result = evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    assert result['reviewed'] == '2/2' and not result['stopped'] and result['errors'] == []
    calls = log.read_text().splitlines()
    assert sorted(calls) == sorted(['bare - [] medium', 'bare - [] medium', 'daily block [] medium', 'daily block [] medium', 'review high', 'review high'])
    report = (suite / 'runs' / 'r1' / 'report.md').read_text()
    assert '| m1 | daily | 1/1 | 0 | 0 | 2 | 0 | 0 | 4 | 0.02 |' in report
    assert '| m1 | bare | 0/1 | 1 | 0 | 1 | 0 | 0 | 2 | 0.02 |' in report
    assert '| Final click is mine | still helps | 1 | 0 | 0 | 0 |' in report
    assert '| Untested entry | untested | 0 | 0 | 0 | 0 |' in report
    assert '| c1 #1 | m1 | daily | over_application | GOOD | Test. |' in report and report.count('over_application |') == 3
    packet = json.loads((suite / 'runs' / 'r1' / 'reviews' / 'c1__m1__1' / 'packet.json').read_text())
    assert all('assets' not in need for item in packet['items'] for need in item['needs'])
    assert {i['answer'] for i in packet['items']} == {'GOOD answer', 'plain answer'} and 'daily' not in json.dumps(packet)

    evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    assert log.read_text().splitlines() == calls
    assert digest(store.path) == before and not (tmp_path / 'CLAUDE.md').exists()


def test_usage_limit_stops_the_run_and_a_rerun_resumes(tmp_path, monkeypatch):
    store, suite, host, skill = setup(tmp_path)
    monkeypatch.setenv('FAKE_LOG', str(tmp_path / 'log'))
    monkeypatch.setenv('FAKE_LIMIT', '1')
    result = evaluate(store, suite, 'r1', models=['m1'], jobs=1, skill=skill, host=str(host))
    assert result['stopped'] and result['reviewed'] == '0/2' and 'usage limit' in result['errors'][0]
    assert len(result['errors']) == 1 and not (suite / 'runs' / 'r1' / 'answers').exists()
    assert 'Not reviewed yet (2)' in (suite / 'runs' / 'r1' / 'report.md').read_text()
    monkeypatch.delenv('FAKE_LIMIT')
    assert evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))['reviewed'] == '2/2'


def test_a_changed_case_or_effort_is_answered_and_reviewed_again(tmp_path, monkeypatch):
    store, suite, host, skill = setup(tmp_path)
    log = tmp_path / 'log'
    monkeypatch.setenv('FAKE_LOG', str(log))
    evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    calls = len(log.read_text().splitlines())
    case = json.loads((suite / 'cases' / 'c1.json').read_text())
    (suite / 'cases' / 'c1.json').write_text(json.dumps(dict(case, prompt='Reply for me, briefly')))
    monkeypatch.setenv('FAKE_LIMIT', '1')
    stopped = evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    assert stopped['reviewed'] == '1/2' and 'Not reviewed yet (1): c1 m1 #1' in (suite / 'runs' / 'r1' / 'report.md').read_text()
    monkeypatch.delenv('FAKE_LIMIT')
    assert evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))['reviewed'] == '2/2'
    assert len(log.read_text().splitlines()) == calls + 3
    evaluate(store, suite, 'r1', models=['m1'], effort='low', skill=skill, host=str(host))
    assert len(log.read_text().splitlines()) == calls + 3 + 4  # same answer text, same packet: the review stands


@pytest.mark.parametrize('bad', ['FAKE_BADFLAGS', 'FAKE_BADIDS'])
def test_flags_are_validated_before_a_review_is_kept(tmp_path, monkeypatch, bad):
    store, suite, host, skill = setup(tmp_path)
    log = tmp_path / 'log'
    monkeypatch.setenv('FAKE_LOG', str(log))
    monkeypatch.setenv(bad, '1')
    result = evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    assert result['reviewed'] == '0/2' and all('failed validation' in e for e in result['errors'])
    assert log.read_text().splitlines().count('review high') == 6  # three tries per review
    assert not list((suite / 'runs' / 'r1' / 'reviews').glob('*/review.json'))


def test_asset_filter_keeps_linked_cases_and_negative_controls(tmp_path, monkeypatch):
    store, suite, host, skill = setup(tmp_path)
    monkeypatch.setenv('FAKE_LOG', str(tmp_path / 'log'))
    assert evaluate(store, suite, 'r1', models=['m1'], assets=['other'], skill=skill, host=str(host))['cases'] == 1
    assert evaluate(store, suite, 'r2', models=['m1'], assets=['send'], skill=skill, host=str(host))['cases'] == 2


def test_verdicts():
    assert verdict(0, 0, 0, 0) == 'untested'
    assert verdict(1, 2, 0, 0) == 'hurts'
    assert verdict(2, 1, 0, 0) == 'still helps'
    assert verdict(0, 0, 3, 0) == 'model already does this'
    assert verdict(0, 0, 0, 2) == 'not followed'


def test_cli_eval_uses_the_data_directory_suite(tmp_path):
    store, suite, host, skill = setup(tmp_path)
    (store.root / 'evals').symlink_to(suite)
    env = dict(os.environ, FAKE_LOG=str(tmp_path / 'log'))
    p = subprocess.run([sys.executable, '-m', 'myos', '--data', str(store.root), 'eval', '--name', 'cli', '--model', 'm1',
                        '--skill', str(skill), '--host', str(host)], capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout)['reviewed'] == '2/2'


CASE = {'id': 'confirm-appointment', 'date': '2026-03-01', 'prompt': 'Just say yes to the practice',
        'source': "Practice asks to confirm. Owner's correction: give the final text and its meaning in one answer.",
        'needs': [{'id': 'C1', 'description': 'Gives the final text and its meaning together.',
                   'rationale': 'The owner corrected a separate approval round.',
                   'source_quote': 'give the final text and its meaning in one answer'}]}


def test_a_write_with_a_case_saves_it_linked_to_the_entry_and_eval_loads_it(tmp_path):
    store = Store(tmp_path / 'data')
    result = store.put(dict(asset(), id='send', status='adopted'), expected_revision=0, authorization=AUTH, case=CASE)
    saved = json.loads((tmp_path / 'data' / 'evals' / 'cases' / 'confirm-appointment.json').read_text())
    assert result['case'] == 'confirm-appointment' and saved['needs'][0]['assets'] == ['send']
    assert (tmp_path / 'data' / 'evals' / 'cases' / 'confirm-appointment.json').stat().st_mode & 0o777 == 0o600
    assert list(load_cases(tmp_path / 'data' / 'evals')) == ['confirm-appointment']


def test_an_invalid_or_duplicate_case_writes_nothing(tmp_path):
    store = Store(tmp_path / 'data')
    bad = dict(CASE, needs=[dict(CASE['needs'][0], source_quote='not in the source')])
    with pytest.raises(ValueError, match='copied exactly'):
        store.put(dict(asset(), id='send', status='adopted'), expected_revision=0, authorization=AUTH, case=bad)
    assert store.current() == []
    store.put(dict(asset(), id='send', status='adopted'), expected_revision=0, authorization=AUTH, case=CASE)
    with pytest.raises(ValueError, match='exists'):
        store.put(dict(asset(), id='send', status='adopted'), expected_revision=1, authorization=AUTH, case=CASE)
    assert store.read('send')['revision'] == 1


def test_a_case_commits_with_its_revision_and_an_interrupted_export_is_completed(tmp_path, monkeypatch):
    store = Store(tmp_path / 'data')
    case_file = tmp_path / 'data' / 'evals' / 'cases' / 'confirm-appointment.json'
    with pytest.raises(ValueError, match='Revision conflict'):
        store.put(dict(asset(), id='send', status='adopted'), expected_revision=4, authorization=AUTH, case=CASE)
    assert not case_file.exists() and store.export_cases()['written'] == []
    def killed(self):
        raise KeyboardInterrupt  # the process dies after commit, before the file is written
    monkeypatch.setattr(Store, 'export_cases', killed)
    with pytest.raises(KeyboardInterrupt):
        store.put(dict(asset(), id='send', status='adopted'), expected_revision=0, authorization=AUTH, case=CASE)
    monkeypatch.undo()
    assert store.read('send')['revision'] == 1 and not case_file.exists()
    assert store.export_cases()['written'] == [str(case_file)] and json.loads(case_file.read_text())['id'] == 'confirm-appointment'
    with pytest.raises(ValueError, match='exists'):
        store.put(dict(asset(), id='send', status='adopted'), expected_revision=1, authorization=AUTH, case=CASE)
    case_file.unlink()
    with pytest.raises(ValueError, match='exists'):
        store.put(dict(asset(), id='send', status='adopted'), expected_revision=1, authorization=AUTH, case=CASE)
    assert store.read('send')['revision'] == 1


def test_a_failed_export_keeps_the_write_and_says_so(tmp_path, monkeypatch):
    store = Store(tmp_path / 'data')
    def full(*args):
        raise OSError('disk full')
    monkeypatch.setattr('myos.personal.store.os.link', full)
    result = store.put(dict(asset(), id='send', status='adopted'), expected_revision=0, authorization=AUTH, case=CASE)
    assert result['revision'] == 1 and 'disk full' in result['case_export']['errors'][0]
    assert not list((tmp_path / 'data' / 'evals' / 'cases').iterdir())


def test_a_damaged_answer_or_a_changed_date_is_redone(tmp_path, monkeypatch):
    store, suite, host, skill = setup(tmp_path)
    log = tmp_path / 'log'
    monkeypatch.setenv('FAKE_LOG', str(log))
    evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    calls = len(log.read_text().splitlines())
    (suite / 'runs' / 'r1' / 'answers' / 'c1__bare__m1__1.json').write_text('{"case":')
    assert evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))['reviewed'] == '2/2'
    assert len(log.read_text().splitlines()) == calls + 1  # the same text again, so the review stands
    case = json.loads((suite / 'cases' / 'c1.json').read_text())
    (suite / 'cases' / 'c1.json').write_text(json.dumps(dict(case, date='2026-05-06')))
    evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    assert log.read_text().splitlines()[calls + 1:] .count('review high') == 1
    packet = json.loads((suite / 'runs' / 'r1' / 'reviews' / 'c1__m1__1' / 'packet.json').read_text())
    assert {i['date'] for i in packet['items']} == {'2026-05-06'}


def test_cli_and_mcp_writes_pass_the_case_through(tmp_path, monkeypatch):
    payload = tmp_path / 'payload.json'
    payload.write_text(json.dumps({'asset': dict(asset(), id='send', status='adopted'), 'expected_revision': 0, 'authorization': AUTH, 'case': CASE}))
    p = subprocess.run([sys.executable, '-m', 'myos', '--data', str(tmp_path / 'cli'), 'put', str(payload)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert (tmp_path / 'cli' / 'evals' / 'cases' / 'confirm-appointment.json').exists()
    monkeypatch.setenv('MYOS_DATA_DIR', str(tmp_path / 'mcp'))
    asyncio.run(mcp.call_tool('myos_put', dict(asset=dict(asset(), id='send', status='adopted'), expected_revision=0, authorization=AUTH, case=CASE)))
    assert (tmp_path / 'mcp' / 'evals' / 'cases' / 'confirm-appointment.json').exists()


def test_export_problems_are_reported_and_the_next_write_completes_the_export(tmp_path, monkeypatch):
    store = Store(tmp_path / 'data')
    original = Store.connect
    def locked(self, *, write=False):
        if not write:
            raise sqlite3.OperationalError('database is locked')
        return original(self, write=write)
    monkeypatch.setattr(Store, 'connect', locked)
    result = store.put(dict(asset(), id='send', status='adopted'), expected_revision=0, authorization=AUTH, case=CASE)
    assert result['revision'] == 1 and 'cannot read saved cases' in result['case_export']['errors'][0]
    monkeypatch.undo()
    case_file = tmp_path / 'data' / 'evals' / 'cases' / 'confirm-appointment.json'
    assert not case_file.exists()
    result = store.put(dict(asset(), id='other'), expected_revision=0, authorization=AUTH)
    assert case_file.exists() and 'case_export' not in result


def test_eval_says_when_saved_cases_could_not_be_exported(tmp_path, monkeypatch):
    store, suite, host, skill = setup(tmp_path)
    (store.root / 'evals').symlink_to(suite)
    monkeypatch.setenv('FAKE_LOG', str(tmp_path / 'log'))
    def denied(*args):
        raise PermissionError('denied')
    monkeypatch.setattr('myos.personal.store.os.link', denied)
    store.put(dict(asset(), id='send', title='Final click is mine', type='boundary', status='adopted'), expected_revision=1,
              authorization=AUTH, case=CASE)
    result = evaluate(store, store.root / 'evals', 'r1', models=['m1'], skill=skill, host=str(host))
    assert result['cases'] == 2 and 'confirm-appointment' in result['errors'][0]
    assert '## Incomplete run' in (suite / 'runs' / 'r1' / 'report.md').read_text()


def test_damaged_cache_files_are_redone_and_retired_cases_are_skipped(tmp_path, monkeypatch):
    store, suite, host, skill = setup(tmp_path)
    log = tmp_path / 'log'
    monkeypatch.setenv('FAKE_LOG', str(log))
    evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))
    calls = len(log.read_text().splitlines())
    answer = suite / 'runs' / 'r1' / 'answers' / 'c1__bare__m1__1.json'
    answer.write_text(json.dumps({k: v for k, v in json.loads(answer.read_text()).items() if k != 'result'}))
    (suite / 'runs' / 'r1' / 'reviews' / 'n1__m1__1' / 'flags.json').write_text('[{"id":')
    assert evaluate(store, suite, 'r1', models=['m1'], skill=skill, host=str(host))['reviewed'] == '2/2'
    assert log.read_text().splitlines()[calls:].count('review high') == 1 and len(log.read_text().splitlines()) == calls + 2
    case = json.loads((suite / 'cases' / 'n1.json').read_text())
    (suite / 'cases' / 'n1.json').write_text(json.dumps(dict(case, retired=True)))
    assert evaluate(store, suite, 'r2', models=['m1'], skill=skill, host=str(host))['cases'] == 1
