# SIFT — Hackathon Demo Plan

## 1. Demo objective

Demonstrate that SIFT does more than return a red warning. It identifies multiple signals, quotes the evidence, explains the risk, states what it cannot verify, and gives safe next steps—while showing restraint on benign content.

## 2. Suggested 3–4 minute walkthrough

### Opening (20 seconds)
“Scam messages are designed to look routine and urgent. SIFT helps people understand the signals before they act. It combines a lightweight trained text model, transparent rules, and local URL inspection. The key is not just detection; it is explainable guidance.”

### Scenario 1 — Fake internship (60 seconds)
Paste a fictional message offering an internship and asking for a registration fee with a short deadline.

Show:
- High concern assessment.
- ML signal and upfront-fee/urgency rule findings.
- Highlighted text evidence.
- Explanation that a payment demand to secure an opportunity is a strong warning sign.
- Advice not to pay and to verify through an independently found official channel.

### Scenario 2 — Legitimate hard negative (30–40 seconds)
Paste a fictional bank safety warning that says never to share an OTP.

Show:
- The rule engine understands this is a warning, not a request for an OTP.
- Low indicators or an appropriately cautious classification.
- Explain that wording alone is not enough; context matters.

### Scenario 3 — URL inspection (40–50 seconds)
Inspect a fictional misleading URL using reserved test domains.

Show:
- Exact parsed host/subdomain structure.
- Why the structure deserves caution.
- The page is not opened and no reputation claim is made.

### Close (20 seconds)
“SIFT does not claim to verify every sender or website. It shows the evidence it found, the limitations it has, and the safest next step. That is how we make a warning useful.”

## 3. Fictional demo fixtures

### A. Fake job/internship
“Congratulations! You have been shortlisted for the Remote Software Internship. Pay ₹799 as a registration fee within 20 minutes to confirm your seat. Reply with your details to receive the joining letter.”

Expected signals: upfront fee, urgency, employment-offer bait. Use only as a fictional fixture.

### B. Benign OTP warning
“Security reminder: Never share your OTP, password, or UPI PIN with anyone. Our support team will never ask you to disclose these details.”

Expected behavior: do not flag as a credential theft request merely because OTP/PIN appears.

### C. UPI/payment bait
“Your refund is pending. Scan the QR code and enter your UPI PIN to receive the amount.”

Expected signals: unsafe PIN request and QR/refund manipulation.

### D. KYC/account pressure
“Your account will be restricted today. Complete verification using the link below and provide the OTP received on your phone.”

Expected signals: threat/urgency, credential request, URL signal if included.

### E. Delivery control
“Your parcel is out for delivery today. Track the shipment in the delivery app you normally use.”

Expected behavior: no high-risk conclusion based only on delivery vocabulary. A real pasted URL would still be structurally inspected.

## 4. Demo reliability

- Preload only fictional examples.
- Test all scenarios on the exact laptop/browser used for the presentation.
- Keep the model and service running before the judge begins.
- Have a short fallback recording or screenshots only if the event rules permit; the live app remains the primary demo.
- Never show a fabricated metric. If evaluation is limited, say exactly what was tested.
