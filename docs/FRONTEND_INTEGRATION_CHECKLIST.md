# Frontend integration checklist

Use this checklist when connecting the Antigravity implementation to the frozen SIFT backend. The frontend must not describe a result as verified safe or as an ML prediction.

## 1. Start and verify the backend

- [ ] From the project root, create/activate the virtual environment and install `requirements.txt`.
- [ ] Start the service: `python -m uvicorn app.main:app --reload`.
- [ ] Confirm `GET http://127.0.0.1:8000/api/health` returns `{"status":"ok","service":"sift"}`.
- [ ] Use `POST http://127.0.0.1:8000/api/analyze` for scans.

## 2. Send the request

Use JSON. `message` and `url` are optional individually, but at least one must be non-blank.

```json
{
  "message": "Congratulations, you are shortlisted for an internship. Pay ₹799 as a registration fee today to confirm your seat.",
  "url": null,
  "include_url_inspection": true,
  "incident_status": "received_only"
}
```

- [ ] Limit `message` to 10,000 characters and `url` to 2,048 characters.
- [ ] Use one of these `incident_status` values: `received_only`, `clicked_link`, `shared_personal_data`, `shared_credentials`, `made_payment`.
- [ ] Send `include_url_inspection: false` only when URL parsing should be skipped.
- [ ] Never open, preview, fetch, or otherwise follow a user-supplied URL in the frontend.

## 3. Render the response

Expect this top-level shape:

```text
{
  assessment: { level, summary, uncertain },
  model: { status, label, score, score_name, limitation },
  signals: [{ source, signal_id, evidence, reason, severity, recommended_action }],
  urls: [{ submitted_url, host, scheme, valid, signals, error }],
  limitations: [string],
  next_steps: [string]
}
```

- [ ] Render `assessment.level` as one of: `low_indicators`, `moderate`, `high`, `critical`.
- [ ] Render `assessment.summary` and the `assessment.uncertain` caution on every result.
- [ ] Render model state exactly as returned. In the current build, `model.status` is `unavailable` and `label`, `score`, and `score_name` are `null`; label it rules-only, not ML-powered.
- [ ] Group `signals` by `source`: `rule` is rule-engine evidence and `url` is local URL-structure evidence. Show each evidence snippet, severity, reason, and recommended action.
- [ ] Render each `urls` item separately. If `valid` is `false`, show its `error`; do not infer a destination or make a network request.
- [ ] Always render `next_steps` and `limitations`, including for `low_indicators`.

## 4. UI states

- [ ] **Empty:** prompt for a message or URL; do not submit an empty request.
- [ ] **Loading:** disable duplicate submission and show that local analysis is running.
- [ ] **Success:** show assessment, evidence, URL inspection, next steps, limitations, and rules-only model status.
- [ ] **No indicators:** show that no specific local signals were found; never claim the content is safe or verified.
- [ ] **Validation error (422):** read `detail[0].msg` when present and display a user-safe message.
- [ ] **Network/server error:** retain the input and display a retry message without exposing implementation details.

## 5. Incident-aware actions

`next_steps` varies only by the selected `incident_status`:

- [ ] `received_only`: do not reply/pay/open; verify independently.
- [ ] `clicked_link`: close the page; change credentials if entered.
- [ ] `shared_personal_data`: contact the affected service and watch for follow-up impersonation.
- [ ] `shared_credentials`: change credentials and contact the bank/payment provider for banking, OTP, or UPI PIN exposure.
- [ ] `made_payment`: contact the bank/payment provider promptly and preserve transaction details.

Render the returned strings rather than duplicating this logic in the frontend.

## 6. Origin and security check

- [ ] The existing backend serves its bundled frontend from the same origin and has no CORS middleware.
- [ ] If Antigravity serves from a different browser origin, its requests will be blocked until the backend is explicitly configured with a narrow allowlist for that known origin. Do not use `*` for CORS.
- [ ] Render all backend text as text, not HTML. Do not use `innerHTML` for evidence, errors, or message content.
- [ ] Do not persist submitted message text unless a separate, reviewed requirement explicitly authorizes it.

## 7. Integration verification

- [ ] Confirm the health endpoint.
- [ ] Scan `fake_internship_registration_fee` from `tests/fixtures/demo_scenarios.json`; expect `high` and rule evidence.
- [ ] Scan `upi_refund_pin_request`; expect `critical` and rule evidence.
- [ ] Scan `legitimate_otp_safety_warning`; expect `low_indicators` without credential-request evidence.
- [ ] Scan `shortened_url_structure`; expect `moderate` and `url_shortener` evidence without opening the link.
- [ ] Scan `ip_host_url_structure`; expect `moderate` and `ip_address_host` evidence.
- [ ] Confirm a blank request and over-limit input show validation errors.
- [ ] Confirm all displayed response data comes from `/api/analyze` and the backend test suite passes with no API-contract changes.

For field details and actual JSON examples, see [API.md](API.md).
