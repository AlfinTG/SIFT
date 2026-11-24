# SIFT

SIFT is a local, explainable scam-message and suspicious-URL analysis platform.

## Current status

The project currently includes a local, rules-only analysis slice:

- A FastAPI `POST /api/analyze` endpoint with validated message/URL input.
- Contextual safety rules for credential disclosure, upfront job fees, payment/refund manipulation, account pressure, reward-fee bait, and urgency.
- Local URL-structure inspection only. It does not open URLs, follow redirects, perform DNS lookups, or use reputation services.
- An Evidence Trail UI with safe next-step guidance selected by the incident status.

The ML classifier is **not installed yet**. The app explicitly labels this as a rules-only fallback rather than presenting a model result.

The latest dataset execution found that all eligible candidates still require
attributable human review, so training remains intentionally blocked. See the
[ML execution report](docs/ML_EXECUTION_REPORT.md) for the audited counts,
review package, integration verification, and next gate.

## Local setup

Use Python 3.11 or newer. From PowerShell in this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` in a browser. The health endpoint is available at `http://127.0.0.1:8000/api/health`.

## Current API example

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/analyze -ContentType 'application/json' -Body '{"message":"Pay ₹799 as a registration fee to confirm your internship today."}'
```

The response is a cautious assessment, evidence objects, local URL inspection results, known limitations, and safe next steps. It is not a fraud probability or verification of a sender or website.

The frontend integration contract, request/response examples, error behavior, and rendering guidance are in [`docs/API.md`](docs/API.md). Reusable demo and regression scenarios are in `tests/fixtures/demo_scenarios.json`; they are not training data.

### Input limits and validation

- `message`: up to 10,000 characters.
- `url`: up to 2,048 characters and must be a complete HTTP or HTTPS URL to be structurally inspected.
- A request must contain a non-blank message, URL, or both. Invalid request bodies return HTTP `422` with validation details.

These limits support long pasted messages while preventing unbounded local processing. An accepted URL that cannot be parsed safely is returned as a per-URL inspection error, allowing the message analysis to continue.

## Dataset conversion (offline)

When an Adaption export is ready, preserve the untouched JSONL or CSV under `ml/data/raw/` and convert it locally:

```powershell
python -m ml.prepare_dataset ml/data/raw/sift-pilot-v2-scam-40.jsonl --output-directory ml/data/processed/sift-pilot-v2-scam-40 --source-batch sift-pilot-v2-scam-40 --generation-prompt-version sift-pilot-v2
```

The converter accepts JSONL objects or Adaption CSV rows. Both formats require an `enhanced_prompt`, `prompt`, or `original_prompt` string with the required message delimiters plus an `enhanced_completion`, `completion`, `output`, or `response` JSON object/string; a strictly fenced JSON completion is also accepted. It extracts only the message, validates completion JSON and exact evidence quotes, separates `AMBIGUOUS` rows, records rejected rows with a reason, and rejects exact duplicate messages. Every converted row remains `unreviewed`.

For the current candidate set, use the consolidated review ledger (the v3 SCAM
batch plus the LEGITIMATE batch):

```powershell
python -m ml.consolidate_review ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv --raw "ml/data/raw/SIFT sift-pilot-v2 LEGITIMATE 40.csv" "ml/data/raw/SIFT pilot v3 SCAM fake_job structural validation batch.csv" "ml/data/raw/SIFT sift-pilot-v2 SCAM 40.csv" "ml/data/raw/SIFT sift-pilot-v2 SCAM 40_1.csv" --audit ml/data/review/consolidated-audit.json --ledger ml/data/review/consolidated-review-ledger.csv --package ml/data/review/consolidated-human-review-package.md
```

After human reviewers have completed the ledger, derive—without overwriting the converter output—a traceable accepted export:

```powershell
python -m ml.dataset_review ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv --manifest ml/pilot_manifest.json --review-ledger-input ml/data/review/consolidated-review-ledger.csv --report ml/data/review/final-review-report.json --accepted-output ml/data/review/accepted-reviewed.csv
```

The derived export carries the accepted decision, reviewer ID, and review time.
The release training and validation commands reject an `accepted` CSV that
lacks this traceability; editing `review_status` alone is not a valid approval.

An accepted ledger decision requires a reviewer ID and ISO 8601 review time. `ml/data/` is ignored by Git, so raw exports and derived data are not accidentally committed.

Run the focused tests with:

```powershell
python -m pytest
```

## Offline ML baseline

The training pipeline is local-only and does not call the API or retain submitted messages. It accepts canonical CSV files, uses only rows whose `review_status` is `accepted` and whose label is `SCAM` or `LEGITIMATE`, and uses only `message_text` as a model feature. `AMBIGUOUS`, rejected, and unreviewed rows are excluded.

Train after both reviewed class exports are available:

```powershell
python -m ml.train ml/data/review/accepted-reviewed.csv --artifact ml/artifacts/message_classifier.joblib --report ml/data/evaluation/training-report.json
```

The trainer uses group-aware train/validation/test splits based on `template_family`; it fails rather than silently creating a leaking or one-class split. The report contains SCAM precision, recall, F1, a confusion matrix, false-positive/false-negative counts, split IDs, and limitations. It does not describe scores as calibrated probabilities.

Evaluate a saved model only on a separately reviewed challenge CSV whose sample IDs do not overlap training IDs:

```powershell
python -m ml.evaluate ml/data/evaluation/independent-challenge.csv --artifact ml/artifacts/message_classifier.joblib --report ml/data/evaluation/external-evaluation.json
```

Validate input before fitting, or smoke-test a saved model locally:

```powershell
python -m ml.validate_dataset ml/data/review/accepted-reviewed.csv
python -m ml.predict "Pay a registration fee today to secure your internship." --artifact ml/artifacts/message_classifier.joblib
```

Models and evaluation files stay under Git-ignored `ml/artifacts/` and `ml/data/evaluation/` directories.

## Hybrid local analysis

`POST /api/analyze` now checks for `ml/artifacts/message_classifier.joblib` locally. If present and readable, the API returns an additional ML prediction and bounded uncalibrated model score; a SCAM prediction adds a supporting medium-severity signal. Existing deterministic rules and URL inspection remain independent: explicit credential/payment rules are never overridden by a model prediction, and a model alone cannot create a critical verdict.

If the artifact is missing or inference fails, the API remains usable in clearly marked rules-only fallback mode, with no fabricated prediction or score. After training reviewed SCAM and LEGITIMATE data, place the artifact at the default path and restart the server:

```powershell
python -m ml.train <reviewed-scam.csv> <reviewed-legitimate.csv> --artifact ml/artifacts/message_classifier.joblib
python -m pytest tests/test_ml_integration.py -q
python -m uvicorn app.main:app --reload
```

Model input stays local and is not persisted or sent to external services. See [`docs/API.md`](docs/API.md) for the full ML response contract and limitations.

## Demo runbook

Start SIFT with:

```powershell
python -m pytest -q
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/`. For a concise demo, use the built-in fake internship scenario, the UPI refund/PIN scenario, the shortened-URL scenario, and the legitimate OTP safety reminder. Explain that SIFT shows indicators and safe next steps, not a verdict of verified safety. The ML panel stays correctly unavailable until a reviewed model artifact exists.

Core analysis will remain local. SIFT will not open submitted URLs, perform live reputation checks, or store raw submitted messages by default.
