import json
from io import StringIO
from pathlib import Path

from myos.cli import collect_input, main


class FakeStdin:
    def __init__(self, content: str, is_tty: bool) -> None:
        self._content = content
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty

    def read(self) -> str:
        return self._content


def test_collect_input_prefers_argv_when_present() -> None:
    raw_input, source = collect_input(["hello", "world"], FakeStdin("", True))
    assert raw_input == "hello world"
    assert source == "argv"


def test_cli_supports_explicit_mode_from_stdin(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    log_path = tmp_path / "sessions.jsonl"
    monkeypatch.setenv("MYOS_LOG_PATH", str(log_path))
    monkeypatch.setattr("sys.stdin", FakeStdin("I want to write an essay.", False))

    exit_code = main(["--mode", "learn"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[learn]" in captured.out

    event = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["detected_mode"] == "learn"
    assert event["mode_source"] == "explicit"
    assert event["handler_used"] == "guided_learn"
    assert event["response_kind"] == "guided_response"


def test_cli_heuristic_mode_and_logging(monkeypatch, tmp_path: Path, capsys) -> None:
    log_path = tmp_path / "sessions.jsonl"
    monkeypatch.setenv("MYOS_LOG_PATH", str(log_path))
    monkeypatch.setattr("sys.stdin", StringIO())

    exit_code = main(["I keep thinking there is something here."])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[explore]" in captured.out

    event = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["raw_input"] == "I keep thinking there is something here."
    assert event["detected_mode"] == "explore"
    assert event["mode_source"] == "heuristic"
    assert "normalized_request" in event
