import csv
from pathlib import Path

import pytest

from ml.classifier import (
    CANONICAL_FIELDS,
    DatasetValidationError,
    ModelUnavailableError,
    load_accepted_dataset,
    load_artifact,
    predict_message,
    save_artifact,
    split_dataset,
    train,
    write_markdown_report,
)


def canonical_row(index: int, label: str, status: str = "accepted") -> dict[str, str]:
    is_scam = label == "SCAM"
    family = "fake_job" if is_scam else ""
    message = f"Pay a fictional registration fee for internship pattern {index}." if is_scam else f"Security reminder for ordinary account notice pattern {index}: never share OTP."
    return {
        "sample_id": f"sample-{label.lower()}-{index}", "message_text": message, "label": label,
        "scam_type": family, "language": "en", "channel": "sms", "tactics": "[]",
        "evidence_quotes": "[]", "rationale": "unit test fixture", "difficulty": "easy",
        "source": "manual_fixture", "source_batch": "unit-test", "generation_prompt_version": "unit",
        "template_family": f"{label.lower()}-family-{index}", "review_status": status,
    }


def write_dataset(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=sorted(CANONICAL_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def accepted_rows() -> list[dict[str, str]]:
    return [*(canonical_row(index, "SCAM") for index in range(8)), *(canonical_row(index, "LEGITIMATE") for index in range(8))]


def test_loader_excludes_ambiguous_unreviewed_and_rejected_rows(tmp_path: Path) -> None:
    path = tmp_path / "canonical.csv"
    rows = accepted_rows() + [
        canonical_row(99, "AMBIGUOUS"),
        canonical_row(100, "SCAM", status="unreviewed"),
        canonical_row(101, "LEGITIMATE", status="rejected"),
    ]
    write_dataset(path, rows)

    dataset = load_accepted_dataset([path])

    assert len(dataset.rows) == 16
    assert set(dataset.labels) == {"SCAM", "LEGITIMATE"}
    assert all(row["review_status"] == "accepted" for row in dataset.rows)


def test_group_splits_keep_template_families_separate(tmp_path: Path) -> None:
    path = tmp_path / "canonical.csv"
    write_dataset(path, accepted_rows())
    splits = split_dataset(load_accepted_dataset([path]))

    train_groups, validation_groups, test_groups = (set(part.groups) for part in (splits.train, splits.validation, splits.test))
    assert not train_groups & validation_groups
    assert not train_groups & test_groups
    assert not validation_groups & test_groups
    assert all(set(part.labels) == {"SCAM", "LEGITIMATE"} for part in (splits.train, splits.validation, splits.test))


def test_training_artifact_and_local_prediction(tmp_path: Path) -> None:
    path = tmp_path / "canonical.csv"
    write_dataset(path, accepted_rows())
    pipeline, splits, report = train(load_accepted_dataset([path]))
    artifact_path = tmp_path / "model.joblib"
    save_artifact(artifact_path, pipeline, training_sample_ids=[row["sample_id"] for row in splits.train.rows])

    prediction = predict_message(artifact_path, "Pay a fictional registration fee today to confirm internship.")

    assert prediction.label in {"SCAM", "LEGITIMATE"}
    assert prediction.score_name == "model_score_not_calibrated_probability"
    assert set(prediction.scores) == {"SCAM", "LEGITIMATE"}
    assert "test" in report and "scam_f1" in report["test"]
    markdown_path = tmp_path / "training-report.md"
    write_markdown_report(markdown_path, report)
    assert "SCAM F1" in markdown_path.read_text(encoding="utf-8")


def test_training_requires_both_reviewed_classes_and_inference_handles_errors(tmp_path: Path) -> None:
    path = tmp_path / "scam-only.csv"
    write_dataset(path, [canonical_row(index, "SCAM") for index in range(3)])
    with pytest.raises(DatasetValidationError, match="both SCAM and LEGITIMATE"):
        train(load_accepted_dataset([path]))
    with pytest.raises(ModelUnavailableError, match="unavailable"):
        load_artifact(tmp_path / "missing.joblib")
    with pytest.raises(ValueError, match="non-blank"):
        predict_message(tmp_path / "missing.joblib", "   ")
