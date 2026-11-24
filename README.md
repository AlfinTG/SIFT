# SIFT

SIFT is a local, explainable scam-message and suspicious-URL analysis platform.

## Current status

The project currently includes a local, rules-only analysis slice:

- A FastAPI `POST /api/analyze` endpoint with validated message/URL input.
- Contextual safety rules for credential disclosure, upfront job fees, payment/refund manipulation, account pressure, reward-fee bait, and urgency.
- Local URL-structure inspection only. It does not open URLs, follow redirects, perform DNS lookups, or use reputation services.
- An Evidence Trail UI with safe next-step guidance selected by the incident status.

The ML classifier is **not installed yet**. The app explicitly labels this as a rules-only fallback rather than presenting a model result.

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

When a reviewed Adaption pilot has been exported as JSONL, preserve the untouched export under `ml/data/raw/` and convert it locally:

```powershell
python -m ml.prepare_dataset ml/data/raw/pilot.jsonl --output-directory ml/data/processed/pilot-v1 --source-batch pilot-v1 --generation-prompt-version v1
```

The converter extracts only text between the required message delimiters, validates completion JSON and exact evidence quotes, separates `AMBIGUOUS` rows, records rejected rows with a reason, and rejects exact duplicate messages. The accepted rows remain `unreviewed` and must be audited before any model training.

Run the focused tests with:

```powershell
python -m pytest
```

Core analysis will remain local. SIFT will not open submitted URLs, perform live reputation checks, or store raw submitted messages by default.
