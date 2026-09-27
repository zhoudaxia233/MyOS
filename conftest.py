"""Keep live personal stores, host files and trace settings out of test fixtures."""
import pytest


@pytest.fixture(autouse=True)
def isolated_tool_environment(monkeypatch):
    # Tests opt into their own temporary stores, sync targets and trace settings.
    for name in ('MYOS_TRACE', 'MYOS_TRACE_DIR', 'MYOS_TRACE_GROUP', 'MYOS_DATA_DIR', 'MYOS_SYNC_TARGETS'):
        monkeypatch.delenv(name, raising=False)
