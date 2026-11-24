# ML execution report — 2026-11-24

## Final status: BLOCKED

The training gate is correctly blocking model training because no eligible row
has a completed, attributable human `accepted` decision. No model artifact or
evaluation metrics were fabricated.

## Dataset

- Raw files inspected: four CSV exports (126 CSV records total).
- Eligible canonical candidates: 35: 30 LEGITIMATE and 5 SCAM.
- Converted v3 SCAM candidates: 5. Its other three raw records were isolated:
  unsupported `medium` difficulty, a safety/identifier finding, and malformed
  completion JSON.
- Existing LEGITIMATE conversion: 30 candidates; 10 earlier conversion
  rejections remain isolated in its `rejected.csv`.
- Both byte-identical v2 SCAM exports (39 records each) remain excluded. Their
  bulk-array completion format cannot be safely converted by the canonical
  per-message converter, and the existing diagnostic is not approval.
- Approved SCAM / LEGITIMATE: 0 / 0. Rejected at conversion: 13. Ambiguous:
  0. Still requiring review: 35.
- Distribution: 34 English, 1 Hinglish; all five SCAM candidates are
  `fake_job`. This is insufficiently balanced for a general consumer-scam
  classifier.
- Audit findings: no missing canonical fields, invalid evidence quotes, exact
  duplicates, or near duplicates. `security_alert_protective` is repeated four
  times in the LEGITIMATE candidates. The v2 manifest does not model the v3
  fake-job batch or current legitimate template-family names, so it cannot
  provide quota approval.

The detailed machine-readable audit, editable ledger, and focused review
package are generated under `ml/data/review/` (git-ignored):

- `consolidated-audit.json`
- `consolidated-review-ledger.csv`
- `consolidated-human-review-package.md`

## Training and evaluation

The validator was run against the two candidate exports and failed as intended:
`no accepted SCAM or LEGITIMATE rows were found`. Consequently, training,
artifact generation, held-out evaluation, false-positive/false-negative
analysis, and per-language/category metrics were not run. Any result would be
untraceable and methodologically unsound.

When a qualified reviewer completes the ledger, derive reviewed exports using
the documented review command, rerun the validation gate, and train only if
group-aware class coverage is sufficient. The present data also needs more
reviewed SCAM families and non-English examples before it can support the
intended general classifier.

## Integration and QA

The existing hybrid integration was inspected and regression-tested. It loads
`ml/artifacts/message_classifier.joblib` locally when present; a missing or
failed artifact returns a truthful unavailable/error state and leaves rules and
URL analysis active. An ML SCAM result is a supporting medium signal only;
deterministic critical/high signals retain precedence. The API schema and
frontend model-state rendering are covered by tests.

- Full regression suite: `python -m pytest -q` — **61 passed**.
- Training gate: intentionally failed due to zero approved rows.
- No separate frontend build or static type-check command is configured in this
  Python/vanilla-JS repository.

## Limitations and remaining action

Human review is the sole immediate blocker. Complete decisions with reviewer
identity and ISO-8601 timestamps, preserve rejections and unresolved samples,
then rerun the gate. Do not interpret future synthetic held-out metrics as
real-world performance.
