"""myos setup against a temporary home and a fake Claude Code CLI: plans first, changes only what it lists, repeats safely."""
import sys
import tomllib

import pytest

from myos.personal import setup as connect_module
from myos.personal.cli import main
from myos.personal.setup import setup as connect  # not `setup`: pytest would run that name as a hook
from myos.personal.store import EXPORT_BEGIN, EXPORT_END, Store
from tests.test_personal_store import AUTH, asset

FAKE_CLAUDE = '''\
import pathlib, sys
here = pathlib.Path(__file__).parent
args = sys.argv[1:]
(here / 'calls').open('a').write(' '.join(args) + '\\n')
if args[:2] == ['mcp', 'get']:
    sys.exit(0 if (here / 'registered').exists() else 1)
if args[:2] == ['mcp', 'add']:
    (here / 'registered').write_text(' '.join(args))
'''
SERVER = ['/venv/bin/python', '-m', 'myos.personal.mcp']


@pytest.fixture
def home(tmp_path):
    home = tmp_path / 'home'
    (home / '.claude').mkdir(parents=True)
    (home / '.codex').mkdir()
    (home / '.claude' / 'CLAUDE.md').write_text('# My rules\n\nBe brief.\n')
    (home / '.codex' / 'config.toml').write_text('model = "x"\n\n[mcp_servers.other]\ncommand = "other"\n')
    return home


@pytest.fixture
def claude(tmp_path):
    folder = tmp_path / 'bin'
    folder.mkdir()
    script = folder / 'claude'
    script.write_text(f'#!{sys.executable}\n' + FAKE_CLAUDE)
    script.chmod(0o755)
    return script


def calls(claude):
    log = claude.parent / 'calls'
    return log.read_text().splitlines() if log.exists() else []


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}


def statuses(result):
    return {(s['host'], s['step']): s['status'] for s in result['steps']}


def test_a_dry_run_lists_every_change_and_makes_none(tmp_path, home, claude):
    before = snapshot(home)
    result = connect(Store(tmp_path / 'data'), home, claude=str(claude), server=SERVER)
    assert not result['applied'] and set(statuses(result).values()) == {'todo'}
    assert set(statuses(result)) == {(h, s) for h in ('claude', 'codex') for s in ('skill', 'block', 'tools')}
    assert snapshot(home) == before and not (tmp_path / 'data').exists()
    assert calls(claude) == ['mcp get myos']  # looking is allowed; registering is not


def test_setup_installs_the_skill_the_block_and_the_tools_and_repeats_without_changes(tmp_path, home, claude):
    store = Store(tmp_path / 'data')
    result = connect(store, home, claude=str(claude), server=SERVER, apply=True)
    assert result['applied'] and set(statuses(result).values()) == {'done'}

    for host in ('.claude', '.codex'):
        assert (home / host / 'skills' / 'myos' / 'SKILL.md').read_text() == (connect_module.SKILL / 'SKILL.md').read_text()
        assert (home / host / 'skills' / 'myos' / 'reference' / 'write.md').is_file()
    text = (home / '.claude' / 'CLAUDE.md').read_text()
    assert text.startswith('# My rules\n\nBe brief.\n\n' + EXPORT_BEGIN) and text.count(EXPORT_BEGIN) == 1 and text.rstrip().endswith(EXPORT_END)
    assert 'No adopted assets yet.' in text
    assert (home / '.codex' / 'AGENTS.md').read_text().startswith(EXPORT_BEGIN)  # created when missing
    assert [p.read_text() for p in (store.root / 'sync-backups').iterdir() if p.name.startswith('CLAUDE.md')] == ['# My rules\n\nBe brief.\n']

    targets = f"{(home / '.claude').resolve() / 'CLAUDE.md'}:{(home / '.codex').resolve() / 'AGENTS.md'}"
    assert calls(claude)[-1] == (f'mcp add --scope user myos -e MYOS_DATA_DIR={store.root} -e MYOS_SYNC_TARGETS={targets} '
                                 '-- /venv/bin/python -m myos.personal.mcp')
    config = tomllib.loads((home / '.codex' / 'config.toml').read_text())
    assert config['model'] == 'x' and config['mcp_servers']['other'] == {'command': 'other'}
    assert config['mcp_servers']['myos'] == {'command': '/venv/bin/python', 'args': ['-m', 'myos.personal.mcp'],
                                             'env': {'MYOS_DATA_DIR': str(store.root), 'MYOS_SYNC_TARGETS': targets}}

    after, made = snapshot(home), len(calls(claude))
    again = connect(store, home, claude=str(claude), server=SERVER, apply=True)
    assert set(statuses(again).values()) == {'ok'} and snapshot(home) == after
    assert calls(claude)[made:] == ['mcp get myos']


