from __future__ import annotations

import argparse
import sys
from typing import Sequence

from myos.log import append_session_log
from myos.mode import SUPPORTED_MODES, detect_mode
from myos.protocol import build_session_request
from myos.router import route_request


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="myos",
        description="Thin terminal-native MyOS runtime.",
    )
    parser.add_argument(
        "--mode",
        choices=SUPPORTED_MODES,
        help="Explicitly set the session mode.",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Request text. If omitted, MyOS reads from stdin.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    raw_input, source = collect_input(args.text, sys.stdin)
    if not raw_input:
        print(
            'myos expects text or stdin. Example: myos "..." or cat file.md | myos --mode learn.',
            file=sys.stderr,
        )
        return 2

    detected_mode, mode_source = detect_mode(raw_input, explicit_mode=args.mode)
    request = build_session_request(
        raw_input=raw_input,
        source=source,
        mode=detected_mode,
        mode_source=mode_source,
    )
    result = route_request(request)
    append_session_log(request, result)
    print(result.text)
    return 0


def collect_input(argv_text: Sequence[str], stdin: object) -> tuple[str, str]:
    argv_content = " ".join(argv_text).strip()
    stdin_content = _read_stdin(stdin).strip()
    if argv_content and stdin_content:
        return f"{argv_content}\n\n{stdin_content}", "argv+stdin"
    if argv_content:
        return argv_content, "argv"
    if stdin_content:
        return stdin_content, "stdin"
    return "", "none"


def _read_stdin(stdin: object) -> str:
    is_tty = getattr(stdin, "isatty", lambda: True)
    if is_tty():
        return ""
    reader = getattr(stdin, "read")
    return reader()
