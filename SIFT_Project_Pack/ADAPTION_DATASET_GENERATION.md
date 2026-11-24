# SIFT — Adaption Dataset Generation Playbook

## 1. Purpose

Use **Adaption's Invent a Dataset** to create synthetic message-classification examples for SIFT. The generated data is a starting point, not ground truth and not proof of real-world performance.

Adaption documentation describes Invent as generating model-ready datasets from a `dataset_prompt`; its output can be an instruction dataset (prompt/completion pairs) or preference pairs. It supports estimating the credit cost before launching. Generation is asynchronous; the documented flow is to wait for completion and download the rows, for example as JSONL. See the source links at the end of this document.

## 2. Recommended workflow

1. Sign in to the Adaption account and confirm the actual available balance, current row limits, and pricing.
2. Use the Invent a Dataset workflow.
3. Run the controlled **96-row pilot** first: 40 SCAM, 40 LEGITIMATE hard negatives, and 16 separately generated AMBIGUOUS rows.
4. Request a credit estimate for the exact prompt and row count before generation. Do not launch a paid run until the displayed estimate and scope are acceptable.
5. Generate SCAM, LEGITIMATE hard-negative, and AMBIGUOUS review rows as separate batches. The AMBIGUOUS batch is never binary training data.
6. Download the generated dataset as JSONL if available.
7. Preserve the original download as immutable raw data.
8. Parse the prompt/completion records into the SIFT training schema described in `DATA_DICTIONARY.md`.
9. Validate the parsed fields and manually review a sample from each batch.
10. Deduplicate, check diversity, language targets, template families, and labels before using any row for training.
11. Keep ambiguous examples separate through conversion, review, and evaluation.
12. Complete the review ledger with reviewer ID, ISO 8601 review time, decision, and notes for every accepted row.
13. Freeze the accepted dataset version and record its provenance.

## 3. Credit discipline

You mentioned having approximately USD 1,000 worth of Adaption credit. Treat that as a budget ceiling, not a target to spend. The actual account balance and product pricing must be checked in the account.

- Never spend credits without running the built-in estimate first.
- Pilot the prompt and inspect outputs before increasing row counts.
- Generate batches only as large as the next step requires.
- Preserve unused budget for retries or later controlled experiments.
- Do not assume a credit amount maps directly to a number of rows; output length, selected settings, and current pricing may affect cost.

## 4. Output format and conversion

For the initial classifier, request `instruction_dataset` output. Each row is a prompt/completion pair. The generation prompt files specify a consistent message block and a strict JSON completion containing a label and metadata.

The downstream conversion should:
- Extract only the received message from the delimited message block in the prompt.
- Parse the completion JSON.
- Validate `label` as `SCAM`, `LEGITIMATE`, or `AMBIGUOUS`.
- Use `SCAM` and `LEGITIMATE` for the initial binary model.
- Move `AMBIGUOUS` to a separate challenge/review file.
- Retain subtype, language, tactic, evidence, source batch, and generation metadata.

Do not train a text classifier on the entire instruction prompt plus answer. That would allow it to learn fixed task instructions and label wording rather than the message itself.

## 5. Suggested batch plan

| Batch | Purpose | Pilot size | Later scale (only if quality passes) |
|---|---|---:|---:|
| `sift-pilot-v2-scam` | 8 each: fake job, phishing/KYC, UPI/payment, reward/lottery, other | 40 | 200–400 |
| `sift-pilot-v2-legitimate` | 8 each: employment; banking/OTP/KYC; payments/refunds/UPI; delivery/rewards/promotions; miscellaneous | 40 | 200–400 |
| `sift-pilot-v2-ambiguous` | Genuine uncertainty for separate review/challenge use | 16 | 30–80 |

Numbers are planning targets, not Adaption plan limits or guaranteed output counts. Keep the scam and legitimate classes approximately balanced in the accepted training set. SCAM and LEGITIMATE language targets are 16 English, 8 Devanagari Hindi, 12 natural Hinglish, and 4 mixed-language examples per class. AMBIGUOUS targets are 6, 4, 4, and 2 respectively. Quality, naturalness, and correct labels take priority over quota fulfilment.

For every batch, record the stable `source_batch`, `generation_prompt_version`, generation date, raw export filename, reviewer owner, and family/language targets in batch notes. The current SCAM batch is `sift-pilot-v2-scam-40` with generation prompt version `sift-pilot-v2`; preserve its export as `ml/data/raw/sift-pilot-v2-scam-40.jsonl` without editing it.

## 6. Prompt files

- `dataset_prompts/adaption_invent_master_prompt.txt` — complete schema and style requirements.
- `dataset_prompts/adaption_scam_messages_prompt.txt` — use for scam-positive batches; specify one family per run or distribute families evenly.
- `dataset_prompts/adaption_legitimate_hard_negatives_prompt.txt` — use for realistic benign controls.
- `dataset_prompts/adaption_ambiguous_messages_prompt.txt` — use only for the separate ambiguity/review batch.

For maximum control, run separate batches by class/family and combine after review. If using a single combined prompt, check the actual class distribution rather than assuming the generator followed an exact quota.

## 6.1 Review and split controls

Run the offline review report across all converted batches together. Treat exact matches, near-duplicate candidates, and manually identified conceptual paraphrases as one template group. Keep each `template_family`, its paraphrases, and any shared seed in a single future split; do not randomly split individual rows. Create the final challenge set independently from pilot generation and do not use it for prompt selection, feature design, thresholds, or model selection.

## 7. What to look for in the first 20–30 rows

- Does every row contain a complete, plausible message?
- Are messages diverse in length, wording, channel, tone, and scenario?
- Do scam examples actually request a risky action or deceive the recipient?
- Do benign examples include realistic security warnings and ordinary operational notices?
- Are there obvious repeated templates with names/currency swapped?
- Are URLs safe placeholders such as `example.com` / `.example` rather than live malicious destinations?
- Does the completion JSON match the message and the requested label?
- Are examples consistently India-relevant without stereotyped or implausible details?

If the quality is weak, revise the prompt and regenerate a small pilot rather than scaling a poor batch.

## 8. Important limitation

Adaption Invent is documented primarily as generating instruction datasets and preference pairs. It does not remove the need to validate whether the resulting rows are suitable for a conventional `message_text → class_label` sklearn classifier. The conversion step is our own data-engineering task. If the generated prompt/completion structure cannot be parsed consistently, change the prompt or choose a data-generation route that produces an explicit tabular/JSONL schema before spending more credits.

## 9. Official references

- Invent a Dataset: https://docs.adaptionlabs.ai/adaptive-data/invent-a-dataset/
- Invent runbook (estimate, generate, wait, download JSONL): https://docs.adaptionlabs.ai/runbooks/invent-a-dataset
- Adaptive Data overview: https://docs.adaptionlabs.ai/adaptive-data/overview
