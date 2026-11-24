from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_fake_internship_fee_has_visible_evidence() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "message": "Congratulations, you are shortlisted for an internship. Pay ₹799 as a registration fee today to confirm your seat.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["assessment"]["level"] == "high"
    assert any(signal["signal_id"] == "upfront_job_fee" for signal in body["signals"])
    assert body["model"]["status"] == "unavailable"


def test_response_contract_contains_frontend_rendering_fields() -> None:
    response = client.post(
        "/api/analyze",
        json={"message": "Please review https://bit.ly/offer before continuing."},
    )

    assert response.status_code == 200
    body = response.json()
    assert {"assessment", "model", "signals", "urls", "limitations", "next_steps"} <= body.keys()
    assert {"level", "summary", "uncertain"} <= body["assessment"].keys()
    assert {"status", "label", "score", "score_name", "limitation"} <= body["model"].keys()
    assert any(signal["source"] == "url" for signal in body["signals"])
    assert body["urls"]
    assert body["limitations"]
    assert body["next_steps"]


def test_benign_otp_warning_is_not_a_credential_request() -> None:
    response = client.post(
        "/api/analyze",
        json={"message": "Security reminder: Never share your OTP, password, or UPI PIN with anyone."},
    )

    assert response.status_code == 200
    signal_ids = {signal["signal_id"] for signal in response.json()["signals"]}
    assert "credential_disclosure_request" not in signal_ids
    assert response.json()["assessment"]["level"] == "low_indicators"


def test_url_inspection_is_structural_and_flags_ip_host() -> None:
    response = client.post("/api/analyze", json={"url": "https://198.51.100.7/login"})

    assert response.status_code == 200
    body = response.json()
    assert body["urls"][0]["host"] == "198.51.100.7"
    signal_ids = {signal["signal_id"] for signal in body["signals"]}
    assert "ip_address_host" in signal_ids
    assert "deep_subdomain_structure" not in signal_ids


def test_empty_request_returns_validation_error() -> None:
    response = client.post("/api/analyze", json={"message": "   "})

    assert response.status_code == 422


def test_non_string_message_is_rejected() -> None:
    response = client.post("/api/analyze", json={"message": ["not", "text"]})

    assert response.status_code == 422


def test_message_limit_is_enforced() -> None:
    response = client.post("/api/analyze", json={"message": "x" * 10_001})

    assert response.status_code == 422
    assert any(error["type"] == "string_too_long" for error in response.json()["detail"])


def test_url_limit_is_enforced() -> None:
    response = client.post("/api/analyze", json={"url": f"https://example.com/{'x' * 2_100}"})

    assert response.status_code == 422
    assert any(error["type"] == "string_too_long" for error in response.json()["detail"])


def test_malformed_direct_url_returns_safe_url_error() -> None:
    response = client.post("/api/analyze", json={"url": "https://[invalid"})

    assert response.status_code == 200
    assert response.json()["urls"][0]["valid"] is False
    assert response.json()["urls"][0]["error"]


def test_critical_rule_outweighs_other_conflicting_indicators() -> None:
    response = client.post(
        "/api/analyze",
        json={"message": "Never share your OTP. Reply with your OTP immediately or your account will be restricted today."},
    )

    body = response.json()
    assert body["assessment"]["level"] == "critical"
    assert {signal["signal_id"] for signal in body["signals"]} >= {
        "credential_disclosure_request",
        "account_pressure",
        "urgency_pressure",
    }
