"""Safe next-step guidance, selected from the user's stated incident status."""

from app.schemas.analysis import IncidentStatus


GUIDANCE: dict[IncidentStatus, list[str]] = {
    "received_only": [
        "Do not reply, pay, scan a QR code, or open the link from the message.",
        "Verify the claim through an official app, website, or contact method you find independently.",
    ],
    "clicked_link": [
        "Close the page and do not enter details or download anything further.",
        "If you entered credentials, change them through the official service and review account activity.",
    ],
    "shared_personal_data": [
        "Contact the affected service through an independently verified official channel.",
        "Watch for follow-up impersonation attempts and avoid sharing further details.",
    ],
    "shared_credentials": [
        "Change affected passwords through the official service and revoke suspicious sessions where available.",
        "If banking credentials, an OTP, or a UPI PIN was exposed, contact the bank or payment provider immediately using official channels.",
    ],
    "made_payment": [
        "Contact the bank or payment provider immediately through official channels to ask about blocking or disputing the transaction.",
        "Preserve the transaction ID, time, amount, recipient details, and the message; beware of recovery agents who request fees or credentials.",
    ],
}


def next_steps_for(incident_status: IncidentStatus) -> list[str]:
    return GUIDANCE[incident_status]
