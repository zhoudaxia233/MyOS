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
    read_tty = not args.text and _stdin_is_tty(sys.stdin)
    if read_tty:
        print("Paste content below. Press Ctrl-D when finished.", file=sys.stderr)
    raw_input, source = collect_input(args.text, sys.stdin, allow_tty=read_tty)
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


def collect_input(
    argv_text: Sequence[str],
    stdin: object,
    allow_tty: bool = False,
) -> tuple[str, str]:
    argv_content = " ".join(argv_text).strip()
    stdin_content = _read_stdin(stdin, allow_tty=allow_tty).strip()
    if argv_content and stdin_content:
        return f"{argv_content}\n\n{stdin_content}", "argv+stdin"
    if argv_content:
        return argv_content, "argv"
    if stdin_content:
        return stdin_content, "tty" if allow_tty else "stdin"
    return "", "none"


def _read_stdin(stdin: object, allow_tty: bool = False) -> str:
    if _stdin_is_tty(stdin) and not allow_tty:
        return ""
    reader = getattr(stdin, "read")
    return reader()


def _stdin_is_tty(stdin: object) -> bool:
    is_tty = getattr(stdin, "isatty", lambda: True)
    return is_tty()
