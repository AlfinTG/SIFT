import csv
import json
from pathlib import Path

from ml.dataset_review import apply_review_ledger, build_review_report, load_manifest, load_review_ledger, main


MANIFEST = Path(__file__).parents[1] / "ml" / "pilot_manifest.json"


def row(sample_id: str, *, label: str = "SCAM", family: str = "fake_job", text: str = "Pay a fee to confirm your internship.", status: str = "accepted", language: str = "en") -> dict[str, str]:
    prefix = f"sift-pilot-v2-{label.lower()}-{family}-"
    return {
        "sample_id": sample_id,
        "message_text": text,
        "label": label,
        "scam_type": family if label == "SCAM" else "",
        "difficulty": "easy" if label == "SCAM" else "hard_negative",
        "template_family": prefix + "01",
        "source_batch": "sift-pilot-v2-scam-40" if label == "SCAM" else f"sift-pilot-v2-{label.lower()}-40",
        "review_status": status,
        "language": language,
    }


def test_manifest_has_controlled_family_and_language_targets() -> None:
    manifest = load_manifest(MANIFEST)
    assert len(manifest["strata"]) == 11
    assert sum(item["target_count"] for item in manifest["strata"]) == 96
    assert sum(item["target_count"] for item in manifest["strata"] if item["label"] == "SCAM") == 40
    assert {item["context_family"] for item in manifest["strata"] if item["label"] == "SCAM"} == {
        "fake_job", "phishing_kyc", "upi_payment", "reward_lottery", "other",
    }
    assert manifest["language_targets"]["SCAM"] == {"en": 16, "hi": 8, "hinglish": 12, "mixed": 4}
    assert manifest["language_targets"]["LEGITIMATE"] == {"en": 16, "hi": 8, "hinglish": 12, "mixed": 4}
    assert manifest["language_targets"]["AMBIGUOUS"] == {"en": 6, "hi": 4, "hinglish": 4, "mixed": 2}
    assert {item["source_batch"] for item in manifest["strata"] if item["label"] == "LEGITIMATE"} == {"sift-pilot-v2-legitimate-40"}


def test_review_reports_cross_batch_duplicate_and_ledger_reason() -> None:
    manifest = load_manifest(MANIFEST)
    first = row("one")
    second = row("two", text=first["message_text"])
    second["source_batch"] = "sift-pilot-v2-scam-40"  # distinct files are represented together at review time
    report = build_review_report([first, second], manifest)
    assert report["exact_duplicate_findings"][0]["sample_id"] == "two"
    ledger = {entry["sample_id"]: entry for entry in report["review_ledger"]}
    assert ledger["two"]["review_status"] == "needs_review"
    assert "exact duplicate" in ledger["two"]["rejection_reason"]


def test_review_flags_manifest_mismatch_and_near_duplicate() -> None:
    manifest = load_manifest(MANIFEST)
    first = row("one", text="Pay the internship registration fee today to confirm your seat.")
    second = row("two", text="Pay the internship registration fee tomorrow to confirm your seat.")
    second["scam_type"] = "upi_payment"
    report = build_review_report([first, second], manifest)
    reasons = [issue["reason"] for issue in report["manifest_findings"]]
    assert "SCAM subtype does not match manifest family" in reasons
    assert report["near_duplicate_candidates"]


def test_quota_report_tracks_accepted_and_remaining() -> None:
    manifest = load_manifest(MANIFEST)
    report = build_review_report([row("one")], manifest)
    fake_job = next(item for item in report["quota_report"] if item["stratum_id"] == "scam-fake_job")
    assert fake_job["accepted_count"] == 1
    assert fake_job["remaining"] == 7
    english_scam = next(item for item in report["language_quota_report"] if item["label"] == "SCAM" and item["language"] == "en")
    assert english_scam["accepted_count"] == 1
    assert english_scam["remaining"] == 15


def test_cli_writes_review_ledger_and_accepted_export(tmp_path, monkeypatch) -> None:
    input_path = tmp_path / "reviewed.csv"
    sample = row("accepted-one")
    with input_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(sample))
        writer.writeheader()
        writer.writerow(sample)
    report_path = tmp_path / "report.json"
    ledger_path = tmp_path / "ledger.csv"
    accepted_path = tmp_path / "accepted.csv"
    monkeypatch.setattr(
        "sys.argv",
        ["dataset_review", str(input_path), "--report", str(report_path), "--ledger", str(ledger_path), "--accepted-output", str(accepted_path)],
    )
    main()
    assert json.loads(report_path.read_text(encoding="utf-8"))["row_count"] == 1
    with ledger_path.open(encoding="utf-8") as file:
        ledger_row = list(csv.DictReader(file))[0]
    assert ledger_row["sample_id"] == "accepted-one"
    assert ledger_row["review_decision"] == "accepted"
    assert {"reviewer_id", "reviewed_at", "review_notes"} <= ledger_row.keys()
    with accepted_path.open(encoding="utf-8") as file:
        assert list(csv.DictReader(file))[0]["review_status"] == "accepted"


def test_completed_ledger_derives_traceable_accepted_export(tmp_path) -> None:
    sample = row("reviewed-one", status="unreviewed")
    ledger_path = tmp_path / "completed-ledger.csv"
    with ledger_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["sample_id", "review_decision", "reviewer_id", "reviewed_at", "review_notes"])
        writer.writeheader()
        writer.writerow({"sample_id": "reviewed-one", "review_decision": "accepted", "reviewer_id": "reviewer-a", "reviewed_at": "2026-11-24T10:00:00+05:30", "review_notes": "Evidence and language verified."})
    derived = apply_review_ledger([sample], load_review_ledger(ledger_path))
    assert derived[0]["review_status"] == "accepted"
    assert derived[0]["review_decision"] == "accepted"
    assert derived[0]["reviewer_id"] == "reviewer-a"
    assert derived[0]["reviewed_at"] == "2026-11-24T10:00:00+05:30"
