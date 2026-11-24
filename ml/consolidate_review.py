"""Create a traceable consolidated audit and focused human-review package.

This utility deliberately consumes only derived canonical CSVs.  It never
updates raw exports or turns an automated finding into an acceptance decision.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ml.classifier import CANONICAL_FIELDS
from ml.dataset_review import (
    REVIEW_FIELDS,
    build_review_report,
    load_manifest,
    near_duplicate_report,
)


BRAND_PATTERN = re.compile(r"\b(?:[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\b")


def _load_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not CANONICAL_FIELDS <= set(reader.fieldnames):
                raise ValueError(f"{path} is not a canonical dataset export")
            for row in reader:
                row = dict(row)
                row["derived_file"] = str(path).replace("\\", "/")
                rows.append(row)
    return rows


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _raw_inventory(paths: list[Path]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            count = sum(1 for _ in csv.DictReader(handle))
        inventory.append({
            "path": str(path).replace("\\", "/"),
            "csv_records": count,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    return inventory


def build_audit(rows: list[dict[str, str]], raw_paths: list[Path], manifest_path: Path) -> dict[str, Any]:
    review = build_review_report(rows, load_manifest(manifest_path))
    evidence_issues: list[dict[str, str]] = []
    missing_fields: list[dict[str, str]] = []
    brand_candidates: list[dict[str, str]] = []
    families: defaultdict[str, list[str]] = defaultdict(list)
    for row in rows:
        sample_id = row["sample_id"]
        for field in ("sample_id", "message_text", "label", "language", "source", "source_batch", "template_family"):
            if not row.get(field, "").strip():
                missing_fields.append({"sample_id": sample_id, "field": field})
        try:
            quotes = json.loads(row["evidence_quotes"])
            if not isinstance(quotes, list) or not quotes or any(not isinstance(quote, str) or quote not in row["message_text"] for quote in quotes):
                evidence_issues.append({"sample_id": sample_id, "reason": "evidence quote is empty or not an exact message substring"})
        except json.JSONDecodeError:
            evidence_issues.append({"sample_id": sample_id, "reason": "evidence_quotes is not JSON"})
        families[row["template_family"]].append(sample_id)
        names = BRAND_PATTERN.findall(row["message_text"])
        if row["label"] == "SCAM" and names:
            brand_candidates.append({"sample_id": sample_id, "possible_named_entity": names[0]})

    template_duplicates = [
        {"template_family": family, "sample_ids": sample_ids}
        for family, sample_ids in families.items() if len(sample_ids) > 1
    ]
    return {
        "audit_version": "sift-consolidated-audit-v1",
        "raw_inventory": _raw_inventory(raw_paths),
        "eligible_candidate_count": len(rows),
        "candidate_distribution": {
            "labels": dict(Counter(row["label"] for row in rows)),
            "languages": dict(Counter(row["language"] for row in rows)),
            "scam_types": dict(Counter(row["scam_type"] for row in rows if row["label"] == "SCAM")),
            "review_statuses": dict(Counter(row["review_status"] for row in rows)),
            "source_batches": dict(Counter(row["source_batch"] for row in rows)),
        },
        "schema_missing_fields": missing_fields,
        "evidence_quote_issues": evidence_issues,
        "exact_duplicate_findings": review["exact_duplicate_findings"],
        "near_duplicate_candidates": near_duplicate_report(rows),
        "template_family_duplicates": template_duplicates,
        "manifest_findings": review["manifest_findings"],
        "possible_brand_or_impersonation_review": brand_candidates,
        "training_gate": {
            "passed": False,
            "reason": "No eligible candidate has a completed accepted review decision with reviewer identity and timestamp.",
        },
        "limitations": [
            "Automated structural validation cannot establish message truthfulness or approve a sample.",
            "The supplied candidates are synthetic and are not a real-world benchmark.",
            "The v2 manifest does not define strata for the v3 fake-job batch or the existing legitimate template families.",
        ],
    }


def _review_package(rows: list[dict[str, str]], audit: dict[str, Any]) -> str:
    by_label: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(row)
    lines = [
        "# Consolidated SIFT review package",
        "",
        "Only the candidates below require a human decision. Automated checks did not approve any row.",
        "Record `accepted`, `rejected`, or `needs_review` in `consolidated-review-ledger.csv`; accepted rows require a reviewer ID and ISO-8601 timestamp.",
        "",
        "## High-priority attention",
        "",
        "- Review all SCAM candidates for fictional-brand impersonation, consumer-detection relevance, and naturalness before acceptance.",
        "- Review the LEGITIMATE candidates for accidental scam-like wording and representativeness; they are English-only.",
        "- Do not approve rows solely because structural checks passed.",
        "",
    ]
    for label, heading in (("SCAM", "Review-ready SCAM candidates"), ("LEGITIMATE", "Review-ready LEGITIMATE candidates")):
        lines.extend([f"## {heading}", ""])
        for row in by_label[label]:
            lines.extend([
                f"### {row['sample_id']}",
                "",
                f"- Source: `{row['source_batch']}` / `{row['derived_file']}`",
                f"- Language: `{row['language']}`; family: `{row['template_family']}`",
                f"- Type: `{row['scam_type'] or 'none'}`",
                f"- Message: {row['message_text']}",
                f"- Rationale: {row['rationale']}",
                "",
            ])
    lines.extend([
        "## Rejected and unresolved source records",
        "",
        "- The v3 fake-job raw batch has three conversion rejections: unsupported `medium` difficulty, a likely identifier/email safety hit, and malformed completion JSON.",
        "- The v2 LEGITIMATE raw batch has ten pre-existing conversion rejections; see its `rejected.csv`.",
        "- Both duplicate v2 SCAM raw exports remain excluded because they are bulk-array completions, not safely convertible per-message canonical records. Their existing diagnostic must not be treated as approved training data.",
        "",
        "## Audit notes",
        "",
        f"- Exact duplicate findings: {len(audit['exact_duplicate_findings'])}",
        f"- Near-duplicate candidates: {len(audit['near_duplicate_candidates'])}",
        f"- Repeated template families: {len(audit['template_family_duplicates'])}",
        "- No AMBIGUOUS candidate was produced by the eligible inputs.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a SIFT consolidated audit and review package from canonical candidate exports.")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--raw", nargs="+", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=Path("ml/pilot_manifest.json"))
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    args = parser.parse_args()

    rows = _load_rows(args.inputs)
    audit = build_audit(rows, args.raw, args.manifest)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Preserve the existing review convention while marking every candidate as requiring review.
    _write_csv(args.ledger, [{
        "sample_id": row["sample_id"], "review_status": "needs_review", "review_decision": "needs_review",
        "reviewer_id": "", "reviewed_at": "", "review_notes": "",
        "rejection_reason": "Human review required; automated structural checks are not approval.",
    } for row in rows])
    args.package.write_text(_review_package(rows, audit), encoding="utf-8")


if __name__ == "__main__":
    main()
