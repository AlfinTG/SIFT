# SIFT — Dataset Contract and Data Dictionary

## 1. Canonical processed row

| Field | Type | Required | Description |
|---|---|---:|---|
| `sample_id` | string | yes | Stable unique row ID generated during conversion |
| `message_text` | string | yes | Only the received message content; exclude task instructions and completion text |
| `label` | enum | yes | `SCAM`, `LEGITIMATE`, or `AMBIGUOUS` |
| `scam_type` | enum/string | no | `fake_job`, `phishing_kyc`, `upi_payment`, `reward_lottery`, `other`, or empty for legitimate |
| `language` | string | yes | `en`, `hi`, `hinglish`, or `mixed` as appropriate |
| `channel` | string | no | SMS, WhatsApp-style chat, email, social DM, job platform, etc. |
| `tactics` | list/string | no | Pressure, impersonation, fee demand, credential theft, reward bait, etc. |
| `evidence_quotes` | list/string | no | Exact substrings supporting the assigned label |
| `rationale` | string | yes | Short explanation for the label |
| `difficulty` | enum | no | `easy`, `hard_negative`, `ambiguous`, `edge_case` |
| `source` | string | yes | `adaption_synthetic`, `public_dataset`, or `manual_fixture` |
| `source_batch` | string | yes | Batch identifier |
| `generation_prompt_version` | string | no | Prompt version for synthetic data |
| `template_family` | string | no | Group identifier for template/near-duplicate splitting |
| `review_status` | enum | yes | `unreviewed`, `accepted`, `rejected`, `needs_review` |

Review accountability is kept outside the canonical training row so review operations do not change model features or the stable conversion contract. The derived review ledger is joined to canonical rows by `sample_id` and contains `review_decision`, `reviewer_id`, `reviewed_at` (ISO 8601 date/time), `review_notes`, and any automated `rejection_reason`. An accepted row is eligible for downstream use only when its final ledger entry identifies the reviewer and review time.

## 2. Language policy

- `en`: predominantly English.
- `hi`: Hindi written predominantly in Devanagari.
- `hinglish`: natural Hindi-English mixing, normally in Latin/Roman script; it is not merely English with an isolated Hindi word.
- `mixed`: material use of more than one language/script where a single primary category would misrepresent the message.

Review naturalness and correct classification before quota fulfilment. Do not relabel a predominantly English message as Hindi or Hinglish just to meet a planned quota.

## 3. Label policy

### SCAM
Use only when the message clearly attempts fraud or a deceptive risky action. Examples: pay a fee to secure a fake internship, disclose an OTP/PIN/password, scan a QR to receive a refund when the action is actually a payment request, or claim an unearned prize that requires payment/credentials.

### LEGITIMATE
Use when the message is a benign notification or legitimate safety communication. Include difficult negatives such as “Never share your OTP”, ordinary delivery updates, payment confirmations, normal hiring notices without suspicious payment/data requests, and non-deceptive promotional messages.

### AMBIGUOUS
Use when there is not enough context to confidently label the message. Do not train the initial binary classifier on these rows. Keep them for human review and cautious evaluation.

## 4. Strict prompt/completion extraction

Adaption's generated instruction row should contain a stable `MESSAGE_TO_CLASSIFY` section in `enhanced_prompt` (or the corresponding original prompt field). The converter must extract the text between explicit start/end delimiters and must not include the fixed instructions.

The completion should be a JSON object that can be parsed. Reject malformed JSON or label mismatch for manual review. Do not repair a bad label by blindly trusting the completion's rationale.

## 5. Example canonical rows

These are fictional schema examples only, not training claims.

```json
{"sample_id":"demo-001","message_text":"Pay ₹799 to confirm your internship seat today.","label":"SCAM","scam_type":"fake_job","language":"en","channel":"chat","tactics":["upfront_fee","urgency"],"evidence_quotes":["Pay ₹799","confirm your internship seat"],"rationale":"The message demands payment to secure an employment opportunity.","difficulty":"easy","source":"manual_fixture","source_batch":"demo-fixtures-v1","generation_prompt_version":"","template_family":"job-fee-01","review_status":"accepted"}
{"sample_id":"demo-002","message_text":"For your security, never share your OTP with anyone, including callers.","label":"LEGITIMATE","scam_type":"","language":"en","channel":"sms","tactics":[],"evidence_quotes":["never share your OTP"],"rationale":"This is a protective warning and does not request the OTP.","difficulty":"hard_negative","source":"manual_fixture","source_batch":"demo-fixtures-v1","generation_prompt_version":"","template_family":"otp-warning-01","review_status":"accepted"}
```

## 6. Training rules

- Initial sklearn training uses only accepted `SCAM` and `LEGITIMATE` rows.
- `message_text` is the input feature; `label` is the target.
- Never use `rationale`, `evidence_quotes`, `scam_type`, or task instructions as model input in the first baseline.
- Preserve `template_family` or equivalent grouping metadata for split design.
- Keep the untouched raw Adaption export alongside the processed file.
- Keep all rows from a `template_family`, conceptual duplicate cluster, or shared generation seed in one split only. Do not randomly split individual synthetic rows.
- Maintain a separately created challenge set that is never used to select features, thresholds, or model versions.
