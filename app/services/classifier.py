"""Safe local adapter between SIFT analysis and the offline ML artifact."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from ml.classifier import ModelUnavailableError, Prediction, predict_message


MODEL_ARTIFACT_PATH = Path(__file__).resolve().parents[2] / "ml" / "artifacts" / "message_classifier.joblib"
MODEL_SCORE_NAME = "model_score_not_calibrated_probability"


@dataclass(frozen=True)
class MLInferenceResult:
    available: bool
    status: str
    prediction: str | None = None
    score: float | None = None
    score_name: str | None = None
    model_version: str | None = None
    limitation: str = ""


def _validated_prediction(prediction: Prediction) -> MLInferenceResult:
    if prediction.label not in {"SCAM", "LEGITIMATE"}:
        raise ValueError("model returned an unsupported class")
    if not math.isfinite(prediction.score) or not 0.0 <= prediction.score <= 1.0:
        raise ValueError("model returned an out-of-range score")
    return MLInferenceResult(
        available=True,
        status="available",
        prediction=prediction.label,
        score=prediction.score,
        score_name=prediction.score_name or MODEL_SCORE_NAME,
        model_version=MODEL_ARTIFACT_PATH.name,
        limitation="This is an uncalibrated local model score, not a probability or proof that a message is fraudulent.",
    )


def run_ml_inference(message: str, *, artifact_path: Path = MODEL_ARTIFACT_PATH) -> MLInferenceResult:
    """Run local model inference without persisting or transmitting ``message``."""

    if not message.strip():
        return MLInferenceResult(
            available=False,
            status="not_run",
            limitation="No message text was provided for text-model analysis.",
        )
    try:
        return _validated_prediction(predict_message(artifact_path, message))
    except ModelUnavailableError:
        return MLInferenceResult(
            available=False,
            status="unavailable",
            limitation="The local classifier artifact is not available; the rules-only fallback is active.",
        )
    except Exception:  # Inference libraries can raise implementation-specific errors.
        return MLInferenceResult(
            available=False,
            status="error",
            limitation="Local model inference could not be completed; the rules and URL checks remain active.",
        )
