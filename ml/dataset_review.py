"""Offline quality gates for the controlled SIFT synthetic-data pilot.

This module reads derived canonical CSV files only.  It never contacts a
provider and it never changes raw exports.  Its reports are intended to guide
human review; they do not automatically mark a row accepted.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REVIEW_FIELDS = [
    "sample_id",
    "review_status",
    "review_decision",
    "reviewer_id",
    "reviewed_at",
    "review_notes",
    "rejection_reason",
]
VALID_REVIEW_STATUSES = {"unreviewed", "accepted", "rejected", "needs_review"}
PILOT_LABELS = {"SCAM", "LEGITIMATE", "AMBIGUOUS"}
PILOT_LANGUAGES = {"en", "hi", "hinglish", "mixed"}
TOKEN_PATTERN = re.compile(r"[\w₹]+", re.UNICODE)


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        manifest = json.load(file)
    strata = manifest.get("strata")
    if not isinstance(strata, list) or len(strata) != 11:
        raise ValueError("manifest must contain exactly 11 strata")
    required = {"stratum_id", "source_batch", "label", "context_family", "target_count", "difficulty", "template_family_prefix"}
    if any(not isinstance(item, dict) or required - item.keys() for item in strata):
        raise ValueError("each manifest stratum is missing required fields")
    language_targets = manifest.get("language_targets")
    if not isinstance(language_targets, dict) or set(language_targets) != PILOT_LABELS:
        raise ValueError("manifest must contain language targets for every pilot label")
    for label, targets in language_targets.items():
        if not isinstance(targets, dict) or set(targets) != PILOT_LANGUAGES:
            raise ValueError(f"language targets for {label} must cover every pilot language")
        if any(not isinstance(count, int) or count < 0 for count in targets.values()):
            raise ValueError(f"language targets for {label} must be non-negative integers")
        stratum_total = sum(item["target_count"] for item in strata if item["label"] == label)
        if sum(targets.values()) != stratum_total:
            raise ValueError(f"language targets for {label} must equal its stratum target total")
    return manifest


def load_canonical_rows(paths: Iterable[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as file:
            rows.extend(dict(row) for row in csv.DictReader(file))
    return rows


def load_review_ledger(path: Path) -> dict[str, dict[str, str]]:
    """Read human review decisions without changing the canonical source CSV."""

    required = {"sample_id", "review_decision", "reviewer_id", "reviewed_at", "review_notes"}
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or not required <= set(reader.fieldnames):
            raise ValueError("review ledger is missing required traceability columns")
        records = [dict(row) for row in reader]
    ledger: dict[str, dict[str, str]] = {}
    for record in records:
        sample_id = record.get("sample_id", "").strip()
        decision = record.get("review_decision", "").strip()
        if not sample_id or decision not in VALID_REVIEW_STATUSES:
            raise ValueError("review ledger contains an invalid sample_id or review_decision")
        if sample_id in ledger:
            raise ValueError("review ledger contains duplicate sample_id values")
        if decision == "accepted" and (not record.get("reviewer_id", "").strip() or not record.get("reviewed_at", "").strip()):
            raise ValueError("accepted review decisions require reviewer_id and reviewed_at")
        ledger[sample_id] = record
    return ledger


def apply_review_ledger(rows: list[dict[str, str]], ledger: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    """Return derived rows with human decisions applied; never overwrite input CSVs."""

    sample_ids = {row.get("sample_id", "") for row in rows}
    unknown = set(ledger) - sample_ids
    if unknown:
        raise ValueError("review ledger references sample_id values absent from the input rows")
    derived: list[dict[str, str]] = []
    for row in rows:
        updated = dict(row)
        record = ledger.get(updated.get("sample_id", ""))
        if record:
            updated["review_status"] = record["review_decision"].strip()
        derived.append(updated)
    return derived


def _normalise(text: str) -> str:
    return " ".join(text.casefold().split())


def _tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(_normalise(text)))


def _stratum_for(row: dict[str, str], strata: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = [
        item for item in strata
        if row.get("source_batch") == item["source_batch"]
        and row.get("label") == item["label"]
        and row.get("template_family", "").startswith(item["template_family_prefix"])
    ]
    return matches[0] if len(matches) == 1 else None


def manifest_findings(rows: list[dict[str, str]], manifest: dict[str, Any]) -> list[dict[str, str]]:
    """Return row-level manifest violations, including quota overflows."""

    findings: list[dict[str, str]] = []
    matched: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        stratum = _stratum_for(row, manifest["strata"])
        if stratum is None:
            findings.append({"sample_id": row.get("sample_id", ""), "reason": "row does not match exactly one manifest stratum"})
            continue
        expected_difficulty = stratum["difficulty"]
        actual_difficulty = row.get("difficulty", "")
        if expected_difficulty == "easy_or_edge_case":
            difficulty_ok = actual_difficulty in {"easy", "edge_case"}
        else:
            difficulty_ok = actual_difficulty == expected_difficulty
        if not difficulty_ok:
            findings.append({"sample_id": row.get("sample_id", ""), "reason": "difficulty does not match manifest stratum"})
        if row.get("label") == "SCAM" and row.get("scam_type") != stratum["context_family"]:
            findings.append({"sample_id": row.get("sample_id", ""), "reason": "SCAM subtype does not match manifest family"})
        if row.get("label") == "LEGITIMATE" and row.get("scam_type", "") != "":
            findings.append({"sample_id": row.get("sample_id", ""), "reason": "LEGITIMATE row has a subtype"})
        matched[stratum["stratum_id"]].append(row)

    for stratum in manifest["strata"]:
        accepted = [row for row in matched[stratum["stratum_id"]] if row.get("review_status") == "accepted"]
        for row in accepted[stratum["target_count"]:]:
            findings.append({"sample_id": row.get("sample_id", ""), "reason": "accepted quota exceeds manifest target"})
    return findings


def exact_duplicate_findings(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[_normalise(row.get("message_text", ""))].append(row)
    findings: list[dict[str, str]] = []
    for group in grouped.values():
        if len(group) > 1:
            keeper = group[0].get("sample_id", "")
            for duplicate in group[1:]:
                findings.append({"sample_id": duplicate.get("sample_id", ""), "reason": f"exact duplicate of {keeper}"})
    return findings


def near_duplicate_report(rows: list[dict[str, str]], threshold: float = 0.80) -> list[dict[str, Any]]:
    """Flag lexical near-duplicates for human inspection; do not auto-reject."""

    report: list[dict[str, Any]] = []
    for left_index, left in enumerate(rows):
        left_text = _normalise(left.get("message_text", ""))
        left_tokens = _tokens(left_text)
        if not left_tokens:
            continue
        for right in rows[left_index + 1:]:
            right_text = _normalise(right.get("message_text", ""))
            if left_text == right_text:
                continue
            right_tokens = _tokens(right_text)
            union = left_tokens | right_tokens
            score = len(left_tokens & right_tokens) / len(union) if union else 0.0
            if score >= threshold:
                report.append({
                    "left_sample_id": left.get("sample_id", ""),
                    "right_sample_id": right.get("sample_id", ""),
                    "token_jaccard": round(score, 3),
                    "left_template_family": left.get("template_family", ""),
                    "right_template_family": right.get("template_family", ""),
                })
    return report


def quota_report(rows: list[dict[str, str]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    for stratum in manifest["strata"]:
        matching = [row for row in rows if _stratum_for(row, [stratum])]
        statuses = Counter(row.get("review_status", "") for row in matching)
        accepted = statuses["accepted"]
        report.append({
            "stratum_id": stratum["stratum_id"], "target_count": stratum["target_count"],
            "accepted_count": accepted, "remaining": max(0, stratum["target_count"] - accepted),
            "overflow": max(0, accepted - stratum["target_count"]),
            "unreviewed_count": statuses["unreviewed"], "needs_review_count": statuses["needs_review"],
            "rejected_count": statuses["rejected"],
        })
    return report


def language_quota_report(rows: list[dict[str, str]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Report planning quotas by label/language without forcing poor-quality rows in."""

    report: list[dict[str, Any]] = []
    for label, targets in manifest["language_targets"].items():
        for language, target_count in targets.items():
            matching = [row for row in rows if row.get("label") == label and row.get("language") == language]
            statuses = Counter(row.get("review_status", "") for row in matching)
            accepted = statuses["accepted"]
            report.append({
                "label": label,
                "language": language,
                "target_count": target_count,
                "accepted_count": accepted,
                "remaining": max(0, target_count - accepted),
                "overflow": max(0, accepted - target_count),
                "unreviewed_count": statuses["unreviewed"],
                "needs_review_count": statuses["needs_review"],
                "rejected_count": statuses["rejected"],
            })
    return report


