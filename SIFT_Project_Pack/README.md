# SIFT — Project Handoff Pack

**Tagline:** Don't just read it. Sift through it.  
**Working description:** An explainable, privacy-conscious digital fraud analysis tool for suspicious messages and links, initially focused on Indian users.

## What this pack is for

Upload these documents to a dedicated ChatGPT Project so the assistant has a consistent product brief, technical direction, data strategy, safety constraints, UI direction, and hackathon execution plan before implementation begins.

This is a **planning and handoff pack**, not a claim that the application has already been implemented. Several technical choices are recorded as recommended defaults and remain open for the user to approve.

## Recommended upload order

1. `PROJECT_INSTRUCTIONS.md` — paste into the ChatGPT Project instructions field.
2. `PRODUCT_VISION.md`
3. `REQUIREMENTS.md`
4. `DIFFERENTIATION.md`
5. `COMPETITIVE_POSITIONING.md`
6. `ARCHITECTURE.md`
7. `ML_AND_DATA_PLAN.md`
8. `ADAPTION_DATASET_GENERATION.md`
9. `DATA_DICTIONARY.md`
10. `SAFETY_PRIVACY.md`
11. `UI_UX_GUIDE.md`
12. `TESTING_AND_EVALUATION.md`
13. `DEMO_PLAN.md`
14. `HACKATHON_EXECUTION_PLAN.md`
15. `DECISIONS_AND_OPEN_QUESTIONS.md`

Also upload the files in `dataset_prompts/` and `templates/` when relevant. If the Project has a file limit, prioritize the instructions, vision, requirements, architecture, ML/data plan, Adaption playbook, safety rules, and decision log.

## Important current decisions

- Problem statement: scam, phishing, and fake-offer verification (PS 2 from the event options discussed).
- Product name: **SIFT**.
- Tagline: **Don't just read it. Sift through it.**
- Proposed detection approach: hybrid — a trained lightweight text classifier, transparent safety rules, and local URL-structure inspection.
- Proposed model: TF-IDF (word + character features) with Logistic Regression as a fast, inspectable baseline.
- Proposed app shape: local web UI + local Python/FastAPI inference service; no cloud dependency for core scanning.
- Adaption is a candidate source for synthetic training examples. Generate a small pilot, estimate credits first, audit the rows, and only then scale up.
- Raw user-submitted messages should not be stored by default.
- No claim of verified safety, real-time threat intelligence, live reputation checking, or production-grade accuracy unless actually implemented and tested.

## Documents and sources

Adaption platform references used while preparing this pack:
- Invent a Dataset: https://docs.adaptionlabs.ai/adaptive-data/invent-a-dataset/
- Invent a Dataset runbook: https://docs.adaptionlabs.ai/runbooks/invent-a-dataset
- Adaptive Data overview: https://docs.adaptionlabs.ai/adaptive-data/overview

The competitor-positioning document is a high-level category comparison, not a final audit of the specific scam-alert product the user previously mentioned. The exact product name is still an open question.

The platform documentation describes instruction datasets as prompt/completion pairs and preference datasets as chosen/rejected completions. It also documents the estimate-before-generation flow and asynchronous generation/download process. Check the live documentation and the actual account interface before spending credits because limits, pricing, and product behavior may change.

## Folder map

```text
SIFT_Project_Pack/
├── README.md
├── PROJECT_INSTRUCTIONS.md
├── PRODUCT_VISION.md
├── REQUIREMENTS.md
├── DIFFERENTIATION.md
├── COMPETITIVE_POSITIONING.md
├── ARCHITECTURE.md
├── ML_AND_DATA_PLAN.md
├── ADAPTION_DATASET_GENERATION.md
├── DATA_DICTIONARY.md
├── SAFETY_PRIVACY.md
├── UI_UX_GUIDE.md
├── TESTING_AND_EVALUATION.md
├── DEMO_PLAN.md
├── HACKATHON_EXECUTION_PLAN.md
├── DECISIONS_AND_OPEN_QUESTIONS.md
├── dataset_prompts/
│   ├── adaption_invent_master_prompt.txt
│   ├── adaption_legitimate_hard_negatives_prompt.txt
│   └── adaption_scam_messages_prompt.txt
└── templates/
    └── training_data_template.csv
```
