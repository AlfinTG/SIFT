"""Command-line entry point for the offline SIFT baseline trainer."""

from __future__ import annotations

import argparse
from pathlib import Path

from ml.classifier import load_accepted_dataset, save_artifact, train, write_json, write_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train SIFT's offline TF-IDF Logistic Regression baseline.")
    parser.add_argument("datasets", nargs="+", type=Path, help="Canonical CSV files containing reviewed data")
    parser.add_argument("--artifact", type=Path, default=Path("ml/artifacts/message_classifier.joblib"))
    parser.add_argument("--report", type=Path, default=Path("ml/data/evaluation/training-report.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("ml/data/evaluation/training-report.md"))
    parser.add_argument("--random-state", type=int, default=42)
    arguments = parser.parse_args()

    # Command-line training is a release operation, so require a derived export
    # carrying the reviewer decision, identity, and timestamp.  The lower-level
    # loader remains usable in unit tests and exploratory notebooks.
    dataset = load_accepted_dataset(arguments.datasets, require_review_traceability=True)
    pipeline, splits, report = train(dataset, random_state=arguments.random_state)
    save_artifact(arguments.artifact, pipeline, training_sample_ids=[row["sample_id"] for row in splits.train.rows])
    write_json(arguments.report, report)
    write_markdown_report(arguments.markdown_report, report)
    print(f"Saved model artifact: {arguments.artifact}")
    print(f"Saved evaluation report: {arguments.report}")
    print(f"Saved human-readable report: {arguments.markdown_report}")


if __name__ == "__main__":
    main()
