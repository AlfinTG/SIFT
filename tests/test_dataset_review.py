import csv
import json
from pathlib import Path

from ml.dataset_review import build_review_report, load_manifest, main


MANIFEST = Path(__file__).parents[1] / "ml" / "pilot_manifest.json"


def row(sample_id: str, *, label: str = "SCAM", family: str = "fake_job", text: str = "Pay a fee to confirm your internship.", status: str = "accepted") -> dict[str, str]:
    prefix = f"sift-pilot-v1-{label.lower()}-{family}-"
    return {
        "sample_id": sample_id,
        "message_text": text,
        "label": label,
        "scam_type": family if label == "SCAM" else "",
        "difficulty": "easy" if label == "SCAM" else "hard_negative",
        "template_family": prefix + "01",
        "source_batch": f"sift-pilot-v1-{label.lower()}",
        "review_status": status,
    }


def test_manifest_has_twelve_controlled_strata() -> None:
    manifest = load_manifest(MANIFEST)
    assert len(manifest["strata"]) == 12
    assert sum(item["target_count"] for item in manifest["strata"]) == 96


def test_review_reports_cross_batch_duplicate_and_ledger_reason() -> None:
    manifest = load_manifest(MANIFEST)
    first = row("one")
    second = row("two", text=first["message_text"])
    second["source_batch"] = "sift-pilot-v1-scam"  # distinct files are represented together at review time
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
    assert fake_job["remaining"] == 9


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
        assert list(csv.DictReader(file))[0]["sample_id"] == "accepted-one"
    with accepted_path.open(encoding="utf-8") as file:
        assert list(csv.DictReader(file))[0]["review_status"] == "accepted"
