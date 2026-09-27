"""Validate an offline semantic review; never generate or judge an answer."""

from myos.personal.answer_review import check_review, main, parse_json  # noqa: F401

if __name__ == "__main__":
    raise SystemExit(main())
