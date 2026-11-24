# Consolidated SIFT review package

Only the candidates below require a human decision. Automated checks did not approve any row.
Record `accepted`, `rejected`, or `needs_review` in `consolidated-review-ledger.csv`; accepted rows require a reviewer ID and ISO-8601 timestamp.

## High-priority attention

- Review all SCAM candidates for fictional-brand impersonation, consumer-detection relevance, and naturalness before acceptance.
- Review the LEGITIMATE candidates for accidental scam-like wording and representativeness; they are English-only.
- Do not approve rows solely because structural checks passed.

## Review-ready SCAM candidates

### sift-949c0dfff45e9cd0

- Source: `sift-pilot-v3-scam-fake-job` / `ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv`
- Language: `hinglish`; family: `fake_job_apex_reviewer_hinglish_01`
- Type: `fake_job`
- Message: Namaste! Aapke profile ko dekh kar humein lagta hai ki aap hamari company 'Apex Digital' ke liye perfect fit hain. Hum Part-time Online Reviewer hire kar rahe hain. Kaam bahut simple hai, bas products actually check karke feedback dena hai. Daily earnings ₹2000 se ₹5000 tak ho sakti hain. Interest hone par example.org/job-portal par register karein ya humein reply karein. Limited seats available!
- Rationale: The message uses a common task-based scam pattern, contacting the user unsolicited and promising unrealistically high daily earnings for simple review work without an interview process. It creates artificial urgency to lure victims into a fraudulent registration process.

### sift-5642a873fdc1d0a0

- Source: `sift-pilot-v3-scam-fake-job` / `ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv`
- Language: `en`; family: `fake_job_zenith_logistics_001`
- Type: `fake_job`
- Message: Hello, I am the HR Manager for Zenith Logistics. We have a vacancy for a Part-time Data Entry Specialist. Salary is 2500-4000 INR per day. Work from home. Requirements: Basic computer knowledge and a smartphone. If interested, please message me on WhatsApp for the registration process and to receive your employee ID. Contact: +91-XXXXX-XXXXX. Limited seats available!
- Rationale: The message promises an unrealistically high daily salary for low-skill data entry work, creates urgency with limited seats, and attempts to move communication to a less regulated platform (WhatsApp) where victims are typically asked for registration fees or security deposits.

### sift-8ab62abebd84445e

- Source: `sift-pilot-v3-scam-fake-job` / `ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv`
- Language: `en`; family: `fake_job_high_pay_no_exp`
- Type: `fake_job`
- Message: Urgent Hiring: Remote Data Entry Clerks Needed Immediately! Earn $450/day working from home. No experience required. We are expanding our team at TechGlobal Solutions and need 50 people started by Monday. To apply, simply reply with your full name, address, and a copy of your ID, or click here to register: http://example.com/hire-now. Payment is made via direct deposit within 24 hours of task completion. Don't miss this limited-time opportunity!
- Rationale: The message offers an unrealistically high salary for no-experience work, creates false urgency, and explicitly requests sensitive personal identity documents or directs users to an unverified external link, which are hallmarks of identity theft and advance-fee fraud schemes.

### sift-6957d1d35a13d81f

- Source: `sift-pilot-v3-scam-fake-job` / `ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv`
- Language: `en`; family: `fake_job_telegram_redirect_01`
- Type: `fake_job`
- Message: Hello! I am Sarah from Global Tech Solutions. We are currently hiring for a Remote Data Analyst position. The role involves simple task optimization and pays between $200-$500 daily. No prior experience is required. To start your onboarding process and receive your first assignment, please message our HR manager on Telegram at @GT_Recruiter_Official or visit example.net/careers/apply. We look forward to working with you!
- Rationale: The unsolicited message offers an unrealistically high daily wage for simple tasks requiring no experience, which is typical of task-based employment scams designed to lure victims into paying for training or equipment. It also attempts to migrate communication to Telegram to evade detection.

### sift-8a8613b62abcd0a5

- Source: `sift-pilot-v3-scam-fake-job` / `ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv`
- Language: `en`; family: `fake_job_data_verifier_sms`
- Type: `fake_job`
- Message: Hi! This is Sarah from Global Tech Solutions. We noticed your profile and have an exclusive remote opportunity for you as a Data Verification Specialist. No experience or specific tech skills needed! Earn $50-$100/hour working flexible hours from home. To get started, please reply with your full name and confirm if you have a WhatsApp account so our hiring manager can send you the simple task instructions immediately. Don't miss out!
- Rationale: The message uses unsolicited contact with unrealistic pay for no work, attempts to move communication to an unmonitored platform (WhatsApp), and explicitly requests personal data (full name) before providing any legitimate job details, which are hallmarks of a fake job scam designed for data harvesting or advance fee fraud.

