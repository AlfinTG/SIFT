# SIFT — Decision Log and Open Questions

## 1. Confirmed by the user

| Item | Current value |
|---|---|
| Hackathon problem direction | PS 2 — Scam, Phishing and Fake Offer Verifier |
| Product name | SIFT |
| Tagline | “Don't just read it. Sift through it.” |
| Pre-preparation | Allowed |
| AI coding assistants | Allowed |
| Git | Not being used for this event |
| Adaption | User reports approximately USD 1,000 in available credit/budget; exact account balance and terms must be checked |

## 2. Current recommendations, not yet locked

| Decision | Recommendation | Reason |
|---|---|---|
| Detection approach | Hybrid ML + contextual rules + URL structure | Combines learned text patterns with inspectable evidence |
| ML baseline | TF-IDF word/character features + Logistic Regression | Lightweight and practical for a short build |
| ML labels | Binary SCAM/LEGITIMATE; ambiguous kept separately | Avoids forcing uncertain examples into false certainty |
| Dataset | Adaption-generated synthetic pilot + reviewed hard negatives | Fast start, but needs quality audit and independent evaluation |
| Local API | FastAPI | Simple local model boundary |
| UI | Lightweight web UI, vanilla JS default | Shortest implementation path unless user chooses another framework |
| URL analysis | Local structure inspection only | Avoids opening risky links and external network dependencies |
| Feedback | Optional, reviewed, offline retraining only | Avoids noisy labels and uncontrolled learning |

## 3. Open questions to settle during discussion/build

1. Does the user want to use Adaption only for synthetic dataset generation, or also investigate its model-training/AutoScientist capability? The recommendation is to use it for data first and keep local sklearn inference for the hackathon baseline.
2. Should the first supported text language be English-only, or English plus Hinglish? Recommendation: start with English examples and include Hinglish only if a small evaluation set can verify behavior.
3. Is the user comfortable with vanilla HTML/CSS/JS + FastAPI, or do they prefer a frontend framework already familiar to them?
4. What is the exact current Adaption credit balance, row cap, and displayed estimate for the desired pilot? Check in the account; do not infer from the reported budget.
5. What is the precise name of the existing scam-alert product/feature the user referred to earlier? Do not assume its identity; this is needed for a fair product comparison.

## 4. Risks to watch

- Synthetic examples may look artificial or encode generator-specific style.
- Adaption's instruction dataset may require a parsing step before it becomes classification data.
- Small or repetitive datasets can create misleadingly high test metrics.
- Rule engines can overflag generic words unless contextual counterexamples are tested.
- A local API may add integration friction; test it early.
- External threat-intelligence APIs would undermine the offline/local promise unless explicitly separated as optional.
- A “risk score” can be misunderstood as a probability; label it carefully.

## 5. Change control

When the user changes a decision, update this file and the affected project documents. Do not silently preserve contradictory requirements across files. Use explicit statuses: `confirmed`, `recommended`, `open`, or `rejected`.
