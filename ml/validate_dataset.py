"""Validate reviewed canonical CSV data before training without fitting a model."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from ml.classifier import load_accepted_dataset, validate_trainable_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SIFT canonical training CSVs.")
    parser.add_argument("datasets", nargs="+", type=Path)
    arguments = parser.parse_args()
    dataset = load_accepted_dataset(arguments.datasets, require_review_traceability=True)
    validate_trainable_dataset(dataset)
    print(f"Validated {len(dataset.rows)} accepted training rows: {dict(Counter(dataset.labels))}")


if __name__ == "__main__":
    main()
