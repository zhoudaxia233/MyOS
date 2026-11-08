"""Keep live personal stores, host files and trace settings out of test fixtures."""
import os
from pathlib import Path

import pytest

# `python -m myos` in subprocesses runs this checkout's code, not whatever the environment has installed.
SRC = str(Path(__file__).resolve().parent / 'src')
os.environ['PYTHONPATH'] = os.pathsep.join([SRC, *filter(None, [os.environ.get('PYTHONPATH')])])


@pytest.fixture(autouse=True)
def isolated_tool_environment(monkeypatch):
    # Tests opt into their own temporary stores, sync targets and trace settings.
    for name in ('MYOS_TRACE', 'MYOS_TRACE_DIR', 'MYOS_TRACE_GROUP', 'MYOS_DATA_DIR', 'MYOS_SYNC_TARGETS'):
        monkeypatch.delenv(name, raising=False)
