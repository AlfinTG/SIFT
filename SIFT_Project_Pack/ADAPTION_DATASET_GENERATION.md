# SIFT — Adaption Dataset Generation Playbook

## 1. Purpose

Use **Adaption's Invent a Dataset** to create synthetic message-classification examples for SIFT. The generated data is a starting point, not ground truth and not proof of real-world performance.

Adaption documentation describes Invent as generating model-ready datasets from a `dataset_prompt`; its output can be an instruction dataset (prompt/completion pairs) or preference pairs. It supports estimating the credit cost before launching. Generation is asynchronous; the documented flow is to wait for completion and download the rows, for example as JSONL. See the source links at the end of this document.

## 2. Recommended workflow

1. Sign in to the Adaption account and confirm the actual available balance, current row limits, and pricing.
2. Use the Invent a Dataset workflow.
3. Run a **small pilot** first (for example, 80 rows total or separate smaller batches).
4. Request a credit estimate for the exact prompt and row count before generation. Do not launch a paid run until the displayed estimate and scope are acceptable.
5. Generate scam examples and legitimate hard negatives. Separate batches are recommended because they give more control over class balance.
6. Download the generated dataset as JSONL if available.
7. Preserve the original download as immutable raw data.
8. Parse the prompt/completion records into the SIFT training schema described in `DATA_DICTIONARY.md`.
9. Validate the parsed fields and manually review a sample from each batch.
10. Deduplicate, check diversity, and inspect labels before using any row for training.
11. Keep ambiguous examples separate.
12. Freeze the accepted dataset version and record its provenance.

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
| Scam batch | Fake job, phishing/KYC, UPI/payment, reward/lottery examples | 40 | 200–400 |
| Legitimate batch | Hard negatives in matching contexts | 40 | 200–400 |
| Ambiguous challenge batch | Context-poor or mixed-signal messages for review/testing | 10–20 | 30–80 |

Numbers are planning targets, not Adaption plan limits or guaranteed output counts. Keep the scam and legitimate classes approximately balanced in the accepted training set.

## 6. Prompt files

- `dataset_prompts/adaption_invent_master_prompt.txt` — complete schema and style requirements.
- `dataset_prompts/adaption_scam_messages_prompt.txt` — use for scam-positive batches; specify one family per run or distribute families evenly.
- `dataset_prompts/adaption_legitimate_hard_negatives_prompt.txt` — use for realistic benign controls.

For maximum control, run separate batches by class/family and combine after review. If using a single combined prompt, check the actual class distribution rather than assuming the generator followed an exact quota.

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
