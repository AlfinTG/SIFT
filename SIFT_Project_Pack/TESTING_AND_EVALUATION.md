# SIFT — Testing and Evaluation Plan

## 1. Evaluation principles

- Evaluate the model separately from the combined product.
- Keep a frozen test set that is not used to tune rules or thresholds.
- Include difficult legitimate messages, not only obvious scam examples.
- Report dataset source and size alongside every metric.
- Do not describe synthetic-only results as real-world accuracy.

## 2. Model evaluation

Report:
- Precision, recall, F1 for `SCAM`.
- Confusion matrix.
- False-positive examples.
- False-negative examples.
- Per-scam-family results when sample counts are sufficient.
- Threshold/uncertainty behavior.

Document whether the test data is synthetic, public, manually authored, or mixed. If the test set is derived from the same generation prompt/batch as training, explicitly disclose that limitation and do not use it as strong generalization evidence.

## 2.1 Integration evaluation

- With no artifact at `ml/artifacts/message_classifier.joblib`, `/api/analyze` must return `model.available=false`, `model.status="unavailable"`, and no prediction or score while rules and URL inspection remain active.
- A SCAM model prediction is a supporting medium-severity ML signal only; it cannot independently produce a critical result.
- A LEGITIMATE model prediction must never suppress deterministic rule or URL evidence.
- Model scores are uncalibrated scores, not fraud probabilities. Test the model adapter, fusion behavior, unavailable/error fallbacks, API schema, and frontend rendering with `python -m pytest tests/test_ml_integration.py -q`.

## 3. Functional test matrix

| Case | Expected behavior |
|---|---|
| Fake internship + upfront fee | Flag fee and employment-offer evidence |
| KYC warning + demand for OTP | Flag credential request and pressure/impersonation signals |
| UPI refund + PIN/QR request | Flag the specific unsafe payment action |
| Legitimate message saying “never share OTP” | Do not flag as an OTP theft request solely due to this phrase |
| Ordinary delivery tracking message | Do not escalate solely because it includes a link or deadline |
| Normal payment confirmation | Do not infer fraud from payment vocabulary alone |
| Reward message requiring a claim fee | Flag reward bait and fee demand |
| Message with no suspicious signals | Low indicators or uncertain, never “verified safe” |
| URL with a shortener | Explain the shortener signal without claiming it is malicious |
| URL containing an IP host or confusing subdomain | Show exact structural feature and cautious explanation |
| URL with HTTPS and suspicious host structure | HTTPS must not suppress the warning |
| Malformed URL | Graceful validation error; do not crash |
| Very long message | Enforce documented input limit and return a clear error |
| API/model unavailable | UI displays honest fallback/error state |

## 4. Rule tests

For every rule, include:
- A positive case.
- A benign counterexample.
- A context-sensitive edge case.
- Expected evidence snippet.

Examples:
- Positive: “Reply with your OTP to keep the account active.”
- Negative: “Never share your OTP with anyone.”
- Edge: “Your OTP is 123456” in a legitimate login notification; the app must not echo sensitive-looking codes unnecessarily in explanations.

## 5. URL tests

- Valid HTTP and HTTPS URLs.
- Shortened URL pattern (structural signal only).
- Raw IP host.
- Punycode/Unicode host handling.
- Misleading subdomain, e.g. `brand.example.attacker.test` (fictional reserved test domain).
- Embedded username/password component.
- Unusual encoding and malformed input.
- No network request occurs during inspection.

## 6. Privacy and offline tests

1. Scan a message and inspect local logs/files; raw text should not be persisted by default.
2. Search the frontend bundle for secrets; there must be none.
3. Disconnect the internet after setup and verify core scan still works.
4. Confirm URL inspector makes no outbound request.
5. Confirm no user content is transmitted to Adaption or another provider during scanning.

## 7. Release checklist

- Fresh install/launch succeeds.
- Model artifact loads.
- Main scan flow works end-to-end.
- At least one positive and one hard-negative case pass.
- URL analysis works without navigation.
- Explanations correspond to real findings.
- Limitations and privacy statement are visible.
- No API key is exposed.
- Demo data is fictional.
- ZIP backup exists and was tested from an extracted folder.