## Review-ready LEGITIMATE candidates

### sift-eb9a4222d7f0a1ff

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `system_log_notification`
- Type: `none`
- Message: Network Log: TCP MTU probing detected path change on interface eth0. New MTU: 1420 bytes. Packet fragmentation disabled. Connection stability optimized for kernel v5.15+. Review full trace at example.org/logs/tcp-dbg-99. No credentials required for read-only access.
- Rationale: The message is a standard network diagnostic log utilizing precise networking terminology and kernel versioning. It poses no security risks, utilizing a reserved example domain for the trace link and explicitly stating that no credentials are needed, which directly counters typical phishing patterns.

### sift-f1beaaa6285e6d3c

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `corporate_expense_approval`
- Type: `none`
- Message: Notification: Your request for a reimbursement of $450.00 for the industry conference has been approved. The funds will be credited to your registered bank account within 3-5 business days. Reference ID: REIMB-99281.
- Rationale: The message contains specific, contextual details regarding a known business event (industry conference) and a precise amount. It references a 'registered bank account,' implying an existing relationship and verified data on file, rather than asking the user to provide new sensitive information. The inclusion of a formal Reference ID and a standard banking timeline (3-5 business days) without any urgent call to action, external links, or requests for credentials indicates a standard administrative notification.

### sift-67b7730cb5bb6dd6

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `infrastructure_security_alert`
- Type: `none`
- Message: Security Notice: A new SSH key was added to your research lab account from IP 192.0.2.14. If this was you, ignore this message. If not, revoke the key immediately at example.org/security. Never share your private key or passphrase with anyone, even support staff.
- Rationale: The message provides a specific, plausible security event (SSH key addition) with a clear conditional instruction (ignore if recognized, act if not). Crucially, it includes proactive security education warning the user never to share credentials with support staff, which is a hallmark of legitimate security communications designed to prevent social engineering. The link uses a reserved example domain, and the tone is informative rather than fear-mongering.

### sift-4759fac73dceb84f

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `billing_reminder`
- Type: `none`
- Message: Urgent: Your monthly credit card payment of $120 is due tomorrow, Oct 15th. To avoid late fees, please pay via the mobile app or your registered net banking portal. Ignore if already paid.
- Rationale: The message provides specific transaction details (amount and date) and directs the user to established, secure channels (mobile app, registered net banking) rather than providing a suspicious external link. The inclusion of 'Ignore if already paid' is a standard customer service practice to reduce confusion, distinguishing it from scam attempts that typically demand immediate action regardless of status.

