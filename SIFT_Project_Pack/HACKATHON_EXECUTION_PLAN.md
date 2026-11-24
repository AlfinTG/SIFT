# SIFT — Hackathon Execution Plan

## 1. Context

Event context previously provided by the user: individual MLH HackDay at AITR Campus, Tuesday 24 November 2026, 11:00 AM–4:00 PM. The usable build window was estimated at approximately 5.5–6.5 focused hours across pre-event preparation and event time. Pre-preparation and AI coding assistants are permitted. Git is not available/being used for this event.

Reconfirm event rules, timing, and presentation format with the organizer if anything changes. Do not assume a judge scoring rubric that has not been provided.

## 2. Build principle

Build the smallest complete product flow first. The model must run inside the app before secondary pages are added.

## 3. Priority order

### P0 — Essential
1. App shell and local launch.
2. Dataset pilot and quality audit.
3. Train and save the first real classifier.
4. Local API inference endpoint.
5. Message scan UI.
6. Contextual rules and evidence output.
7. Risk fusion and honest uncertainty/limitations.
8. Core positive and hard-negative tests.

### P1 — Strong value
1. URL structural inspector.
2. Evidence highlighting.
3. Safe next-step guidance.
4. Pattern Library with four initial entries.
5. Responsive layout and clear methodology section.

### P2 — Stretch only after P0/P1 are stable
1. Full Safety Center paths.
2. Feedback storage/review workflow.
3. Additional languages.
4. Additional model experiments or external data integrations.

## 4. Suggested work sequence

### Preparation session
- Create the workspace and confirm runtime/dependencies.
- Validate Adaption access and run a small credit estimate.
- Generate a small dataset pilot; inspect before scaling.
- Prepare the canonical training CSV/JSONL.
- Train a baseline model and verify local inference with a standalone script.
- Create a minimal FastAPI endpoint and test it with one known message.
- Create a timestamped backup.

### Build session
- Implement UI-to-API integration.
- Add safety rules and evidence objects.
- Add URL parsing without network calls.
- Add result view and guidance.
- Add Pattern Library and Safety Center if time remains.
- Run the test matrix.
- Test the entire application from a fresh extracted folder.
- Rehearse the demo with the exact laptop and examples.

## 5. Time protection

Do not spend most of the build window tuning an ML model. A modest model that is integrated, measured, and explained is more valuable than a large dataset or complicated model that never reaches the UI.

Cut features in this order if behind schedule:
1. Feedback/retraining UI.
2. Additional language support.
3. Fancy charts and animations.
4. Large Pattern Library content.

Do not cut:
- Honest uncertainty and limitations.
- Actual ML inference if the product is presented as ML-assisted.
- At least one contextual hard-negative test.
- URL non-navigation safety.
- A reliable end-to-end scan.

## 6. No-Git backup workflow

Before a risky milestone:
- Copy the entire working folder to `SIFT_backup_YYYYMMDD_HHMM`.
- Zip milestone snapshots.
- Keep the last known-good version untouched.
- Verify a backup by extracting it and launching from the extracted copy.

Avoid manually copying selected files after multiple changes; use a complete folder snapshot to prevent missing dependencies.

## 7. AI coding-agent workflow

- One coding agent owns implementation at a time (Antigravity or the user's selected builder).
- Give the agent a single milestone, explicit acceptance tests, and permission to inspect before editing.
- Ask a second assistant to review a focused area only after a working implementation exists.
- Return fixes to the implementation owner and rerun tests.
- Do not run multiple coding agents editing the same workspace concurrently.

## 8. Final launch gate

The prototype is ready to present only when a fresh launch succeeds, the scanner works, at least one scam and one legitimate hard negative behave as expected, the URL inspector does not visit the URL, and the demo explanations match actual engine findings.
