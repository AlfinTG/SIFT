"""Regression checks for hand-authored demo scenarios, not training data."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


FIXTURES_PATH = Path(__file__).parent / "fixtures" / "demo_scenarios.json"
SCENARIOS = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))["scenarios"]
client = TestClient(app)


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item["scenario_id"])
def test_demo_scenario_matches_documented_expectations(scenario: dict[str, object]) -> None:
    response = client.post("/api/analyze", json={"message": scenario["message"]})

    assert response.status_code == 200
    body = response.json()
    signals = body["signals"]
    assert body["assessment"]["level"] in scenario["expected_risk_levels"]
    assert {signal["signal_id"] for signal in signals} >= set(scenario["expected_signal_ids"])
    assert {signal["source"] for signal in signals} == set(scenario["expected_evidence_categories"])
    assert body["assessment"]["uncertain"] is True
    assert body["model"]["status"] == "unavailable"
    assert body["model"]["label"] is None
    assert body["model"]["score"] is None