def test_the_block_shows_adopted_entries_and_later_writes_keep_it_current(tmp_path, home, claude, monkeypatch):
    store = Store(tmp_path / 'data')
    store.put(dict(asset(), id='send', title='Final click is mine', type='boundary', status='adopted', core=True), expected_revision=0, authorization=AUTH)
    connect(store, home, hosts=['claude'], claude=str(claude), server=SERVER, apply=True)
    assert 'Final click is mine' in (home / '.claude' / 'CLAUDE.md').read_text()
    assert not (home / '.codex' / 'AGENTS.md').exists() and 'myos' not in (home / '.codex' / 'config.toml').read_text()

    from myos.personal import sync
    monkeypatch.setenv('MYOS_SYNC_TARGETS', str(home / '.claude' / 'CLAUDE.md'))
    store.put(dict(asset(), id='quiet', title='Quiet option first', status='adopted'), expected_revision=0, authorization=AUTH)
    assert sync.after_put(store)['targets'][0]['status'] == 'updated'
    assert 'Quiet option first' in (home / '.claude' / 'CLAUDE.md').read_text()


def test_setup_leaves_links_and_broken_blocks_alone_and_says_what_is_left_to_do(tmp_path, home):
    linked = tmp_path / 'checkout-skill'
    linked.mkdir()
    (home / '.claude' / 'skills').mkdir()
    (home / '.claude' / 'skills' / 'myos').symlink_to(linked)
    real = tmp_path / 'dotfiles' / 'AGENTS.md'
    real.parent.mkdir()
    real.write_text('Shared rules\n')
    (home / '.codex' / 'AGENTS.md').symlink_to(real)
    (home / '.claude' / 'CLAUDE.md').write_text(f'{EXPORT_BEGIN}\nhalf a block\n')

    result = connect(Store(tmp_path / 'data'), home, claude=None, server=SERVER, apply=True)
    found = statuses(result)
    assert found[('claude', 'skill')] == 'ok' and list(linked.iterdir()) == []
    assert found[('claude', 'block')] == 'blocked' and (home / '.claude' / 'CLAUDE.md').read_text() == f'{EXPORT_BEGIN}\nhalf a block\n'
    assert found[('codex', 'block')] == 'blocked' and real.read_text() == 'Shared rules\n'
    assert found[('claude', 'tools')] == 'manual'  # no Claude Code command on this computer: the step is printed instead
    manual = next(s for s in result['steps'] if (s['host'], s['step']) == ('claude', 'tools'))
    assert 'claude mcp add --scope user myos' in manual['detail'] and '/venv/bin/python -m myos.personal.mcp' in manual['detail']
    assert found[('codex', 'skill')] == found[('codex', 'tools')] == 'done'


def test_setup_keeps_an_existing_registration_and_an_unreadable_codex_config(tmp_path, home, claude):
    (claude.parent / 'registered').write_text('mcp add myos earlier')
    (home / '.codex' / 'config.toml').write_text('not = [valid\n')
    result = connect(Store(tmp_path / 'data'), home, claude=str(claude), server=SERVER, apply=True)
    assert statuses(result)[('claude', 'tools')] == 'ok' and calls(claude) == ['mcp get myos']
    assert statuses(result)[('codex', 'tools')] == 'blocked' and (home / '.codex' / 'config.toml').read_text() == 'not = [valid\n'


def test_setup_needs_an_assistant(tmp_path):
    (tmp_path / 'home').mkdir()
    with pytest.raises(ValueError, match='No assistant found'):
        connect(Store(tmp_path / 'data'), tmp_path / 'home', claude=None, server=SERVER)
    with pytest.raises(ValueError, match='Unknown assistant'):
        connect(Store(tmp_path / 'data'), tmp_path / 'home', hosts=['other'], claude=None, server=SERVER)


def test_cli_shows_the_plan_and_applies_only_with_yes(tmp_path, home, claude, monkeypatch, capsys):
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setenv('PATH', str(claude.parent))
    before = snapshot(home)
    assert main(['--data', str(tmp_path / 'data'), 'setup']) == 0
    plan = capsys.readouterr().out
    assert 'Nothing was changed' in plan and 'myos setup --yes' in plan and 'Claude Code' in plan and 'Codex' in plan
    assert snapshot(home) == before

    assert main(['--data', str(tmp_path / 'data'), 'setup', '--yes', '--host', 'claude']) == 0
    done = capsys.readouterr().out
    assert 'Restart' in done and 'Set up MyOS with me' in done and 'Codex' not in done
    assert (home / '.claude' / 'skills' / 'myos' / 'SKILL.md').is_file() and calls(claude)[-1].startswith('mcp add --scope user myos')
