import csv
import json

import pytest

from ml.prepare_dataset import canonicalize_row, convert_jsonl


def instruction_row(message: str, completion: dict[str, object]) -> dict[str, object]:
    return {
        "enhanced_prompt": f"Review this message.\n\nMESSAGE_TO_CLASSIFY_BEGIN\n{message}\nMESSAGE_TO_CLASSIFY_END\n\nReturn JSON.",
        "completion": json.dumps(completion),
    }


def scam_completion(message: str) -> dict[str, object]:
    return {
        "label": "SCAM",
        "scam_type": "fake_job",
        "language": "en",
        "channel": "chat",
        "tactics": ["upfront_fee"],
        "evidence_quotes": [message],
        "rationale": "The message requests a fee for an employment opportunity.",
        "difficulty": "easy",
        "template_family": "job-fee-01",
    }


def test_canonicalize_extracts_only_delimited_message() -> None:
    message = "Pay ₹799 to confirm your internship seat."
    row = canonicalize_row(instruction_row(message, scam_completion(message)), source_batch="pilot-1", generation_prompt_version="v1")

    assert row["message_text"] == message
    assert "MESSAGE_TO_CLASSIFY_BEGIN" not in row["message_text"]
    assert row["review_status"] == "unreviewed"


def test_canonicalize_rejects_evidence_not_present_in_message() -> None:
    message = "Normal delivery update."
    completion = scam_completion("not in the message")

    with pytest.raises(ValueError, match="evidence_quotes"):
        canonicalize_row(instruction_row(message, completion), source_batch="pilot-1", generation_prompt_version="v1")


def test_convert_separates_ambiguous_and_rejects_duplicates(tmp_path) -> None:
    scam_message = "Pay ₹799 to confirm your internship seat."
    ambiguous_message = "Your account needs attention."
    ambiguous_completion = {
        "label": "AMBIGUOUS",
        "scam_type": "none",
        "language": "en",
        "channel": "sms",
        "tactics": [],
        "evidence_quotes": ["needs attention"],
        "rationale": "The message lacks enough context to classify.",
        "difficulty": "ambiguous",
        "template_family": "account-vague-01",
    }
    raw_path = tmp_path / "pilot.jsonl"
    raw_path.write_text(
        "\n".join(
            json.dumps(row)
            for row in [
                instruction_row(scam_message, scam_completion(scam_message)),
                instruction_row(ambiguous_message, ambiguous_completion),
                instruction_row(scam_message, scam_completion(scam_message)),
            ]
        ),
        encoding="utf-8",
    )

    summary = convert_jsonl(raw_path, tmp_path / "converted", source_batch="pilot-1", generation_prompt_version="v1")

    assert summary.accepted == 1
    assert summary.ambiguous == 1
    assert summary.rejected == 1
    with (tmp_path / "converted" / "ambiguous.csv").open(encoding="utf-8") as file:
        assert list(csv.DictReader(file))[0]["label"] == "AMBIGUOUS"


def test_canonicalize_requires_nonempty_evidence_and_legitimate_none_subtype() -> None:
    message = "For your security, never share your OTP with anyone."
    completion = {
        "label": "LEGITIMATE", "scam_type": "fake_job", "language": "en", "channel": "sms",
        "tactics": [], "evidence_quotes": [], "rationale": "This is a warning.",
        "difficulty": "hard_negative", "template_family": "sift-pilot-v1-legitimate-phishing_kyc-01",
    }
    with pytest.raises(ValueError, match="LEGITIMATE rows"):
        canonicalize_row(instruction_row(message, completion), source_batch="pilot", generation_prompt_version="v1")

    completion["scam_type"] = "none"
    with pytest.raises(ValueError, match="evidence_quotes"):
        canonicalize_row(instruction_row(message, completion), source_batch="pilot", generation_prompt_version="v1")


def test_canonicalize_rejects_live_urls_and_possible_phone_numbers() -> None:
    completion = scam_completion("Visit https://not-reserved.invalid now")
    with pytest.raises(ValueError, match="live URL"):
        canonicalize_row(
            instruction_row("Visit https://not-reserved.invalid now", completion), source_batch="pilot", generation_prompt_version="v1"
        )

    completion = scam_completion("Call 9876543210 to confirm your internship.")
    with pytest.raises(ValueError, match="phone number"):
        canonicalize_row(
            instruction_row("Call 9876543210 to confirm your internship.", completion), source_batch="pilot", generation_prompt_version="v1"
        )

    completion = scam_completion("Use www.not-reserved.invalid to confirm your internship.")
    with pytest.raises(ValueError, match="live URL"):
        canonicalize_row(
            instruction_row("Use www.not-reserved.invalid to confirm your internship.", completion), source_batch="pilot", generation_prompt_version="v1"
        )
