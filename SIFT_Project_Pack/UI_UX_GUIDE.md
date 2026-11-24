# SIFT — UI/UX Direction

## 1. Design intent

Create a clean, premium, focused safety tool—not a generic neon hacker dashboard. It should feel trustworthy, modern, calm, and quick to understand.

## 2. Visual direction

Suggested palette:
- Deep forest green: `#174C38`
- Warm off-white: `#F7F3E8`
- Soft lime accent: `#D8F36A`
- Charcoal text: `#202622`
- Muted amber for caution: use sparingly
- Restrained red for high-severity warnings: use sparingly

Use white/cream surfaces, strong typography hierarchy, generous spacing, simple iconography, and restrained borders/shadows. Avoid excessive gradients, neon glows, cyber-grid backgrounds, and crowded cards.

## 3. Information architecture

Main navigation:
1. Overview
2. Scan Message
3. Inspect URL
4. Pattern Library
5. Safety Center
6. Methodology / About

Keep the primary action—paste and analyze a message—obvious on the Overview page.

## 4. Overview page

- Product name and tagline.
- Main message input entry point.
- Secondary Inspect URL action.
- Short explanation of the Evidence Trail.
- A few fictional example cases for exploration.
- Visible privacy/limitations statement: core scanning is local; low risk is not a safety guarantee.

## 5. Scan results

Recommended hierarchy:
1. Risk label and plain-language summary.
2. Compact model/rule/URL signal breakdown.
3. Evidence Trail with highlighted exact snippets.
4. Why the evidence matters.
5. Safe next steps.
6. What SIFT cannot verify.
7. Related pattern entry.

Do not rely on red/green alone. Use text labels and icons so the meaning remains clear to color-blind users.

## 6. Risk labels

Use four labels:
- Low indicators detected.
- Moderate concern.
- High concern.
- Critical warning.

Add “Uncertain — review carefully” when outputs conflict or the model has low confidence. Do not label low risk as “Safe” or “Verified”.

## 7. Pattern Library

Each entry should include:
- Pattern name.
- How it usually works.
- Common red flags.
- What a safer legitimate flow looks like (without making universal claims).
- Safe verification steps.
- A fictional example.

Initial entries: fake job/internship, phishing/KYC, UPI/payment, reward/lottery.

## 8. Safety Center

Ask what happened using short plain-language choices:
- I only received the message.
- I clicked the link.
- I shared personal information.
- I shared an OTP/password/PIN.
- I made a payment.

Then show prioritized steps. Do not overload the user with every possible response at once.

## 9. Accessibility and responsiveness

- Mobile-first responsive layout.
- Keyboard-accessible controls and visible focus.
- Adequate text contrast.
- Clear labels and helpful validation errors.
- Preserve line breaks in pasted messages.
- Ensure long URLs and evidence snippets wrap safely.
- Avoid motion-heavy transitions.

## 10. UI truthfulness

- Show whether ML was actually used or the app is in fallback mode.
- Do not display invented accuracy or threat-intelligence badges.
- Do not display a result that appears precise when the underlying evidence is weak.
- Highlight only exact text returned by the analysis engine.
