# SIFT — Machine Learning and Data Plan

## 1. Learning objective

Train a lightweight text classifier to distinguish clearly scam-like messages from clearly legitimate messages. The model is one signal in the system; it is not the sole judge and does not verify a sender or website.

Initial labels:
- `SCAM`: message is clearly deceptive or attempts to obtain money, credentials, sensitive information, or an unsafe action through fraud/impersonation.
- `LEGITIMATE`: message is a benign communication or a legitimate safety warning, without a deceptive request.
- `AMBIGUOUS`: evidence is insufficient or context is missing. Keep these rows in a separate review/challenge set; exclude them from the initial binary training fit.

Scam subtype metadata:
- `fake_job`
- `phishing_kyc`
- `upi_payment`
- `reward_lottery`
- `other`

## 2. Baseline model

Recommended baseline:
- Text normalization: conservative; do not remove currency symbols, digits, URLs, or important punctuation blindly.
- Word TF-IDF: unigrams and bigrams.
- Character TF-IDF: short character n-grams to help with spelling variations and obfuscation.
- Classifier: Logistic Regression with a suitable class-weight strategy if the dataset is imbalanced.
- Save a single fitted scikit-learn pipeline with joblib.

Do not claim this is state-of-the-art. It is selected because it is lightweight, explainable enough for a short prototype, and fast to train locally.

## 3. Data sources and provenance

Potential inputs:
1. Synthetic examples generated using Adaption's Invent a Dataset.
2. Public datasets only after checking their license, source provenance, label definitions, duplicates, and relevance.
3. Small manually authored fictional examples for smoke tests and demonstration; label them as authored test fixtures, not as independent benchmark data.

Keep metadata for every row: source, batch, generation prompt/version, label reviewer, date, language, scam family, template/family identifier, and split designation.

Do not send real private messages to Adaption. Synthetic generation is the intended first workflow.

## 4. Dataset design

A practical first pilot:
- 40 clearly scam-like rows.
- 40 clearly legitimate rows, with difficult benign examples included.
- 10–20 ambiguous cases held separately for review/testing.

After checking the pilot, consider scaling to a few hundred examples. Do not start with thousands simply because credits are available. First inspect whether the output is varied, correctly labelled, and useful for the intended classifier.

For the controlled pilot, target five equally represented scam families: fake jobs, phishing/KYC, UPI/payment, reward/lottery, and other clear scams. Pair legitimate hard negatives by context: employment/recruitment; banking/OTP/KYC safety; payments/refunds/UPI; delivery/rewards/promotions; and miscellaneous legitimate communications. This prevents the classifier from learning that a category or keyword alone implies fraud.

The SCAM and LEGITIMATE pilot targets are 16 English, 8 Devanagari Hindi, 12 natural Hinglish, and 4 mixed-language examples per class. The separate 16-row AMBIGUOUS target is 6 English, 4 Hindi, 4 Hinglish, and 2 mixed. These are quality-aware planning targets, not grounds to force unnatural text or incorrect labels.

## 5. Hard negatives and contrast pairs

Important benign examples include:
- “Never share your OTP with anyone” (safety warning, not an OTP request).
- A bank alert that says a transaction occurred but asks the user to open the official app independently.
- A job invitation with no payment demand and a verifiable application route in the fictional scenario.
- A delivery update that contains a tracking reference but no credential/payment demand.
- A genuine refund status message that does not ask for a PIN, OTP, QR scan, or collect approval.
- A promotional message with an ordinary discount and no false prize or fee claim.

Hard negatives should be linguistically similar to scam examples while remaining benign. This is critical for reducing keyword-triggered false positives.

## 6. Data quality gates

Before training:
1. Confirm all required fields exist and labels are valid.
2. Remove exact duplicates.
3. Inspect near-duplicates and recurring templates.
4. Check the scam/legitimate balance and category coverage.
5. Inspect a random sample from every class and subtype.
6. Look for label contradictions and unsupported claims.
7. Ensure legitimate examples are not merely obviously generic filler.
8. Separate ambiguous rows.
9. Track generated and manually authored content separately.
10. Save a frozen, versioned dataset snapshot before training.

Reject or repair batches with repetitive wording, incorrect labels, implausible language, or unrealistic distributions.

## 7. Training and evaluation split

Do not randomly split rows if many examples are paraphrases of the same seed/template. Group near-duplicates and related templates together so a group stays in one split.

Recommended target split, subject to dataset size:
- 70% train.
- 15% validation.
- 15% test.

Prefer an independently generated or manually curated challenge set for the final demonstration of generalization. Keep it untouched during model selection. If the data is too small to support a stable split, report that limitation and do not overstate metrics.

## 8. Metrics

Report at minimum:
- Precision and recall for the SCAM class.
- F1 score.
- Confusion matrix.
- False positives (legitimate classified as scam).
- False negatives (scam classified as legitimate).
- Per-category recall where the sample size allows it.

Accuracy alone is insufficient. In this product, false positives harm trust and false negatives can expose users to loss; discuss both.

## 9. Model uncertainty

Logistic Regression's `predict_proba` output is not automatically a calibrated fraud probability. Call it a model score or class score unless probability calibration has been tested on suitable held-out data.

Define an uncertainty band using validation data. When the top score is weak, or when the ML output conflicts with strong/contradictory evidence, return a cautionary/uncertain assessment. Select thresholds based on measured validation behavior, not guesswork.

## 10. Explainability

Do not present a feature coefficient as proof that a particular word makes a message fraudulent. The user-facing Evidence Trail should rely primarily on:
- Actual matched rule evidence.
- Actual URL components.
- Model output and its limitations.

If model token contributions are shown, label them as influential text features rather than causal proof. Never fabricate highlighted spans.

## 11. Future feedback loop

If feedback is included:
1. Ask explicit consent.
2. Store only the minimum necessary information.
3. Avoid storing raw user messages by default.
4. Treat feedback as an unverified label suggestion.
5. Review/validate before adding it to a training set.
6. Retrain offline.
7. Compare candidate model against the previous version on a frozen evaluation set.
8. Replace the model only if the candidate meets documented criteria.

No automatic online learning in the first release.
