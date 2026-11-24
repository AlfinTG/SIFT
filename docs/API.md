# SIFT API contract

SIFT exposes a local-only analysis API. It does not retain submitted message content, open submitted URLs, follow redirects, query DNS, or call reputation services.

## Start locally

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Check it with `GET /api/health`.

## Analyze content

`POST /api/analyze`

### Request body

| Field | Type | Required | Details |
| --- | --- | --- | --- |
| `message` | string | No | Up to 10,000 characters. A non-blank `message` or `url` is required. |
| `url` | string or null | No | Up to 2,048 characters. It is structurally parsed only when URL inspection is enabled. |
| `include_url_inspection` | boolean | No | Defaults to `true`. Set to `false` to skip extraction and inspection. |
| `incident_status` | string | No | Defaults to `received_only`. Allowed values: `received_only`, `clicked_link`, `shared_personal_data`, `shared_credentials`, `made_payment`. |

Example request:

```json
{
  "message": "Congratulations, you are shortlisted for an internship. Pay ₹799 as a registration fee today to confirm your seat.",
  "incident_status": "received_only"
}
```

### Response body

| Field | Type | Frontend use |
| --- | --- | --- |
| `assessment.level` | `low_indicators` \| `moderate` \| `high` \| `critical` | Overall risk level. It is not a fraud probability. |
| `assessment.summary` | string | Risk summary. |
| `assessment.uncertain` | boolean | Always render the result as uncertain; SIFT does not verify safety. |
| `assessment.contributing_sources` | array | Signal sources that contributed to the overall assessment. |
| `model.available` | boolean | Whether a local model prediction was produced for this request. |
| `model.status` | `available` | `unavailable` | `error` | `not_run` | Local ML inference state. |
| `model.prediction` | `SCAM` | `LEGITIMATE` | null | Prediction only when `available` is true; never fabricated in fallback mode. |
| `model.score`, `model.score_name` | number/null, fixed descriptor/null | An uncalibrated model score, never a fraud probability. |
| `model.model_version` | string/null | Local artifact filename when inference succeeds. |
| `model.limitation`, `model.limitations` | string, array | Scope and failure/fallback explanations. |
| `signals` | array | Unified evidence trail. Filter by `source`: `rule` for rule-engine findings and `url` for URL-structure findings. |
| `signals[].evidence` | string | Exact evidence snippet for display. |
| `signals[].reason` | string | Plain-language explanation. |
| `signals[].recommended_action` | string | Safe recommended action for that finding. |
| `urls` | array | One local structural inspection per supplied/extracted HTTP(S) URL. A valid inspection has `host`, `scheme`, and `signals`; an invalid one has `valid: false` and `error`. |
| `limitations` | array of strings | Mandatory scope and safety caveats. |
| `next_steps` | array of strings | Incident-aware safe actions. |

Rule and URL engines remain independent. A SCAM ML prediction adds only a medium-severity supporting signal; it cannot create a critical assessment or override explicit deterministic rule evidence. A LEGITIMATE ML prediction does not suppress rule or URL evidence.

Actual response for the example request:

```json
{
  "assessment": {
    "level": "high",
    "summary": "Several warning signs or a high-concern indicator were detected.",
    "uncertain": true,
    "contributing_sources": ["rule"]
  },
  "model": {
    "available": false,
    "status": "unavailable",
    "label": null,
    "prediction": null,
    "score": null,
    "score_name": null,
    "model_version": null,
    "limitation": "The local classifier artifact is not available; the rules-only fallback is active.",
    "limitations": ["The local classifier artifact is not available; the rules-only fallback is active."]
  },
  "signals": [
    {
      "source": "rule",
      "signal_id": "upfront_job_fee",
      "evidence": "Pay ₹799 as a registration fee",
      "reason": "A payment appears to be required in connection with an employment opportunity, which is a strong warning sign.",
      "severity": "high",
      "recommended_action": "Do not pay. Verify the employer through an independently found official channel."
    },
    {
      "source": "rule",
      "signal_id": "urgency_pressure",
      "evidence": "today",
      "reason": "The message creates time pressure, which can discourage careful verification.",
      "severity": "low",
      "recommended_action": "Take time to verify the claim through a trusted, independently found channel."
    }
  ],
  "urls": [],
  "limitations": [
    "The ML classifier is not installed in this rules-only foundation; results do not include a model prediction.",
    "SIFT has not verified the sender's identity, domain ownership, website reputation, page contents, or whether a claimed event is real.",
    "URL inspection is local structural parsing only. SIFT does not open URLs, follow redirects, perform DNS lookups, or use live reputation checks.",
    "A low-indicator result does not mean a message or website is safe or verified."
  ],
  "next_steps": [
    "Do not reply, pay, scan a QR code, or open the link from the message.",
    "Verify the claim through an official app, website, or contact method you find independently."
  ]
}
```

### Error responses

Validation errors return `422 Unprocessable Entity` with FastAPI's `detail` array. For example, a blank message with no URL returns:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Value error, Provide a message or URL to analyze.",
      "input": {"message": "   "},
      "ctx": {"error": {}}
    }
  ]
}
```

Messages over 10,000 characters, URLs over 2,048 characters, unsupported field types, and invalid `incident_status` values also return `422`.

## Frontend integration

1. Submit the current form values to `/api/analyze` as JSON.
2. Render `assessment.level`, `assessment.summary`, and the uncertainty notice first.
3. Show ML status from `model`. Show prediction/score only when `model.available` is true, and label the score as uncalibrated—not a probability or proof.
4. Split `signals` by `source` to render rule findings separately from URL findings. Render each evidence snippet, reason, severity, and recommended action.
5. Render `urls` separately, including per-URL parse errors. Do not attempt to open URLs to enrich the result.
6. Always render `next_steps` and `limitations`, including on `low_indicators` results.

For reusable demo content and expected outputs, see `tests/fixtures/demo_scenarios.json`. Those fixtures are regression/demo material only, not training data.

## ML activation and safety

The adapter looks only for `ml/artifacts/message_classifier.joblib` and runs it locally through `ml.classifier.predict_message`; it never sends a scanned message to another service or stores it. Missing or unreadable artifacts return a rules-only response with no prediction. Train the reviewed dataset first, then start/restart the API:

```powershell
python -m ml.train <reviewed-scam.csv> <reviewed-legitimate.csv> --artifact ml/artifacts/message_classifier.joblib
python -m pytest tests/test_ml_integration.py -q
python -m uvicorn app.main:app --reload
```
