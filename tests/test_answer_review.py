"""Offline review integrity, not a test of an LLM's semantic accuracy."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from myos.personal.answer_review import check_review


@pytest.fixture
def example():
    packet = {"items": [{"id": "R1", "question": "What needs my feedback?",
                        "source": "Draft v2 needs your factual review. It has not been sent.",
                        "answer": "Please check the facts in draft v2.",
                        "needs": [{"id": "N1", "description": "Identify factual review as the next step.",
                                   "rationale": "The user asks what needs feedback.",
                                   "source_quote": "needs your factual review"}]}]}
    raw = json.dumps(packet).encode()
    review = {"packet_sha256": hashlib.sha256(raw).hexdigest(), "reviews": [{"id": "R1", "full_answer_checked": True,
              "support": [{"status": "supported", "answer_quote": "check the facts",
                           "source_quote": "needs your factual review", "reason": "Matches the stated request."}],
              "coverage": [{"id": "N1", "status": "covered", "answer_quote": "check the facts",
                            "reason": "Gives the requested next step."}]}]}
    return raw, review


def test_short_answer_can_pass_without_repeating_every_source_fact(example):
    result = check_review(*example)
    assert result["results"] == [{"id": "R1", "support": "pass", "coverage": "pass", "overall": "pass"}]


@pytest.mark.parametrize("axis,status,expected", [("coverage", "missing", "fail"),
                                                   ("coverage", "unclear", "unclear"),
                                                   ("support", "unsupported", "fail"),
                                                   ("support", "unclear", "unclear")])
def test_axes_stay_separate_and_uncertainty_is_not_pass(example, axis, status, expected):
    raw, review = example
    review["reviews"][0][axis][0]["status"] = status
    result = check_review(raw, review)["results"][0]
    assert result["overall"] == expected
    assert result["support" if axis == "coverage" else "coverage"] == "pass"


@pytest.mark.parametrize("mutation", ["packet", "answer_quote", "source_quote", "need_quote", "missing_need",
                                      "duplicate_need", "extra_need", "missing_answer", "duplicate_answer",
                                      "empty_claims", "unconditional_skip", "empty_reason", "unchecked_answer"])
def test_rejects_changed_inputs_missing_checks_and_fabricated_evidence(example, mutation):
    raw, review = deepcopy(example)
    row = review["reviews"][0]
    if mutation == "packet":
        raw += b" "
    elif mutation in ("answer_quote", "source_quote"):
        row["support"][0][mutation] = "This quote was never present."
    elif mutation == "need_quote":
        packet = json.loads(raw)
        packet["items"][0]["needs"][0]["source_quote"] = "Invented requirement evidence"
        raw = json.dumps(packet).encode()
        review["packet_sha256"] = hashlib.sha256(raw).hexdigest()
    elif mutation == "missing_need":
        row["coverage"] = []
    elif mutation == "duplicate_need":
        row["coverage"] *= 2
    elif mutation == "extra_need":
        row["coverage"].append({**row["coverage"][0], "id": "N2"})
    elif mutation == "missing_answer":
        review["reviews"] = []
    elif mutation == "duplicate_answer":
        review["reviews"] *= 2
    elif mutation == "empty_claims":
        row["support"] = []
    elif mutation == "unconditional_skip":
        row["coverage"][0]["status"] = "not_applicable"
    elif mutation == "unchecked_answer":
        row["full_answer_checked"] = False
    else:
        row["coverage"][0]["reason"] = " "
    with pytest.raises(ValueError):
        check_review(raw, review)


def test_conditional_need_can_be_inapplicable(example):
    raw, review = example
    packet = json.loads(raw)
    packet["items"][0]["needs"].append({**packet["items"][0]["needs"][0], "id": "N2", "condition": "Only when discussing sending."})
    raw = json.dumps(packet).encode()
    review["packet_sha256"] = hashlib.sha256(raw).hexdigest()
    review["reviews"][0]["coverage"].append({"id": "N2", "status": "not_applicable", "answer_quote": "", "reason": "No sending advice."})
    assert check_review(raw, review)["counts"]["pass"] == 1


def test_packet_cannot_make_every_task_need_optional(example):
    raw, review = example
    packet = json.loads(raw)
    packet["items"][0]["needs"][0]["condition"] = "Only when mentioned."
    raw = json.dumps(packet).encode()
    review["packet_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="unconditional current-task need"):
        check_review(raw, review)


def test_no_factual_claims_requires_explanation_and_still_checks_coverage(example):
    raw, review = example
    review["reviews"][0]["support"] = []
    review["reviews"][0]["no_material_claims_reason"] = "Only a suggested next step, no statement of completed action."
    review["reviews"][0]["coverage"][0]["status"] = "missing"
    row = check_review(raw, review)["results"][0]
    assert row == {"id": "R1", "support": "not_applicable", "coverage": "fail", "overall": "fail"}


@pytest.mark.parametrize("status,exit_code", [("covered", 0), ("missing", 1), ("unclear", 3)])
def test_actual_command_reports_quality_separately_from_validity(tmp_path, example, status, exit_code):
    raw, review = example
    review["reviews"][0]["coverage"][0]["status"] = status
    packet_path, review_path = tmp_path / "packet.json", tmp_path / "review.json"
    packet_path.write_bytes(raw)
    review_path.write_text(json.dumps(review))
    script = Path(__file__).resolve().parents[1] / "scripts/check_answer_review.py"
    result = subprocess.run([sys.executable, str(script), str(packet_path), str(review_path)], capture_output=True, text=True)
    assert result.returncode == exit_code
    assert json.loads(result.stdout)["counts"][{0: "pass", 1: "fail", 3: "unclear"}[exit_code]] == 1
    assert packet_path.read_bytes() == raw


def test_actual_command_rejects_invalid_review(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts/check_answer_review.py"
    packet, review = tmp_path / "packet.json", tmp_path / "review.json"
    packet.write_text('{"items": []}')
    review.write_text('{}')
    result = subprocess.run([sys.executable, str(script), str(packet), str(review)], capture_output=True, text=True)
    assert result.returncode == 2
    assert not result.stdout
    assert "hash mismatch" in result.stderr


@pytest.mark.parametrize("file", ["packet", "review"])
def test_actual_command_rejects_duplicate_fields_instead_of_overwriting_failure(tmp_path, example, file):
    raw, review = example
    review_text = json.dumps(review)
    if file == "review":
        review_text = review_text.replace('"status": "supported"', '"status": "unsupported", "status": "supported"')
    else:
        raw = raw.replace(b'"id": "R1"', b'"id": "HIDDEN", "id": "R1"', 1)
        review["packet_sha256"] = hashlib.sha256(raw).hexdigest()
        review_text = json.dumps(review)
    packet_path, review_path = tmp_path / "packet.json", tmp_path / "review.json"
    packet_path.write_bytes(raw)
    review_path.write_text(review_text)
    script = Path(__file__).resolve().parents[1] / "scripts/check_answer_review.py"
    result = subprocess.run([sys.executable, str(script), str(packet_path), str(review_path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "duplicate JSON field" in result.stderr
    assert not result.stdout
