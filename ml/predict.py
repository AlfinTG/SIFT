"""Local command-line smoke test for a saved SIFT model artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.classifier import predict_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local inference with a saved SIFT model.")
    parser.add_argument("message", help="Message text to classify locally")
    parser.add_argument("--artifact", type=Path, default=Path("ml/artifacts/message_classifier.joblib"))
    arguments = parser.parse_args()
    prediction = predict_message(arguments.artifact, arguments.message)
    print(json.dumps(prediction.__dict__, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
