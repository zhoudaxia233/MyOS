"""Keep active entry points clear and current documentation links working."""
import os
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def assert_no_tracked_retired_roots(root):
    # Ignored private leftovers may survive an update; only the Git index defines
    # which old entry points this checkout would ship.
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).split(b'\0')
    roots = {os.fsdecode(path).split('/', 1)[0] for path in tracked if path}
    for name in ('modules', 'orchestrator', 'core', 'routines', 'evals', 'var', 'start', 'archive', 'services', 'ARCHITECTURE_V2.md', 'DESIGN.md', 'CONSTITUTION.md', 'EXTERNAL_CONTEXT_ADAPTERS.md', 'CYBER_BRAIN.md', 'MUTATION_POLICY.md', 'CHECKLIST.md'):
        assert name not in roots, name


def test_no_retired_framework_in_active_root():
    assert_no_tracked_retired_roots(ROOT)
    assert list((ROOT / '.agents/skills').glob('*/SKILL.md')) == [ROOT / '.agents/skills/myos/SKILL.md']
    # Hosts discover the Skill at .agents/skills; the files live in the package so an installed MyOS carries them.
    assert (ROOT / '.agents/skills/myos').resolve() == ROOT / 'src/myos/skill'


def test_layout_allows_private_leftovers_but_rejects_tracked_entrypoints(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / '.gitignore').write_text('/modules/\n/orchestrator/\n/var/\n')
    for name in ('modules', 'orchestrator', 'var', 'evals'):
        directory = tmp_path / name
        directory.mkdir()
        (directory / 'private.txt').write_bytes(b'private fixture\n')
    subprocess.run(['git', 'add', '.gitignore'], cwd=tmp_path, check=True)
    assert_no_tracked_retired_roots(tmp_path)
    for name in ('modules', 'orchestrator', 'var', 'evals'):
        assert (tmp_path / name / 'private.txt').read_bytes() == b'private fixture\n'

    entrypoint = tmp_path / 'orchestrator' / 'main.py'
    entrypoint.write_text('# retired entry point\n')
    subprocess.run(['git', 'add', '-f', 'orchestrator/main.py'], cwd=tmp_path, check=True)
    with pytest.raises(AssertionError, match='orchestrator'):
        assert_no_tracked_retired_roots(tmp_path)


def test_current_document_links_resolve():
    current = ['README.md', 'README-zh.md', 'AGENTS.md', 'docs/getting-started.md', 'docs/getting-started-zh.md', 'docs/reference.md', 'docs/storage.md', 'docs/storage-zh.md', 'docs/usage-contract.md', 'docs/tracing.md', 'docs/answer-review.md', 'docs/maintenance.md', 'src/myos/skill/SKILL.md']
    for name in current:
        path = ROOT / name
        for target in re.findall(r'\]\(([^)\s]+)\)', path.read_text()):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            assert (path.parent / target.split('#', 1)[0]).exists(), (name, target)
            assert '.agents/skills' not in target, (name, target, 'GitHub cannot follow the link; point at src/myos/skill')

