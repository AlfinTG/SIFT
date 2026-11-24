# SIFT — Differentiation and Product Identity

## 1. Positioning

SIFT should not claim to be the first scam detector or the most accurate system. Existing browsers, operating systems, messaging apps, banks, telecom providers, and security products may already provide scam or phishing warnings. SIFT's credible differentiation is the way the prototype brings several user-facing capabilities together and makes its reasoning visible.

## 2. Primary differentiator: the Evidence Trail

Most important result component: **show the evidence, not just the verdict**.

For each signal, expose:
- What was detected.
- The exact words or URL component that triggered it.
- Which engine found it (ML, rule, URL inspection).
- Why it matters in context.
- What the user should do safely.

Example:

| Signal | Evidence | Explanation | Safe action |
|---|---|---|---|
| Upfront job fee | “Pay ₹799 to confirm your internship” | A fee demanded to secure an employment opportunity is a strong warning sign | Do not pay; verify the organization independently |
| Pressure | “Offer expires in 20 minutes” | The message is discouraging careful verification | Pause and verify through a separately found official channel |

Evidence snippets must be sourced from actual engine output. Never invent a quote to make an explanation appear convincing.

## 3. Secondary differentiators

### A. Risk breakdown, not a mystery score
Show independent dimensions such as message model signal, safety-rule signals, and URL structure. Explain that a combined risk level is a heuristic summary, not a validated fraud probability.

### B. “What SIFT cannot verify”
Explicitly list missing capabilities: sender identity, ownership of the domain, current reputation, website contents, whether the claimed account event is real, and whether a specific offer exists.

### C. Contextual false-positive care
A message containing “OTP” is not automatically a scam. Distinguish requests to disclose an OTP from legitimate warnings not to share it. Treat ambiguous cases cautiously.

### D. Learn the pattern
Link each finding to a concise educational entry explaining the manipulation tactic, common variants, safe verification, and the mistake to avoid.

### E. After-the-click guidance
Offer a clear response path based on what happened: received only, clicked, shared data, shared credentials, or paid. This makes the tool useful after a mistake as well as before one.

### F. Privacy-conscious local processing
Core scanning should occur on the user's device/local machine for the prototype. Do not save raw messages by default. Adaption is for synthetic dataset generation, not live user-message processing.

## 4. Proposed named experience

**SIFT Evidence Trail** — the primary result experience that combines:
1. Assessment.
2. Signals and evidence.
3. Why it matters.
4. What cannot be verified.
5. Safe next step.
6. Relevant learning resource.

Avoid inventing multiple brand names for every small component. Keep SIFT as the product brand and Evidence Trail as its main feature.

## 5. How to demonstrate differentiation

Use one high-risk fake internship, one nuanced benign OTP warning, one suspicious URL, and one post-payment safety scenario. Show both detection and restraint. The benign example is crucial: a product that flags everything is not trustworthy.

## 6. Claims to avoid

Do not say:
- “100% accurate”.
- “Detects every scam”.
- “Verifies any website”.
- “Uses live threat intelligence” unless a real source is integrated.
- “Learns continuously” because feedback is collected.
- “The first AI scam detector”.

Prefer: “Combines a lightweight trained text classifier, transparent safety rules, and local URL-structure analysis to produce evidence-backed guidance.”
