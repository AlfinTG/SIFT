from app.services.rules import analyze_message_rules


def signal_ids(message: str) -> set[str]:
    return {signal.signal_id for signal in analyze_message_rules(message)}


def test_protective_credential_warning_is_not_a_request() -> None:
    assert "credential_disclosure_request" not in signal_ids(
        "For your security, never share your OTP, password, or UPI PIN with anyone."
    )


def test_later_credential_request_is_not_suppressed_by_protective_language() -> None:
    ids = signal_ids("Never share your OTP with anyone. To unlock your account, reply with your OTP now.")

    assert "credential_disclosure_request" in ids


def test_legitimate_messages_with_scam_keywords_are_not_escalated() -> None:
    messages = [
        "Your parcel is out for delivery today. Track it in the delivery app you normally use.",
        "Payment confirmation: ₹799 was received. Never share your OTP with anyone.",
        "Your internship application was received. There is no fee to apply.",
    ]

    for message in messages:
        assert not ({"credential_disclosure_request", "upfront_job_fee", "upi_refund_manipulation", "reward_claim_fee"} & signal_ids(message))


def test_protective_no_payment_language_is_not_a_payment_demand() -> None:
    messages = [
        "Your internship application is received. Do not pay a registration fee to anyone.",
        "You are a prize winner, but no processing fee is required to claim it.",
        "Refund safety reminder: Never scan the QR code or enter your UPI PIN to receive money.",
    ]

    for message in messages:
        assert not ({"upfront_job_fee", "reward_claim_fee", "upi_refund_manipulation"} & signal_ids(message))


def test_explicit_payment_and_credential_signals_override_low_urgency() -> None:
    ids = signal_ids(
        "Your refund is pending today. Scan the QR code and enter your UPI PIN immediately to receive the amount."
    )

    assert {"upi_refund_manipulation", "urgency_pressure"} <= ids
