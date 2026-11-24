# SIFT — Competitive Positioning (Category-Level)

**Purpose:** Keep the product positioning realistic. Scam and phishing detection already exists in built-in platforms and security products. SIFT should demonstrate a useful workflow and explainability rather than claim the entire detection category is new.

## 1. Existing protection categories

| Product/category | Existing capability (officially documented) | What SIFT should acknowledge |
|---|---|---|
| Google Messages spam protection | Google documents on-device machine-learning models for known spam patterns, spam/scam identification, and URL checking. Its documentation says URL data may be sent to Google for verification; reporting can also contribute data to improve protection. | SIFT is not replacing the built-in filter or claiming better detection. It can offer a user-initiated analysis view with a more explicit, inspectable explanation and next-step workflow. |
| Pixel / Android scam protections | Google documents built-in spam/scam warnings for calls and messages on supported devices. It also documents Circle to Search and Google Lens flows that can analyze suspicious message content and provide guidance. Availability and exact capabilities depend on device/features. | SIFT should not claim cross-device or system-wide protection. Its prototype is a standalone workflow for pasting text/URLs and reviewing evidence. |
| Chrome Safe Browsing | Chrome checks visited sites/downloads against unsafe-site and download information, with different protection modes and privacy mechanisms. | This is a browser protection layer, not a reason to claim that URL checks are unique to SIFT. SIFT's initial local URL inspector is structural and does not have equivalent reputation data. |
| Microsoft Defender SmartScreen | Microsoft documents phishing/malware website and download protection, reputation checks, suspicious-page analysis, and enhanced phishing protections in supported Windows environments. | SIFT does not have SmartScreen's threat reputation ecosystem. It must explicitly state that it does not verify live domain reputation or malware status. |
| Telecom, caller-ID, bank, payment, and messaging-provider warnings | These can provide sender/caller reputation, transaction monitoring, account-specific alerts, blocking, or reporting in their own context. Capabilities vary by provider and region. | SIFT should complement—not impersonate—those services. For actual account or payment incidents, direct users to their provider's official support route. |

## 2. The honest SIFT position

SIFT is a **user-initiated explain-and-act layer** for suspicious communication. The user supplies a message or URL and receives:

1. A transparent split between ML, rule, and URL-structure signals.
2. Exact evidence snippets and an explanation for each finding.
3. Contextual care for benign messages that contain security-related words.
4. A clear statement of what SIFT cannot verify.
5. A safe, incident-specific next-step path.
6. Educational scam-pattern material connected to the actual findings.

This is a product-experience differentiator to demonstrate, not a claim that no existing product offers any similar feature. Google Lens/Circle to Search, for example, already documents scam analysis and guidance flows. SIFT's opportunity is to make its own evidence contract, local processing, transparent limitations, and structured recovery guidance consistent across the product.

## 3. Capability comparison — prototype scope

| Capability | SIFT MVP target | Important limitation |
|---|---|---|
| Paste and analyze arbitrary message | Yes | User must manually supply content; no inbox integration |
| ML classification | Yes, lightweight local model | Data is initially synthetic/reviewed and may not generalize |
| Contextual safety rules | Yes | Rules cover a finite set of patterns and can miss new tactics |
| URL structural inspection | Yes, local parsing | No live reputation, DNS/domain ownership, redirect, or malware verification |
| Evidence Trail | Yes | Explanations must map only to actual signals |
| Incident-specific advice | Yes | Guidance is educational; not a bank or law-enforcement service |
| Automatic blocking | No | SIFT is not integrated with SMS/call/browser interception |
| Live threat intelligence | No in MVP | Do not display a live reputation or “verified safe” claim |

## 4. Defensible differentiators to prove in the demo

### A. Evidence Trail
The user can see which exact phrase or URL component triggered a warning, which engine found it, why it matters, and what to do next.

### B. Contextual restraint
A benign message saying “Never share your OTP” should not be flagged as an OTP theft request. Show this hard negative live.

### C. Honest limits
Make the absence of live reputation/sender verification visible. Distinguish local structural indicators from verified threat intelligence.

### D. From detection to action
The product changes advice based on whether the user only received the message, clicked, shared data/credentials, or paid.

### E. Privacy-conscious default
Core scan runs locally, raw messages are not stored by default, and third-party data generation is kept separate from live user scans.

## 5. What is still unknown

The exact scam-alert product or feature the user referred to earlier has not been identified. Do not assume it is Google Scam Detection, Truecaller, a bank feature, or another service. When its exact name is supplied, compare its documented capabilities and limitations against SIFT using current official sources.

## 6. Official references consulted

- Google Messages spam detection and privacy: https://support.google.com/messages/answer/9327903
- Google Messages spam reporting: https://support.google.com/messages/answer/9061432
- Google Pixel spam and scam protection: https://support.google.com/pixelphone/answer/16704479
- Google Chrome Safe Browsing privacy/protection: https://support.google.com/chrome/answer/13844634
- Microsoft Defender SmartScreen: https://learn.microsoft.com/en-us/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen/
- Google Android scam-protection announcement (14 October 2026): https://blog.google/security/new-android-scam-protections/

Re-check these official pages when making claims in a public pitch because device eligibility, feature availability, privacy behavior, and product scope can change.
