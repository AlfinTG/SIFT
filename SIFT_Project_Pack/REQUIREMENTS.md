# SIFT — Product Requirements

## 1. Must-have requirements

### R1 — Message scan
- Accept pasted plain-text messages.
- Validate empty input and a reasonable maximum length.
- Return the model classification/score, rule findings, combined assessment, explanation, and suggested action.
- Do not store message text after the request completes by default.

### R2 — ML classification
- Use a real supervised model trained from reviewed labelled examples.
- Initial baseline: binary `SCAM` versus `LEGITIMATE` classification.
- Keep ambiguous examples separate; do not force them into either class.
- Surface an “uncertain / needs caution” state when the model's decision score is weak or the signals disagree.

### R3 — Safety rules
- Detect contextual patterns for credential/OTP/PIN requests, payment demands, upfront job fees, pressure/urgency, threat of account closure, impersonation cues, and reward bait.
- Each triggered rule must return a reason and evidence snippet.
- Rules must be contextual: a message warning “Never share your OTP” must not be treated as an OTP theft request.

### R4 — URL inspection
- Extract URLs from messages and accept a URL entered directly.
- Parse structure locally without visiting the destination.
- Consider shorteners, raw IP hosts, confusing subdomains, punycode/Unicode, unusual encoding, suspicious host/path patterns, and embedded credentials where feasible.
- Explain that HTTPS is not proof of trustworthiness.
- Clearly state that domain age, ownership, reputation, malware status, and page contents are not verified in the MVP.

### R5 — Evidence Trail
Every finding must contain:
- `source`: `ml`, `rule`, or `url`.
- `signal_id` or stable rule identifier.
- `evidence`: exact matched text or URL component where possible.
- `reason`: plain-language explanation.
- `severity`: informational, low, medium, high, or critical.
- `recommended_action`: a specific safe action.

### R6 — Safe recommendations
- Give clear action guidance for “received only”, “clicked a link”, “shared personal data”, “shared OTP/password/PIN”, and “made a payment”.
- For suspected financial fraud, advise promptly contacting the bank/payment provider through official channels and using official Indian cybercrime reporting channels; do not guarantee recovery.

### R7 — Reliability
- Provide useful errors when the local inference service is unavailable.
- Show a visible limitation notice if the model file is missing or a fallback mode is active.
- App must have a simple, documented local launch procedure.

## 2. Strongly desired requirements

- Standalone Inspect URL page or panel.
- Evidence text highlighting in the original message.
- Searchable Scam Pattern Library.
- Safety Center with incident-specific steps.
- Recent scan metadata only if the user explicitly enables it; raw text remains excluded by default.
- About / Methodology page explaining model, rules, limitations, and dataset provenance.
- Keyboard-friendly, responsive layout.

## 3. Stretch requirements

- Hinglish/Hindi analysis after language-specific evaluation.
- Optional user feedback with explicit consent and no automatic retraining.
- Evaluation dashboard with confusion matrix and false-positive examples.
- Controlled review/retraining flow for future versions.
- External threat-intelligence integration only after the local MVP works and privacy implications are reviewed.

## 4. Out of scope for first release

- Browser extension, mobile app, accounts, cloud dashboard, multi-tenant service.
- Live web crawling or opening submitted URLs.
- Real-time bank, UPI, telecom, or government integrations.
- Claiming guaranteed detection or verified-safe status.
- Large language model fine-tuning solely to make a classifier look more advanced.

## 5. Core acceptance tests

1. A fake internship asking for a registration fee is flagged with the fee/offer evidence visible.
2. A phishing message demanding an OTP under an account-suspension threat is flagged with both signals visible.
3. A UPI refund message asking for a PIN or QR action is flagged with the specific unsafe request visible.
4. A benign security notice telling the user never to share an OTP is not automatically classified as a scam by the rule engine.
5. A benign delivery or appointment message is not marked high risk solely due to a short deadline or a tracking link.
6. A suspicious URL can be parsed without network access or navigation.
7. HTTPS does not suppress other structural warnings.
8. The result clearly explains that “Low” does not mean verified safe.
9. Raw scanned text is not persisted by default.
10. The app starts from a fresh project folder using the documented instructions.
