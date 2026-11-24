# SIFT — Safety, Privacy, and Responsible Use

## 1. Core safety promise

SIFT provides indicators and guidance. It does not certify a message, sender, website, payment request, or job offer as genuine.

## 2. User-facing language

Prefer:
- “We found several warning signs.”
- “This message appears suspicious based on the indicators shown.”
- “We could not identify strong indicators, but this does not verify the sender or link.”
- “Verify independently through the official app or a contact method you find yourself.”

Avoid:
- “100% scam” unless describing an obviously fictional test case in a controlled demo.
- “Guaranteed safe.”
- “Verified website.”
- “Your money will be recovered.”

## 3. Do not encourage risky interaction

Never instruct users to:
- Open the suspicious URL to see what happens.
- Call or message a phone number included in the suspicious message.
- Scan a QR code in the message.
- Share an OTP, UPI PIN, password, CVV, recovery code, or screen-sharing access.
- Pay a “verification”, “release”, “processing”, “refund”, or “recovery” fee.

Safe verification should use the official app already installed, a website typed independently from a trusted source, or contact details obtained independently—not the message itself.

## 4. URL inspection safety

- Parse submitted URLs locally; do not fetch pages, follow redirects, resolve content, or execute scripts.
- Never embed live malicious URLs in demo content.
- Use reserved example domains such as `example.com` or `.example` in fixtures.
- Treat URL structure as indicators, not proof. A shortener or unusual domain is a warning signal; a familiar-looking domain is not proof of legitimacy.
- HTTPS only means a connection uses encryption to that host; it does not prove the host is trustworthy.

## 5. Privacy defaults

- Core analysis runs locally.
- Do not send the user's scanned content to Adaption or any other third-party model/API.
- Do not persist raw messages, URLs, or sensitive user content by default.
- If recent history is implemented, make it opt-in and local; store only the minimum needed, with a clear delete option.
- Avoid collecting phone numbers, names, UPI IDs, account numbers, or other unnecessary personal information in analytics.
- Do not place API keys in frontend code or client-side configuration.

## 6. Incident-response guidance

SIFT's Safety Center should adapt guidance to what the user says happened.

### Received only
- Do not reply, pay, scan QR codes, or open the link.
- Verify the claim through an independently accessed official app/site/contact.
- Preserve the message if the user may need to report it.

### Clicked a link
- Close the page; do not enter more details or download anything.
- If credentials were entered, change them using the official service from a trusted device/session.
- Check account activity and revoke suspicious sessions where appropriate.

### Shared personal data or credentials
- Change affected passwords from the official app/site.
- Revoke sessions and enable appropriate account protections.
- Contact the affected service using independently verified channels.
- If an OTP, UPI PIN, banking password, or card details were exposed, contact the bank/payment provider immediately through official channels.

### Made a payment
- Contact the bank/payment provider immediately using official channels and ask about blocking/raising a dispute.
- In India, direct users to official cybercrime reporting resources, including the national cybercrime portal and 1930 helpline where applicable. Do not invent a case status or guarantee recovery.
- Preserve transaction ID, time, amount, recipient details, and message evidence.
- Warn against recovery agents who demand fees or credentials.

## 7. Dataset safety

- Generate fictional messages and domains.
- Do not include real personal data, actual credentials, operational malware links, or real payment handles.
- Dataset labels are generated suggestions requiring review; they are not ground truth.
- Retain licensing/provenance details for public datasets.

## 8. Known limitations to disclose

The initial prototype does not independently verify sender identity, domain ownership, website reputation, current malware status, or whether a claimed account event is real. It may miss new scam tactics or misclassify unusual legitimate messages. The user must be encouraged to verify important claims independently.
