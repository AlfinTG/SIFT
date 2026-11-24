"""Evaluate a saved SIFT model against a separately supplied reviewed dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from ml.classifier import DatasetValidationError, evaluate_pipeline, load_accepted_dataset, load_artifact, write_json, write_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a SIFT model on an independently supplied reviewed CSV.")
    parser.add_argument("dataset", nargs="+", type=Path, help="Canonical accepted CSV files for evaluation")
    parser.add_argument("--artifact", type=Path, default=Path("ml/artifacts/message_classifier.joblib"))
    parser.add_argument("--report", type=Path, default=Path("ml/data/evaluation/external-evaluation.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("ml/data/evaluation/external-evaluation.md"))
    arguments = parser.parse_args()

    dataset = load_accepted_dataset(arguments.dataset)
    artifact = load_artifact(arguments.artifact)
    overlap = set(artifact.get("training_sample_ids", [])) & {row["sample_id"] for row in dataset.rows}
    if overlap:
        raise DatasetValidationError("evaluation dataset overlaps the model training set; use an independent challenge dataset")
    report = evaluate_pipeline(artifact["pipeline"], dataset)
    report["limitations"] = ["This report is only independent if the supplied data was not used for prompt design, training, or threshold selection."]
    write_json(arguments.report, report)
    write_markdown_report(arguments.markdown_report, {"dataset_size": len(dataset.rows), "test": report, "limitations": report["limitations"]})
    print(f"Saved evaluation report: {arguments.report}")
    print(f"Saved human-readable report: {arguments.markdown_report}")


if __name__ == "__main__":
    main()
