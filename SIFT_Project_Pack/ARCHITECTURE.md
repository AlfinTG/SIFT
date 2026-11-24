# SIFT — Proposed Technical Architecture

**Status:** Recommended baseline; major stack decisions remain subject to user approval.

## 1. Design goals

- Build one reliable end-to-end flow quickly.
- Keep all core analysis local.
- Separate model inference, deterministic rules, URL parsing, evidence fusion, and presentation.
- Avoid external API dependencies in the live scan path.
- Keep memory and CPU use modest.

## 2. Proposed architecture

```text
Browser UI (local)
      |
      | POST /api/analyze
      v
FastAPI application (local)
      |
      +--> Input validation + URL extraction
      |
      +--> ML classifier (scikit-learn pipeline)
      |
      +--> Contextual safety rule engine
      |
      +--> URL structural inspector (no network visit)
      |
      +--> Evidence fusion + uncertainty handling
      |
      v
Structured analysis response
      |
      v
UI: risk summary + Evidence Trail + safe next steps
```

## 3. Proposed stack

| Layer | Recommended option | Why |
|---|---|---|
| UI | HTML, CSS, JavaScript | Fast to build, no complex frontend build chain required |
| Local API | Python + FastAPI | Simple typed HTTP boundary for model inference |
| ML | scikit-learn | Lightweight, CPU-friendly, inspectable baseline |
| Text features | TF-IDF word + character n-grams | Useful for message text, spelling variation, and obfuscation patterns |
| Classifier | Logistic Regression | Fast baseline, easy to evaluate and serialize |
| Model artifact | joblib | Store the fitted preprocessing + classifier pipeline |
| URL parsing | Python standard library (`urllib.parse`) plus careful validation | Avoid a third-party dependency if not needed |
| Tests | pytest + small deterministic test fixtures | Repeatable engine and API checks |

Confirm package/Python-version compatibility before installing or pinning versions. The user's development environment is Windows; commands should be given for PowerShell unless the user says otherwise.

## 4. Suggested project structure

```text
sift/
├── app/
│   ├── main.py                 # FastAPI entry point and static UI hosting
│   ├── api/                    # Request/response routes
│   ├── schemas/                # Pydantic request/response models
│   ├── services/
│   │   ├── classifier.py       # Load and call the fitted ML pipeline
│   │   ├── rules.py            # Contextual safety rules
│   │   ├── url_inspector.py    # Local URL parsing and structural signals
│   │   ├── analyzer.py         # Orchestration and evidence fusion
│   │   └── guidance.py         # Safe next-step mapping
│   └── data/
│       └── patterns.json       # Educational pattern library content
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── ml/
│   ├── data/
│   │   ├── raw/                # Imported datasets; never commit secrets or user PII
│   │   ├── processed/
│   │   └── evaluation/
│   ├── prepare_dataset.py
│   ├── train.py
│   ├── evaluate.py
│   └── artifacts/
│       └── message_classifier.joblib
├── tests/
│   ├── test_rules.py
│   ├── test_urls.py
│   ├── test_classifier.py
│   ├── test_api.py
│   └── fixtures/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

This is a proposed structure, not an existing codebase. Do not generate every file in advance if a smaller vertical slice is enough.

## 5. Request/response contract (conceptual)

### Request

```json
{
  "message": "Text pasted by the user",
  "include_url_inspection": true
}
```

### Response

```json
{
  "assessment": {
    "level": "high",
    "summary": "Several warning signs were detected.",
    "uncertain": false
  },
  "model": {
    "label": "SCAM",
    "score": 0.83,
    "score_name": "model_score_not_calibrated_probability"
  },
  "signals": [
    {
      "source": "rule",
      "signal_id": "upfront_job_fee",
      "evidence": "Pay ₹799 to confirm your internship",
      "reason": "A fee is being demanded to secure an employment opportunity.",
      "severity": "high",
      "recommended_action": "Do not pay; verify the employer independently."
    }
  ],
  "urls": [],
  "limitations": [
    "SIFT has not verified the sender's identity or any website reputation."
  ],
  "next_steps": []
}
```

The example is a contract illustration only. The numeric value is not a performance claim and must not be displayed as a fraud probability unless properly calibrated.

## 6. Analysis orchestration

1. Validate the request.
2. Preserve the original message for display; create a normalized copy for analysis.
3. Extract candidate URLs without opening them.
4. Run ML classification.
5. Run contextual rules independently.
6. Inspect URLs locally.
7. Convert all signals into a consistent evidence object.
8. Fuse evidence into a cautious risk level.
9. If outputs conflict or the model is uncertain, avoid a confident “safe” verdict.
10. Attach guidance based on actual signals and the user's selected incident state.

## 7. Risk fusion principles

- A high-severity explicit request for an OTP, PIN, password, or upfront payment may outweigh a low model score.
- A model score alone should not create a “Critical” result.
- A suspicious URL structure can raise concern but cannot prove the destination is malicious.
- Lack of findings must never be phrased as verification.
- Keep the scoring logic deterministic, documented, and covered by tests.

## 8. Local/offline behavior

- The UI and API should be served locally, preferably from the same FastAPI app to avoid unnecessary CORS setup.
- No live scan should send content to a third-party service.
- URL inspection must not make HTTP requests to the destination.
- Adaption API credentials are used only from a separate, local dataset-generation workflow; they must never be exposed to the browser.
- Verify offline operation by disconnecting the internet after setup and testing the core app.

## 9. Fallbacks

- If the classifier artifact is missing, show a clearly marked rules-only fallback; never silently pretend ML ran.
- If URL parsing fails, return a safe error for that URL and continue the message scan.
- If the API is unavailable, show a useful UI error and launch instructions.
