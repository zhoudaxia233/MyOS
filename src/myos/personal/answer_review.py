"""Validate an offline semantic review; never generate or judge an answer."""

import argparse
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def parse_json(data):
    def unique_fields(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON field: {key}")
            result[key] = value
        return result

    return json.loads(data, object_pairs_hook=unique_fields)


def indexed(rows, label):
    require(isinstance(rows, list) and rows, f"{label}: expected a nonempty list")
    result = {}
    for row in rows:
        require(isinstance(row, dict) and nonempty(row.get("id")), f"{label}: missing id")
        require(row["id"] not in result, f"{label}: duplicate id {row['id']}")
        result[row["id"]] = row
    return result


def quotation(value, text, label, required=False):
    require(isinstance(value, str), f"{label}: expected a string")
    require(not required or nonempty(value), f"{label}: quotation required")
    require(not value or (nonempty(value) and value in text), f"{label}: quotation not found")


def outcome(statuses, failures):
    if any(status in failures for status in statuses):
        return "fail"
    if "unclear" in statuses:
        return "unclear"
    return "pass"


def check_review(packet_bytes, review):
    """Check correspondence and aggregate the reviewer's semantic judgments.

    A valid review is not proof that its criteria, judgments or claim inventory
    are correct. The packet must be frozen before the reviewer receives it.
    """
    packet = parse_json(packet_bytes)
    require(isinstance(packet, dict) and isinstance(review, dict), "expected JSON objects")
    digest = hashlib.sha256(packet_bytes).hexdigest()
    require(review.get("packet_sha256") == digest, "packet hash mismatch")
    items = indexed(packet.get("items"), "items")
    reviews = indexed(review.get("reviews"), "reviews")
    require(items.keys() == reviews.keys(), "reviews must cover exactly the packet item ids")
    results = []
    for item_id, item in items.items():
        for field in ("question", "source", "answer"):
            require(nonempty(item.get(field)), f"{item_id}: missing {field}")
        needs = indexed(item.get("needs"), f"{item_id} needs")
        for need in needs.values():
            for field in ("description", "rationale"):
                require(nonempty(need.get(field)), f"{item_id}/{need['id']}: missing {field}")
            quotation(need.get("source_quote"), item["source"], f"{item_id}/{need['id']} source", True)
            require(isinstance(need.get("condition", ""), str), "condition must be a string")
        require(any(not nonempty(need.get("condition")) for need in needs.values()), f"{item_id}: an unconditional current-task need is required")

        row = reviews[item_id]
        require(row.get("full_answer_checked") is True, f"{item_id}: full-answer review acknowledgement required")
        support = row.get("support")
        require(isinstance(support, list), f"{item_id}: material claim review required")
        require(support or nonempty(row.get("no_material_claims_reason")), f"{item_id}: explain absence of material claims")
        for claim in support:
            require(isinstance(claim, dict), f"{item_id}: expected claim object")
            require(claim.get("status") in ("supported", "unsupported", "unclear"), f"{item_id}: invalid support status")
            require(nonempty(claim.get("reason")), f"{item_id}: claim reason required")
            quotation(claim.get("answer_quote"), item["answer"], f"{item_id} claim", True)
            quotation(claim.get("source_quote"), item["source"], f"{item_id} evidence", claim["status"] == "supported")

        coverage = indexed(row.get("coverage"), f"{item_id} coverage")
        require(coverage.keys() == needs.keys(), f"{item_id}: coverage must include exactly all need ids")
        for need_id, finding in coverage.items():
            status = finding.get("status")
            require(status in ("covered", "missing", "unclear", "not_applicable"), f"{item_id}/{need_id}: invalid coverage status")
            require(nonempty(finding.get("reason")), f"{item_id}/{need_id}: coverage reason required")
            quotation(finding.get("answer_quote"), item["answer"], f"{item_id}/{need_id} answer", status == "covered")
            require(status != "not_applicable" or nonempty(needs[need_id].get("condition")), f"{item_id}/{need_id}: unconditional need cannot be skipped")

        source_status = outcome([claim["status"] for claim in support], {"unsupported"}) if support else "not_applicable"
        needs_status = outcome([finding["status"] for finding in coverage.values()], {"missing"})
        results.append({"id": item_id, "support": source_status, "coverage": needs_status,
                        "overall": outcome([source_status, needs_status], {"fail"})})
    return {"validation": "valid", "packet_sha256": digest, "results": results,
            "assessment": outcome([row["overall"] for row in results], {"fail"}),
            "counts": {status: sum(row["overall"] == status for row in results)
                       for status in ("pass", "fail", "unclear")},
            "limit": "Assessment comes from the semantic reviewer. Code checks evidence correspondence, not truth, criterion relevance or completeness of the claim inventory."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("review", type=Path)
    args = parser.parse_args()
    try:
        result = check_review(args.packet.read_bytes(), parse_json(args.review.read_text()))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Invalid review: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["counts"]["fail"] else 3 if result["counts"]["unclear"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