### sift-2f8ca91de5f39b5e

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `corporate_interview_confirmation_with_security_advisory`
- Type: `none`
- Message: Subject: Interview Confirmation: Senior Finance Role (Req #4922)

Dear Candidate,

This email confirms your upcoming interview for the Senior Accounting position within our Veralto subsidiary. Your interview is scheduled for Tuesday, October 24th, at 2:00 PM PST via Microsoft Teams.

Please note the following compliance reminders per California compensation laws and our internal security protocols:
1. Our recruiters will never ask for your bank account details, social security number, or payment for equipment prior to an official offer letter.
2. Do not share any one-time passwords (OTP) or login credentials with anyone claiming to be from our hiring team.
3. All communication regarding this role will come strictly from our @company.com domain.

If you have questions about the role specifics or need to reschedule, please reply directly to this thread or contact our talent acquisition office. We look forward to discussing your expertise in Workday and financial reporting.

Sincerely,
Talent Acquisition Team
- Rationale: The message is classified as legitimate because it explicitly warns the recipient against common scam tactics (requesting money, SSN, or OTPs) rather than attempting to execute them. It provides specific, verifiable details about the interview (role, time, platform) and establishes a clear, secure communication protocol (@company.com domain). The tone is professional, and the inclusion of compliance reminders regarding California laws indicates a genuine corporate adherence to legal standards rather than an attempt to bypass them.

### sift-0b8116138e602ade

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `firmware_update_notification`
- Type: `none`
- Message: System Update: Valve Index firmware v1.2.4 is ready to install. This patch resolves controller drift issues reported in mixed-reality setups. Connect your base stations via USB-C to proceed. Do not disconnect power during update. Support: example.com/help/index-fw.
- Rationale: The message follows the standard format for a hardware system notification, providing specific version numbers, technical details about the fix (controller drift), and clear safety instructions. The URL uses a reserved example domain, indicating it is a placeholder for documentation rather than a phishing link. There are no elements of urgency, threats, or requests for sensitive information typical of scams.

### sift-b6a31065cf98ea94

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `bank_transaction_alert`
- Type: `none`
- Message: Alert: Your salary credit of ₹45,200 from TechSolutions Ltd has been processed. Current available balance: ₹12,350. Note: Bank officials will never ask for your PIN or OTP over phone or email. Report suspicious calls to 1930. Visit example.com/salary-update for details.
- Rationale: The message is a standard banking notification that provides specific transaction details without requesting sensitive information. It proactively includes a security advisory warning users against sharing credentials and directs them to the official cyber crime helpline, which is characteristic of legitimate customer education rather than a phishing attempt.

### sift-9a0541a55f1bd7bf

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `internal_hr_compliance`
- Type: `none`
- Message: Hi Sarah, this is the HR team. We noticed a discrepancy in your tax filing documents for the current quarter. Please visit the payroll office or check the 'Documents' tab in the employee self-service portal to rectify this by EOD to ensure your salary is credited on time.
- Rationale: The message uses a professional tone appropriate for HR communications and provides specific, safe instructions to resolve the issue through verified internal channels (physical office or established self-service portal) rather than requesting sensitive data via reply or clicking external links. The mention of a consequence (salary delay) is standard procedural information rather than an urgent threat designed to panic the recipient into bypassing security protocols.

### sift-85cfc61fe546eded

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `corporate_compliance_notice`
- Type: `none`
- Message: Subject: Mandatory Compliance Training: Recognizing Recruitment Scams

To All Staff,

As part of Sharp HealthCare's annual compliance requirement, all employees must complete the updated module on "Identifying Fraudulent Job Offers and Impersonation Attempts." This training is critical given the rise in scams targeting our clinical staff and applicants.

Access the training here: https://example.com/compliance-training

Key takeaways you will learn:
- Legitimate HR will never request gift cards, wire transfers, or crypto payments for equipment.
- We do not conduct interviews solely via text message or Telegram.
- Never share your Multi-Factor Authentication (MFA) codes or passwords with anyone, even if they claim to be from IT or HR.

Completion is required by end-of-month. This is a standard safety reminder; no personal data update is needed via this email. If you have questions about the curriculum, contact the Learning & Development department directly.

Stay safe,
Human Resources Department
- Rationale: The message is an internal corporate communication focused on security awareness and compliance training. It explicitly warns against common scam tactics (gift cards, MFA sharing) rather than employing them. The link uses a reserved example domain, and the text explicitly states that no personal data update is required, removing the primary incentive for phishing. The tone is instructional and authoritative without creating artificial urgency for immediate action beyond completing a training module.

### sift-f73552c902b59781

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `transactional_reward_update`
- Type: `none`
- Message: Hello! You have received a cashback reward of ₹50 for your last transaction. The amount has been credited to your wallet. To redeem these points for future vouchers, check the 'Rewards' tab in the app. T&C apply.
- Rationale: The message informs the user of a credited amount without requesting any action outside the official application environment. It directs the user to an internal tab ('Rewards') rather than providing external links or asking for sensitive data. The inclusion of 'T&C apply' is standard for legitimate promotional communications.

### sift-c5c662ec08d6ca86

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `internal_research_invitation`
- Type: `none`
- Message: Subject: Q3 Productivity Metrics & Well-being Survey Invitation

Hello,

Our think tank has completed the longitudinal analysis on hybrid work ecosystems for Q3. We are inviting select department heads to participate in a follow-up focus group to discuss the intersection of digital collaboration tools and employee burnout rates.

Your participation is voluntary and data will be anonymized. To register your interest, please visit our internal survey page: https://example.org/workforce-study.

Security Notice: Legitimate research teams do not request credit card information or personal identification numbers (PINs) to participate in internal studies. Any message asking for such details in relation to this survey is fraudulent. Please verify all links by navigating manually through the company intranet if you are unsure.

Thank you for contributing to our data-driven approach to sustainable work models.

Regards,
Future of Work Research Lead
- Rationale: The message explicitly warns recipients against providing sensitive financial or identity information, which is a strong indicator of legitimacy. It encourages manual verification of links via the company intranet rather than relying solely on the provided URL. The content is professionally written, contextually appropriate for an internal research initiative, and lacks urgency or threats typical of phishing attempts.

### sift-4394838d7b351507

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `internal_hr_policy_update`
- Type: `none`
- Message: Subject: Action Required: Update Your Hybrid Work Preference Profile

Dear Team Member,

As part of our ongoing commitment to optimizing workplace autonomy and well-being, we are rolling out an updated module within our HR portal. This update allows you to refine your hybrid work schedule preferences for the upcoming quarter based on the latest organizational psychology research we've adopted.

Please log in to the secure employee portal at https://example.com/hr-portal to review your current settings. Note: Our IT security team reminds you that we will NEVER ask for your password or OTP via email. If you receive a call requesting verification codes, hang up immediately and report it to security.

This is a routine administrative update. No immediate action is required other than logging in at your convenience before Friday.

Best regards,
The Workplace Strategy Team
- Rationale: The message is classified as legitimate because it explicitly warns users against sharing credentials, a behavior opposite to phishing attempts. It provides a logical business context for the update (organizational psychology research) and uses low-pressure language ('at your convenience') rather than creating artificial urgency. The link directs to a reserved example domain, and the tone is consistent with internal corporate communications.

### sift-9b021d1c408f31e2

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `system_status_update`
- Type: `none`
- Message: Alert: Your Sketchfab asset 'LowPoly_City_v2' has passed PBR compliance review. Polygon count: 4,802 (within mobile budget). License: CC-BY 4.0 verified. No action required; metadata updated in pipeline. Download receipt: example.net/receipts/9921.
- Rationale: The message provides specific, verifiable technical details regarding a 3D asset (polygon count, license type) and explicitly states that no user action is required. It functions as a standard system status update rather than a request for credentials, payment, or urgent interaction, which are hallmarks of phishing attempts. The inclusion of a passive receipt link to a reserved domain further supports its nature as an informational log rather than a social engineering lure.

### sift-4027c6f7de6a43eb

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `Banking KYC Notification`
- Type: `none`
- Message: Your account KYC update is pending. Please visit your nearest branch with your original Aadhaar and PAN card to complete the verification process. Do not share your OTP or password with anyone calling on your behalf.example.com/branch-locator
- Rationale: The message directs the user to visit a physical bank branch for in-person verification with original documents, rather than requesting sensitive information via a link or phone call. It also includes a standard security warning against sharing OTPs or passwords, which aligns with legitimate banking protocols. The provided URL is intended for locating a branch, not for data entry.

### sift-4ad3aa5c37cca168

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `logistics_delivery_update`
- Type: `none`
- Message: Delivery Update: Your package containing office supplies is out for delivery and expected by 6 PM today. Please have your ID ready for verification upon receipt. This is a legitimate notification from FastShip Logistics. We do not request payment via link to release parcels. Contact support at example.com/help if unavailable.
- Rationale: Although delivery alerts are frequently used in phishing, this message is classified as legitimate because it provides a routine status update without demanding urgent action or payment. It actively protects the user by explicitly stating that the company does not request payments via links, and it directs users to a safe, reserved domain for support rather than a suspicious URL.

### sift-ee87cf567638074e

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `retention_promotion`
- Type: `none`
- Message: Special Offer: Get an additional 5% cashback on your next utility bill payment using the 'SAVE5' promo code in the payments section of our app. Valid until Sunday. T&C apply.
- Rationale: The message directs the user to perform an action strictly within the official application's interface ('payments section of our app') rather than clicking an external link or providing sensitive data. It uses standard marketing language for a cashback promotion, includes a reference to terms and conditions, and does not create a sense of panic or request confidential information, which are hallmarks of legitimate corporate communications.

### sift-df1d7c91600baf4f

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `security_alert_protective`
- Type: `none`
- Message: Urgent Security Alert: We detected a login attempt from a new device (iPhone 14) in Mumbai. If this wasn't you, your account may be at risk. Do NOT share your OTP or PIN with anyone. Verify now: https://example.com/verify
- Rationale: This is a legitimate security notification because it explicitly warns the user AGAINST sharing sensitive credentials (OTP/PIN), which is a hallmark of genuine bank communications. Scammers typically ask for these details. The link uses a reserved example domain for safety, and the message provides a clear, non-deceptive call to action to verify via a official channel rather than replying with data.

### sift-75d5f96b68fb0e14

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `recruitment_communication`
- Type: `none`
- Message: Hi Rahul, regarding the Finance Analyst role you applied for, we'd like to schedule a second round interview. Please share your availability for next Tuesday and Wednesday. No payment is required for the recruitment process. Best, HR Team.
- Rationale: The message references a specific prior application and outlines a clear next step in the hiring pipeline. By proactively stating that no payment is needed, it transparently distinguishes itself from common recruitment scams, aligning with legitimate corporate hiring practices.

### sift-3b11a4a27c3110e6

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `E-commerce Refund Notification`
- Type: `none`
- Message: Refund Initiated: Your return for Order #99821 (₹1,299) has been approved. The amount will be credited to your source account within 5-7 working days. Transaction ID: REF7721. Reminder: Genuine refunds never require you to scan a QR code or share your CVV. Track status at example.net/returns.
- Rationale: This message is a standard transactional update that provides specific details without requesting sensitive information. It explicitly warns the user against common fraud techniques such as QR scanning or CVV sharing, which is a hallmark of legitimate service providers.

### sift-d50a9365b85081f6

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `corporate_hr_notification`
- Type: `none`
- Message: Hi Team, the quarterly performance reviews are now open. Please schedule your 1:1 with your manager via the calendar link in the company intranet. Ensure your self-assessment is submitted before the meeting to avoid delays in the appraisal process.
- Rationale: The message refers to internal company processes (quarterly reviews, 1:1s, self-assessments) and directs the user to the company intranet rather than an external or suspicious URL. The tone is professional and instructional, typical of HR communications, with no urgency tactics, threats, or requests for sensitive personal data.

### sift-50c6fc02650818d3

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `service_completion_alert`
- Type: `none`
- Message: Render Complete: Your DALL-E 3 batch #8821 (prompt: 'cyberpunk street scene') has finished processing. 4/50 images flagged for manual review due to anatomical artifacts common in generative models. View results at example.net/gallery/8821. No payment info needed.
- Rationale: The message provides specific, plausible technical details regarding the rendering process (anatomical artifacts in generative models) and explicitly states that no payment information is required, which negates common phishing motives. The use of a reserved example domain and the context of a completed batch job align with standard automated service notifications rather than fraudulent activity.

### sift-ed0bd4f66c2c0575

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `official_job_offer`
- Type: `none`
- Message: Dear Candidate, thank you for interviewing with us. We are pleased to offer you the position. Please check your email for the official offer letter. Note: We will never ask you to pay for training, equipment, or security deposits during the hiring process.
- Rationale: The message follows standard professional hiring protocols by directing the candidate to an official email for documentation. Crucially, it explicitly warns against common recruitment scams involving upfront payments for training or equipment, which is a strong indicator of legitimacy rather than deception.

### sift-a4c6de49283ff819

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `banking_kyc_security_alert`
- Type: `none`
- Message: IMPORTANT: Your bank account KYC is pending. To avoid temporary service interruption, please visit your nearest branch with your original PAN and Aadhaar card. We will NEVER ask you to click a link or share your OTP over the phone to complete this process.
- Rationale: This message is classified as legitimate because it adheres to secure banking protocols by requiring in-person verification rather than remote data submission. It proactively warns users against common phishing tactics like clicking links or sharing OTPs, which is characteristic of authentic bank security advisories.

### sift-f93442934ec70d0f

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `security_alert_protective`
- Type: `none`
- Message: Alert from SecureBank: We detected a login attempt on your account from a new device (IP: 192.0.2.1). If this was not you, please reset your password immediately at example.com/security. Remember, we will NEVER ask for your OTP, PIN, or password via SMS or phone call.
- Rationale: This is a legitimate security notification. While it mentions a suspicious login and urges immediate action (traits often found in scams), it explicitly warns the user NOT to share credentials (OTP/PIN), which is the hallmark of a genuine protective message. Scammers typically try to extract these secrets, not warn against sharing them. The link uses a reserved example domain, and the tone is advisory rather than threatening.

### sift-d7269ae1e0df403d

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `security_alert_protective`
- Type: `none`
- Message: Bank Alert: We detected a new sign-in to your account from a Windows device in Mumbai. If this wasn't you, please open our official app immediately to secure your profile. Do not reply with your OTP or PIN. Ref: 9921.
- Rationale: This is a legitimate security alert because it explicitly warns the user NOT to share sensitive credentials (OTP/PIN) and directs them to verify activity through the official app rather than clicking a link or replying to the message. Scammers typically attempt to harvest these details, whereas this message protects them.

### sift-6e9b5ecbbee34bbe

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `corporate_recruitment_onboarding`
- Type: `none`
- Message: Your application for the Senior Project Manager role has progressed to the final stage. Please log into our secure candidate portal at https://example.com/careers to upload your professional references and complete the background check authorization form. Failure to do so by Friday may delay your onboarding.
- Rationale: The message describes a standard corporate recruitment process, directing the candidate to a secure portal for routine onboarding documentation. The urgency regarding the Friday deadline aligns with typical hiring schedules rather than malicious pressure. Furthermore, it uses a reserved example domain and does not request sensitive data or payments directly in the text.

### sift-ab7060712d15c2f6

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `security_alert_protective`
- Type: `none`
- Message: Urgent Security Alert: We detected a login attempt from a new device (Chrome on Windows) at 10:42 AM IST. If this was you, no action is needed. If not, please reset your password immediately via the official app. Note: Our team will NEVER ask for your OTP, PIN, or password via this message or any call. Stay safe.
- Rationale: This message uses urgency typical of scams but directs the user to a safe, self-service action (reset via official app) rather than clicking a link or replying. Crucially, it explicitly warns against sharing credentials, which is a hallmark of legitimate bank security communications, not scams.

### sift-879148aa33fda8fd

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `banking_transaction_alert`
- Type: `none`
- Message: Transaction Alert: A refund of $45.99 from Merchant X has been credited to your account ending in 1234. If you did not expect this or suspect an error, please log in to your official banking app to raise a dispute.
- Rationale: This message is a standard transactional notification that follows secure communication protocols. It avoids creating a sense of panic and does not contain clickable links or requests for credentials. Instead, it directs the user to their trusted, official banking application to resolve any issues, and includes partial account details with specific refund amounts, which is a hallmark of legitimate banking communications.

### sift-176fe2f214d629cf

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `Internal Compliance Notification`
- Type: `none`
- Message: URGENT: All employees must complete the mandatory Compliance and Ethics training module by tomorrow. Please use your corporate SSO credentials to log in at https://example.net/learning. This is a prerequisite for the annual bonus cycle.
- Rationale: The message originates from an internal corporate context requiring mandatory training, a standard business procedure. The link uses a reserved example domain rather than a malicious lookalike, and the request to use existing corporate SSO credentials is consistent with legitimate internal portal access protocols. The urgency and bonus linkage are typical drivers for internal policy adherence rather than indicators of external fraud in this specific simulated context.

### sift-b7233437df5ea932

- Source: `sift-pilot-v2-legitimate-40` / `ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv`
- Language: `en`; family: `security_login_alert`
- Type: `none`
- Message: Important Security Notice: We detected a login attempt on your account from a new device in Mumbai. If this was you, no action is needed. If not, your account is temporarily locked for safety. Do not share your OTP with anyone claiming to unlock it. Reset your password securely at example.org/login-help.
- Rationale: The message adheres to standard security protocols by proactively warning users against sharing OTPs with third parties. It directs users to a secure, reserved example domain for self-service password resets rather than soliciting credentials directly, avoiding threatening language or urgent payment demands.

## Rejected and unresolved source records

- The v3 fake-job raw batch has three conversion rejections: unsupported `medium` difficulty, a likely identifier/email safety hit, and malformed completion JSON.
- The v2 LEGITIMATE raw batch has ten pre-existing conversion rejections; see its `rejected.csv`.
- Both duplicate v2 SCAM raw exports remain excluded because they are bulk-array completions, not safely convertible per-message canonical records. Their existing diagnostic must not be treated as approved training data.

## Audit notes

- Exact duplicate findings: 0
- Near-duplicate candidates: 0
- Repeated template families: 1
- No AMBIGUOUS candidate was produced by the eligible inputs.
