"""Local, offline training and inference utilities for SIFT's text baseline."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import FeatureUnion, Pipeline


TRAINING_LABELS = {"SCAM", "LEGITIMATE"}
CANONICAL_FIELDS = {
    "sample_id", "message_text", "label", "scam_type", "language", "channel", "tactics",
    "evidence_quotes", "rationale", "difficulty", "source", "source_batch",
    "generation_prompt_version", "template_family", "review_status",
}
ARTIFACT_VERSION = 2
REVIEW_TRACE_FIELDS = {"review_decision", "reviewer_id", "reviewed_at"}


class DatasetValidationError(ValueError):
    """Raised when a reviewed dataset cannot safely support the requested operation."""


class ModelUnavailableError(RuntimeError):
    """Raised when an inference artifact is unavailable or incompatible."""


@dataclass(frozen=True)
class Dataset:
    rows: list[dict[str, str]]

    @property
    def messages(self) -> list[str]:
        return [row["message_text"] for row in self.rows]

    @property
    def labels(self) -> list[str]:
        return [row["label"] for row in self.rows]

    @property
    def groups(self) -> list[str]:
        return [row["template_family"] or row["sample_id"] for row in self.rows]


@dataclass(frozen=True)
class DatasetSplits:
    train: Dataset
    validation: Dataset
    test: Dataset


@dataclass(frozen=True)
class Prediction:
    label: str
    score: float
    scores: dict[str, float]
    score_name: str = "model_score_not_calibrated_probability"


def load_accepted_dataset(paths: Iterable[Path], *, require_review_traceability: bool = False) -> Dataset:
    """Load only human-accepted binary rows from canonical CSV exports.

    Metadata is validated for schema integrity but is never exposed to the model.
    """

    rows: list[dict[str, str]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None or not CANONICAL_FIELDS <= set(reader.fieldnames):
                raise DatasetValidationError(f"{path} is missing canonical dataset fields")
            if require_review_traceability and not REVIEW_TRACE_FIELDS <= set(reader.fieldnames):
                raise DatasetValidationError(
                    f"{path} is missing review traceability fields; derive it from a completed review ledger before training"
                )
            for row_number, row in enumerate(reader, start=2):
                if not row.get("sample_id", "").strip() or not row.get("message_text", "").strip():
                    raise DatasetValidationError(f"{path}:{row_number} has a blank sample_id or message_text")
                label = row.get("label", "").strip().upper()
                status = row.get("review_status", "").strip()
                if label not in {"SCAM", "LEGITIMATE", "AMBIGUOUS"}:
                    raise DatasetValidationError(f"{path}:{row_number} has an invalid label")
                if status == "accepted" and label in TRAINING_LABELS:
                    if require_review_traceability:
                        if row.get("review_decision", "").strip() != "accepted":
                            raise DatasetValidationError(f"{path}:{row_number} is accepted without an accepted review decision")
                        if not row.get("reviewer_id", "").strip() or not row.get("reviewed_at", "").strip():
                            raise DatasetValidationError(f"{path}:{row_number} is accepted without reviewer traceability")
                        try:
                            datetime.fromisoformat(row["reviewed_at"].strip().replace("Z", "+00:00"))
                        except ValueError as error:
                            raise DatasetValidationError(f"{path}:{row_number} has a non-ISO review timestamp") from error
                    normalised = dict(row)
                    normalised["label"] = label
                    rows.append(normalised)
    duplicate_ids = [sample_id for sample_id, count in Counter(row["sample_id"] for row in rows).items() if count > 1]
    if duplicate_ids:
        raise DatasetValidationError("accepted input contains duplicate sample_id values")
    if not rows:
        raise DatasetValidationError("no accepted SCAM or LEGITIMATE rows were found")
    return Dataset(rows)


def validate_trainable_dataset(dataset: Dataset) -> None:
    distribution = Counter(dataset.labels)
    if set(distribution) != TRAINING_LABELS:
        raise DatasetValidationError("training requires accepted rows from both SCAM and LEGITIMATE classes")
    if min(distribution.values()) < 3:
        raise DatasetValidationError("training requires at least three accepted rows per class for grouped train/validation/test splits")
    groups_by_label: dict[str, set[str]] = {label: set() for label in TRAINING_LABELS}
    for row in dataset.rows:
        groups_by_label[row["label"]].add(row["template_family"] or row["sample_id"])
    if min(len(groups) for groups in groups_by_label.values()) < 3:
        raise DatasetValidationError("training requires at least three template families per class to avoid group leakage")


def _subset(dataset: Dataset, indices: list[int]) -> Dataset:
    return Dataset([dataset.rows[index] for index in indices])


def _has_both_classes(dataset: Dataset) -> bool:
    return set(dataset.labels) == TRAINING_LABELS


def split_dataset(dataset: Dataset, *, random_state: int = 42) -> DatasetSplits:
    """Create reproducible 70/15/15 group-aware splits or fail clearly."""

    validate_trainable_dataset(dataset)
    indices = list(range(len(dataset.rows)))
    for seed in range(random_state, random_state + 100):
        first = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
        train_indices, holdout_indices = next(first.split(indices, dataset.labels, dataset.groups))
        train = _subset(dataset, train_indices.tolist())
        holdout = _subset(dataset, holdout_indices.tolist())
        if not (_has_both_classes(train) and _has_both_classes(holdout)):
            continue
        holdout_groups = holdout.groups
        second = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=seed)
        validation_relative, test_relative = next(second.split(list(range(len(holdout.rows))), holdout.labels, holdout_groups))
        validation = _subset(holdout, validation_relative.tolist())
        test = _subset(holdout, test_relative.tolist())
        if _has_both_classes(validation) and _has_both_classes(test):
            split_groups = [set(part.groups) for part in (train, validation, test)]
            if not (split_groups[0] & split_groups[1] or split_groups[0] & split_groups[2] or split_groups[1] & split_groups[2]):
                return DatasetSplits(train, validation, test)
    raise DatasetValidationError("could not create group-aware train/validation/test splits containing both classes; collect more diverse template families")


def build_pipeline() -> Pipeline:
    """Build the deliberately small, inspectable baseline without metadata features."""

    features = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
        ("character_tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)),
    ])
    return Pipeline([("features", features), ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))])


def evaluate_pipeline(pipeline: Pipeline, dataset: Dataset) -> dict[str, Any]:
    if not dataset.rows:
        raise DatasetValidationError("cannot evaluate an empty dataset")
    predictions = pipeline.predict(dataset.messages)
    precision, recall, f1, _ = precision_recall_fscore_support(dataset.labels, predictions, labels=["SCAM"], average=None, zero_division=0)
    matrix = confusion_matrix(dataset.labels, predictions, labels=["LEGITIMATE", "SCAM"]).tolist()
    false_positive_count = sum(actual == "LEGITIMATE" and predicted == "SCAM" for actual, predicted in zip(dataset.labels, predictions))
    false_negative_count = sum(actual == "SCAM" and predicted == "LEGITIMATE" for actual, predicted in zip(dataset.labels, predictions))
    return {
        "row_count": len(dataset.rows),
        "class_distribution": dict(Counter(dataset.labels)),
        "scam_precision": float(precision[0]),
        "scam_recall": float(recall[0]),
        "scam_f1": float(f1[0]),
        "confusion_matrix_labels": ["LEGITIMATE", "SCAM"],
        "confusion_matrix": matrix,
        "false_positive_count": false_positive_count,
        "false_negative_count": false_negative_count,
        "classification_report": classification_report(dataset.labels, predictions, labels=["LEGITIMATE", "SCAM"], output_dict=True, zero_division=0),
    }


def train(dataset: Dataset, *, random_state: int = 42) -> tuple[Pipeline, DatasetSplits, dict[str, Any]]:
    splits = split_dataset(dataset, random_state=random_state)
    pipeline = build_pipeline()
    pipeline.fit(splits.train.messages, splits.train.labels)
    report = {
        "dataset_size": len(dataset.rows),
        "class_distribution": dict(Counter(dataset.labels)),
        "split_counts": {"train": len(splits.train.rows), "validation": len(splits.validation.rows), "test": len(splits.test.rows)},
        "validation": evaluate_pipeline(pipeline, splits.validation),
        "test": evaluate_pipeline(pipeline, splits.test),
        "threshold_analysis": {
            "decision_rule": "highest uncalibrated class score",
            "selected_threshold": None,
            "limitation": "No operating threshold is selected from this pilot; select any future uncertainty threshold using validation data only.",
        },
        "limitations": [
            "Model scores are not calibrated probabilities.",
            "The held-out test set is group-separated but is not an independent real-world benchmark.",
            "Synthetic-only evaluation must not be described as real-world accuracy.",
        ],
        "split_sample_ids": {"train": [row["sample_id"] for row in splits.train.rows], "validation": [row["sample_id"] for row in splits.validation.rows], "test": [row["sample_id"] for row in splits.test.rows]},
    }
    return pipeline, splits, report


def save_artifact(path: Path, pipeline: Pipeline, *, training_sample_ids: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"artifact_version": ARTIFACT_VERSION, "pipeline": pipeline, "training_sample_ids": list(training_sample_ids), "created_at": datetime.now(timezone.utc).isoformat()}, path)


def load_artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ModelUnavailableError(f"model artifact is unavailable: {path}")
    try:
        artifact = joblib.load(path)
    except Exception as error:  # joblib may raise implementation-specific exceptions.
        raise ModelUnavailableError(f"could not load model artifact: {error}") from error
    if not isinstance(artifact, dict) or artifact.get("artifact_version") != ARTIFACT_VERSION or "pipeline" not in artifact:
        raise ModelUnavailableError("model artifact has an unsupported format")
    return artifact


def predict_message(artifact_path: Path, message_text: str) -> Prediction:
    if not isinstance(message_text, str) or not message_text.strip():
        raise ValueError("message_text must be a non-blank string")
    pipeline = load_artifact(artifact_path)["pipeline"]
    probabilities = pipeline.predict_proba([message_text])[0]
    classes = pipeline.named_steps["classifier"].classes_
    scores = {str(label): float(score) for label, score in zip(classes, probabilities)}
    label = max(scores, key=scores.__getitem__)
    return Prediction(label=label, score=scores[label], scores=scores)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    """Write a concise companion report without inventing an interpretation of metrics."""

    test = report.get("test", {})
    lines = [
        "# SIFT model evaluation",
        "",
        f"- Dataset rows: {report.get('dataset_size', test.get('row_count', 'unknown'))}",
        f"- Split counts: {report.get('split_counts', 'external evaluation')}",
        f"- SCAM precision: {test.get('scam_precision', 'not available')}",
        f"- SCAM recall: {test.get('scam_recall', 'not available')}",
        f"- SCAM F1: {test.get('scam_f1', 'not available')}",
        f"- False positives: {test.get('false_positive_count', 'not available')}",
        f"- False negatives: {test.get('false_negative_count', 'not available')}",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report.get("limitations", [])],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