def build_review_report(rows: list[dict[str, str]], manifest: dict[str, Any]) -> dict[str, Any]:
    invalid_statuses = [
        {"sample_id": row.get("sample_id", ""), "reason": "invalid review_status"}
        for row in rows if row.get("review_status") not in VALID_REVIEW_STATUSES
    ]
    manifest_issues = manifest_findings(rows, manifest)
    duplicate_issues = exact_duplicate_findings(rows)
    reasons: defaultdict[str, list[str]] = defaultdict(list)
    for issue in [*manifest_issues, *duplicate_issues, *invalid_statuses]:
        reasons[issue["sample_id"]].append(issue["reason"])
    ledger = [
        {
            "sample_id": row.get("sample_id", ""),
            "review_status": "needs_review" if reasons[row.get("sample_id", "")] else row.get("review_status", "unreviewed"),
            "review_decision": "needs_review" if reasons[row.get("sample_id", "")] else row.get("review_status", "unreviewed"),
            "reviewer_id": "",
            "reviewed_at": "",
            "review_notes": "",
            "rejection_reason": "; ".join(reasons[row.get("sample_id", "")]),
        }
        for row in rows
    ]
    return {
        "row_count": len(rows),
        "manifest_findings": manifest_issues,
        "exact_duplicate_findings": duplicate_issues,
        "near_duplicate_candidates": near_duplicate_report(rows),
        "review_status_findings": invalid_statuses,
        "review_ledger": ledger,
        "quota_report": quota_report(rows, manifest),
        "language_quota_report": language_quota_report(rows, manifest),
    }


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Review derived SIFT pilot CSVs offline.")
    parser.add_argument("inputs", nargs="+", type=Path, help="Derived accepted/ambiguous CSV files")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("pilot_manifest.json"))
    parser.add_argument("--report", type=Path, required=True, help="Destination for a derived JSON report")
    parser.add_argument("--ledger", type=Path, help="Optional derived review ledger CSV")
    parser.add_argument("--review-ledger-input", type=Path, help="Completed human review ledger used only to derive statuses and accepted output")
    parser.add_argument("--accepted-output", type=Path, help="Optional export of rows already marked accepted")
    arguments = parser.parse_args()
    rows = load_canonical_rows(arguments.inputs)
    if arguments.review_ledger_input:
        rows = apply_review_ledger(rows, load_review_ledger(arguments.review_ledger_input))
    report = build_review_report(rows, load_manifest(arguments.manifest))
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if arguments.ledger:
        _write_csv(arguments.ledger, REVIEW_FIELDS, report["review_ledger"])
    if arguments.accepted_output:
        fieldnames = list(rows[0].keys()) if rows else []
        _write_csv(arguments.accepted_output, fieldnames, [row for row in rows if row.get("review_status") == "accepted"])


if __name__ == "__main__":
    main()
