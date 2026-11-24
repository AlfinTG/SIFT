from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.classifier import MLInferenceResult, run_ml_inference
from ml.classifier import Prediction


client = TestClient(app)


def available_scam(_: str) -> MLInferenceResult:
    return MLInferenceResult(True, "available", "SCAM", 0.72, "model_score_not_calibrated_probability", "unit-test.joblib", "Uncalibrated local score.")


def available_legitimate(_: str) -> MLInferenceResult:
    return MLInferenceResult(True, "available", "LEGITIMATE", 0.72, "model_score_not_calibrated_probability", "unit-test.joblib", "Uncalibrated local score.")


def unavailable(_: str) -> MLInferenceResult:
    return MLInferenceResult(False, "unavailable", limitation="No local model artifact.")


def failed(_: str) -> MLInferenceResult:
    return MLInferenceResult(False, "error", limitation="Local inference failed.")


def test_adapter_handles_missing_available_and_failed_artifacts(monkeypatch, tmp_path: Path) -> None:
    assert run_ml_inference("   ").status == "not_run"
    missing = run_ml_inference("hello", artifact_path=tmp_path / "missing.joblib")
    assert missing.status == "unavailable"
    assert missing.prediction is None

    monkeypatch.setattr("app.services.classifier.predict_message", lambda path, message: Prediction("SCAM", 0.8, {"SCAM": 0.8, "LEGITIMATE": 0.2}))
    available = run_ml_inference("pay now", artifact_path=tmp_path / "model.joblib")
    assert available.available is True
    assert available.prediction == "SCAM"
    assert available.score == 0.8

    monkeypatch.setattr("app.services.classifier.predict_message", lambda path, message: (_ for _ in ()).throw(RuntimeError("broken model")))
    failed_result = run_ml_inference("pay now", artifact_path=tmp_path / "model.joblib")
    assert failed_result.status == "error"
    assert failed_result.prediction is None

    monkeypatch.setattr("app.services.classifier.predict_message", lambda path, message: Prediction("SCAM", 1.2, {"SCAM": 1.2}))
    invalid_result = run_ml_inference("pay now", artifact_path=tmp_path / "model.joblib")
    assert invalid_result.status == "error"
    assert invalid_result.prediction is None


def test_rules_remain_stronger_than_legitimate_model(monkeypatch) -> None:
    monkeypatch.setattr("app.services.analyzer.run_ml_inference", available_legitimate)
    response = client.post("/api/analyze", json={"message": "Pay ₹799 registration fee for this internship today."})
    body = response.json()
    assert body["assessment"]["level"] == "high"
    assert body["model"]["prediction"] == "LEGITIMATE"
    assert "rule" in body["assessment"]["contributing_sources"]
    assert not any(signal["source"] == "ml" for signal in body["signals"])


def test_scam_model_is_supporting_signal_not_conclusive(monkeypatch) -> None:
    monkeypatch.setattr("app.services.analyzer.run_ml_inference", available_scam)
    response = client.post("/api/analyze", json={"message": "Hello, please review this when convenient."})
    body = response.json()
    assert body["assessment"]["level"] == "moderate"
    assert body["model"]["score_name"] == "model_score_not_calibrated_probability"
    assert body["model"]["available"] is True
    assert any(signal["signal_id"] == "model_scam_signal" for signal in body["signals"])
    assert body["assessment"]["contributing_sources"] == ["ml"]


def test_strong_rule_and_scam_model_keep_rule_based_risk(monkeypatch) -> None:
    monkeypatch.setattr("app.services.analyzer.run_ml_inference", available_scam)
    response = client.post("/api/analyze", json={"message": "Reply with your OTP immediately or your account will be restricted."})
    body = response.json()
    assert body["assessment"]["level"] == "critical"
    assert {signal["source"] for signal in body["signals"]} >= {"rule", "ml"}


def test_unavailable_or_failed_ml_never_fabricates_prediction(monkeypatch) -> None:
    for inference in (unavailable, failed):
        monkeypatch.setattr("app.services.analyzer.run_ml_inference", inference)
        body = client.post("/api/analyze", json={"message": "A routine message with no strong indicators."}).json()
        assert body["model"]["available"] is False
        assert body["model"]["prediction"] is None
        assert body["model"]["score"] is None
        assert not any(signal["source"] == "ml" for signal in body["signals"])


def test_url_signal_combines_with_scam_model(monkeypatch) -> None:
    monkeypatch.setattr("app.services.analyzer.run_ml_inference", available_scam)
    body = client.post("/api/analyze", json={"message": "Review https://bit.ly/offer"}).json()
    assert body["assessment"]["level"] == "moderate"
    assert set(body["assessment"]["contributing_sources"]) == {"ml", "url"}


def test_frontend_contains_safe_model_rendering() -> None:
    page = client.get("/").text
    script = client.get("/app.js").text
    assert 'id="mlModelDetails"' in page
    assert "model.available" in script
    assert "not a probability or proof" in script
