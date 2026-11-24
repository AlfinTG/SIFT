"""Contextual, deterministic safety rules for message analysis.

Rules emit evidence only when their context is present. They are deliberately
separate from the future classifier so an explicit dangerous request is never
suppressed by a low model score.
"""

import re

from app.schemas.analysis import EvidenceSignal


def _signal(
    signal_id: str,
    evidence: str,
    reason: str,
    severity: str,
    recommended_action: str,
) -> EvidenceSignal:
    return EvidenceSignal(
        source="rule",
        signal_id=signal_id,
        evidence=evidence,
        reason=reason,
        severity=severity,  # type: ignore[arg-type]
        recommended_action=recommended_action,
    )


def _first_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(0) if match else None


def _first_actionable_match(pattern: str, text: str) -> str | None:
    """Return the first match that is not phrased as protective advice."""

    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        clause_start = max(
            text.rfind(".", 0, match.start()),
            text.rfind("!", 0, match.start()),
            text.rfind("?", 0, match.start()),
            text.rfind("\n", 0, match.start()),
        ) + 1
        preceding_text = text[clause_start:match.start()]
        if re.search(r"\b(?:never|do\s+not|don't|avoid)\b", preceding_text, re.IGNORECASE):
            continue
        return match.group(0)
    return None


def _is_no_payment_advice(evidence: str, text: str) -> bool:
    """Avoid treating an explicit warning that no payment is required as a demand."""

    start = text.casefold().find(evidence.casefold())
    context = text[max(0, start - 48) : start + len(evidence) + 48] if start >= 0 else evidence
    return bool(
        re.search(
            r"\b(?:no|without)\s+(?:\w+\s+){0,2}(?:fee|fees|payment)|"
            r"\b(?:do\s+not|don't|never)\s+(?:\w+\s+){0,3}(?:pay|deposit|transfer)",
            context,
            re.IGNORECASE,
        )
    )


def _credential_request_match(text: str) -> str | None:
    """Find a credential request while preserving protective-warning context.

    A statement such as ``Never share your OTP`` is a benign warning. The same
    statement must not suppress a later explicit request in the message, so each
    candidate is evaluated using only the words immediately before that request.
    """

    pattern = re.compile(
        r"\b(?:share|provide|send|reply\s+with|tell\s+us|enter|submit|disclose)\b[^.!?\n]{0,80}\b(?:otp|upi\s*pin|pin|password|cvv|recovery\s+code)\b",
        re.IGNORECASE,
    )
    return _first_actionable_match(pattern.pattern, text)


def analyze_message_rules(message: str) -> list[EvidenceSignal]:
    """Return context-sensitive findings for known high-risk scam patterns."""

    findings: list[EvidenceSignal] = []
    text = message.strip()
    if not text:
        return findings

    credential_request = _credential_request_match(text)
    if credential_request:
        findings.append(
            _signal(
                "credential_disclosure_request",
                credential_request,
                "The message asks you to disclose a security credential. Legitimate support should not ask for these details in a message.",
                "critical",
                "Do not share the credential. Contact the service through its official app or a contact method you find independently.",
            )
        )

    job_fee = _first_match(
        r"\b(?:pay|deposit|transfer|registration|processing|training|security)\b.{0,70}\b(?:fee|fees|₹\s?\d+[\d,]*|rs\.?\s?\d+[\d,]*)\b",
        text,
    )
    job_context = re.search(r"\b(?:job|internship|placement|recruit(?:ment|er)|joining|offer letter|shortlisted)\b", text, re.I)
    if job_fee and job_context and not _is_no_payment_advice(job_fee, text):
        findings.append(
            _signal(
                "upfront_job_fee",
                job_fee,
                "A payment appears to be required in connection with an employment opportunity, which is a strong warning sign.",
                "high",
                "Do not pay. Verify the employer through an independently found official channel.",
            )
        )

    refund_manipulation = _first_actionable_match(
        r"\b(?:scan\s+(?:the\s+)?qr(?:\s+code)?|qr\s+scan|enter\s+(?:your\s+)?upi\s*pin|approve\s+(?:the\s+)?collect)\b",
        text,
    )
    payment_context = re.search(r"\b(?:refund|refunds|payment|receive\s+(?:the\s+)?amount|cashback)\b", text, re.I)
    if refund_manipulation and payment_context:
        findings.append(
            _signal(
                "upi_refund_manipulation",
                refund_manipulation,
                "The message pairs a refund or payment claim with an action that can authorize a payment or expose a PIN.",
                "critical",
                "Do not scan the QR code, enter a UPI PIN, or approve a collect request. Check the transaction only in the official payment app.",
            )
        )

    account_threat = _first_match(
        r"\b(?:account|card|service)\b.{0,50}\b(?:blocked|restricted|suspended|closed|deactivated)\b",
        text,
    )
    if account_threat:
        findings.append(
            _signal(
                "account_pressure",
                account_threat,
                "The message uses a threat about account access to pressure a quick response.",
                "medium",
                "Pause and check the account only through the official app or a website you access independently.",
            )
        )

    reward_fee = _first_match(
        r"\b(?:prize|winner|lottery|reward)\b.{0,100}\b(?:fee|tax|processing|pay|payment)\b",
        text,
    )
    if reward_fee and not _is_no_payment_advice(reward_fee, text):
        findings.append(
            _signal(
                "reward_claim_fee",
                reward_fee,
                "The message links an unexpected reward to a payment or processing demand.",
                "high",
                "Do not pay a claim fee or share details. Verify any offer through an independently found official channel.",
            )
        )

    urgency = _first_match(r"\b(?:within\s+\d+\s+(?:minutes?|hours?)|today|immediately|urgent(?:ly)?|last\s+chance)\b", text)
    if urgency:
        findings.append(
            _signal(
                "urgency_pressure",
                urgency,
                "The message creates time pressure, which can discourage careful verification.",
                "low",
                "Take time to verify the claim through a trusted, independently found channel.",
            )
        )

    return findings
