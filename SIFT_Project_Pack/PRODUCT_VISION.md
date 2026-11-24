# SIFT — Product Vision

## 1. Product summary

SIFT is an explainable, privacy-conscious digital fraud analysis platform that helps users assess suspicious messages and links before acting. It combines a lightweight trained text classifier, transparent safety rules, and URL-structure inspection to surface evidence and recommend safe next steps.

**Tagline:** Don't just read it. Sift through it.

**Core principle:** Detection is not enough. Understanding is protection.

## 2. Problem

People receive messages that imitate employers, banks, payment providers, delivery services, schools, and reward programs. The messages can combine legitimate-looking details with pressure, fake authority, requests for money or credentials, or deceptive links. A simple “scam” label may not help a user understand what triggered the warning or what to do next.

SIFT focuses on the decision point: help users pause, understand the signals, verify through a trusted independent route, and respond safely.

## 3. Initial audience

- Students and job seekers who receive internship, placement, scholarship, and part-time job offers.
- Everyday digital users who receive KYC, account, UPI, refund, delivery, and reward messages.
- Users who are unsure whether a message is merely unusual, genuinely suspicious, or clearly deceptive.

The first demo should use India-relevant contexts and currency conventions. It should not imply official affiliation with a bank, government agency, telecom company, or payment provider.

## 4. Initial coverage

| Category | Common signals to examine |
|---|---|
| Fake jobs and internships | Registration/training/security fees, guaranteed selection, rushed offers, personal-data requests, unofficial contact channels |
| Phishing and KYC | Threatened suspension, credential/OTP requests, lookalike domains, urgent account verification |
| UPI and payment fraud | UPI PIN/OTP requests, QR-code refund claims, collect-request pressure, advance payment, fake support |
| Reward and lottery bait | Unexpected prize, processing fee, claim deadline, tax/payment request, credential collection |

These are detection themes, not a guarantee that every message in a category is fraudulent.

## 5. User promise

Given a message or URL, SIFT should:

1. Show a cautious risk assessment.
2. Explain the actual evidence behind that assessment.
3. Separate model output from rule and URL findings.
4. Tell the user what the tool cannot verify.
5. Suggest a safe verification path and relevant next action.
6. Teach a reusable pattern rather than only showing a red warning.

## 6. Product experience

The central flow is **Paste → Analyze → Understand → Act safely**.

A result should include:
- Risk level: Low indicators, Moderate, High, or Critical.
- A short plain-language summary.
- An Evidence Trail with exact text snippets and URL components.
- Signal source: ML model, safety rule, or URL inspector.
- A short explanation of why each signal matters.
- Safe next steps.
- “What SIFT cannot verify” and an uncertainty statement.
- Related pattern-library material.

## 7. What SIFT is not

- Not a law-enforcement or government reporting system.
- Not a bank, payment provider, antivirus, browser Safe Browsing replacement, or guaranteed URL reputation checker.
- Not a guarantee that a low-risk message is safe.
- Not a live website crawler in the initial version.
- Not an autonomous system that learns immediately from every user click or feedback submission.

## 8. Success for the hackathon

A judge should be able to paste a fake internship offer, see a reasoned assessment with highlighted evidence, inspect a suspicious URL without visiting it, and receive concrete safety guidance. The same system should avoid condemning a benign control message simply because it contains words such as “OTP”, “bank”, or “urgent”.

The prototype's strongest proof is a stable end-to-end demonstration and honest evaluation—not a large claimed accuracy number.
