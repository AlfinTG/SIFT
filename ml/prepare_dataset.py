"""Convert an Adaption instruction-data JSONL export into SIFT's CSV contract.

This script is intentionally offline. It reads an immutable raw export, writes
derived CSV files, and never sends rows to a service. Rows that cannot meet the
contract are recorded with a reason instead of being silently repaired.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from urllib.parse import urlsplit
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANONICAL_FIELDS = [
    "sample_id",
    "message_text",
    "label",
    "scam_type",
    "language",
    "channel",
    "tactics",
    "evidence_quotes",
    "rationale",
    "difficulty",
    "source",
    "source_batch",
    "generation_prompt_version",
    "template_family",
    "review_status",
]
REJECTION_FIELDS = ["row_number", "reason", "raw_row"]
VALID_LABELS = {"SCAM", "LEGITIMATE", "AMBIGUOUS"}
VALID_SCAM_TYPES = {"fake_job", "phishing_kyc", "upi_payment", "reward_lottery", "other", "none", ""}
VALID_LANGUAGES = {"en", "hi", "hinglish", "mixed"}
VALID_DIFFICULTIES = {"easy", "hard_negative", "ambiguous", "edge_case", ""}
RESERVED_URL_HOSTS = {"example.com"}
MESSAGE_BLOCK = re.compile(r"MESSAGE_TO_CLASSIFY_BEGIN\s*\n(.*?)\n\s*MESSAGE_TO_CLASSIFY_END", re.DOTALL)
URL_PATTERN = re.compile(r"(?:https?://|www\.)[^\s<>\"']+", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
UPI_PATTERN = re.compile(r"\b[\w.-]{2,}@[\w.-]{2,}\b", re.IGNORECASE)
CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
OTP_PATTERN = re.compile(r"\b(?:otp|pin|cvv|password)\s*(?:is|:|-)?\s*\d{3,8}\b", re.IGNORECASE)


@dataclass(frozen=True)
class ConversionSummary:
    accepted: int
    ambiguous: int
    rejected: int
    labels: dict[str, int]


def _as_json_string(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _prompt_from(raw: dict[str, Any]) -> str:
    for key in ("enhanced_prompt", "prompt", "original_prompt"):
        value = raw.get(key)
        if isinstance(value, str):
            return value
    raise ValueError("missing an enhanced_prompt, prompt, or original_prompt string")


def _completion_from(raw: dict[str, Any]) -> dict[str, Any]:
    for key in ("completion", "output", "response"):
        value = raw.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as error:
                raise ValueError(f"{key} is not valid JSON: {error.msg}") from error
            if isinstance(parsed, dict):
                return parsed
            raise ValueError(f"{key} JSON must be an object")
    raise ValueError("missing completion, output, or response")


def _extract_message(prompt: str) -> str:
    match = MESSAGE_BLOCK.search(prompt)
    if not match:
        raise ValueError("missing MESSAGE_TO_CLASSIFY delimiters")
    message = match.group(1).strip()
    if not message:
        raise ValueError("message block is empty")
    return message


def _required_string(completion: dict[str, Any], field: str) -> str:
    value = completion.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_string(completion: dict[str, Any], field: str) -> str:
    value = completion.get(field, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value.strip()


def _string_list(completion: dict[str, Any], field: str) -> list[str]:
    value = completion.get(field, [])
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{field} must be a list of non-empty strings")
    return [item.strip() for item in value]


def _sample_id(source_batch: str, message: str) -> str:
    digest = hashlib.sha256(f"{source_batch}\n{message}".encode("utf-8")).hexdigest()[:16]
    return f"sift-{digest}"


def _validate_synthetic_safety(message: str) -> None:
    """Reject likely live destinations or sensitive identifiers in synthetic rows."""

    for url in URL_PATTERN.findall(message):
        parsed = urlsplit(url if url.lower().startswith(("http://", "https://")) else f"https://{url}")
        host = (parsed.hostname or "").lower()
        if host not in RESERVED_URL_HOSTS and not host.endswith(".example"):
            raise ValueError("message contains a non-reserved live URL")
    if PHONE_PATTERN.search(message):
        raise ValueError("message contains a possible real phone number")
    if UPI_PATTERN.search(message):
        raise ValueError("message contains a possible UPI identifier")
    if CARD_PATTERN.search(message):
        raise ValueError("message contains a possible payment-card number")
    if OTP_PATTERN.search(message):
        raise ValueError("message contains a possible credential or OTP value")


def canonicalize_row(raw: dict[str, Any], *, source_batch: str, generation_prompt_version: str) -> dict[str, str]:
    """Validate and convert one instruction-data row to the canonical schema."""

    message = _extract_message(_prompt_from(raw))
    completion = _completion_from(raw)
    label = _required_string(completion, "label").upper()
    if label not in VALID_LABELS:
        raise ValueError(f"label must be one of {sorted(VALID_LABELS)}")

    scam_type = _optional_string(completion, "scam_type").lower()
    if scam_type not in VALID_SCAM_TYPES:
        raise ValueError("scam_type is not recognized")
    if label == "LEGITIMATE" and scam_type not in {"", "none"}:
        raise ValueError("LEGITIMATE rows must use scam_type none or an empty value")
    if label == "LEGITIMATE":
        scam_type = ""
    if label == "SCAM" and scam_type in {"", "none"}:
        raise ValueError("SCAM rows require a specific scam_type")

    language = _required_string(completion, "language").lower()
    if language not in VALID_LANGUAGES:
        raise ValueError("language is not recognized")
    difficulty = _optional_string(completion, "difficulty").lower()
    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError("difficulty is not recognized")

    tactics = _string_list(completion, "tactics")
    evidence_quotes = _string_list(completion, "evidence_quotes")
    if not evidence_quotes:
        raise ValueError("evidence_quotes must contain at least one exact message substring")
    for quote in evidence_quotes:
        if quote not in message:
            raise ValueError("each evidence_quotes entry must appear exactly in message_text")
    _validate_synthetic_safety(message)

    return {
        "sample_id": _sample_id(source_batch, message),
        "message_text": message,
        "label": label,
        "scam_type": scam_type,
        "language": language,
        "channel": _optional_string(completion, "channel").lower(),
        "tactics": _as_json_string(tactics),
        "evidence_quotes": _as_json_string(evidence_quotes),
        "rationale": _required_string(completion, "rationale"),
        "difficulty": difficulty,
        "source": "adaption_synthetic",
        "source_batch": source_batch,
        "generation_prompt_version": generation_prompt_version,
        "template_family": _optional_string(completion, "template_family"),
        "review_status": "unreviewed",
    }


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def convert_jsonl(
    raw_path: Path,
    output_directory: Path,
    *,
    source_batch: str,
    generation_prompt_version: str = "",
) -> ConversionSummary:
    """Convert a JSONL export, preserving invalid rows in a rejection report."""

    accepted: list[dict[str, str]] = []
    ambiguous: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    seen_messages: set[str] = set()

    with raw_path.open(encoding="utf-8") as file:
        for row_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                if not isinstance(raw, dict):
                    raise ValueError("JSONL row must be an object")
                row = canonicalize_row(raw, source_batch=source_batch, generation_prompt_version=generation_prompt_version)
                duplicate_key = " ".join(row["message_text"].casefold().split())
                if duplicate_key in seen_messages:
                    raise ValueError("duplicate message_text in this conversion run")
                seen_messages.add(duplicate_key)
                (ambiguous if row["label"] == "AMBIGUOUS" else accepted).append(row)
            except (json.JSONDecodeError, ValueError) as error:
                rejected.append({"row_number": str(row_number), "reason": str(error), "raw_row": line.rstrip("\n")})

    _write_csv(output_directory / "accepted.csv", CANONICAL_FIELDS, accepted)
    _write_csv(output_directory / "ambiguous.csv", CANONICAL_FIELDS, ambiguous)
    _write_csv(output_directory / "rejected.csv", REJECTION_FIELDS, rejected)
    label_counts = Counter(row["label"] for row in [*accepted, *ambiguous])
    return ConversionSummary(len(accepted), len(ambiguous), len(rejected), dict(label_counts))


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a SIFT Adaption instruction-data JSONL export.")
    parser.add_argument("raw_path", type=Path, help="Immutable JSONL export from the dataset provider")
    parser.add_argument("--output-directory", type=Path, required=True, help="Directory for derived CSV files")
    parser.add_argument("--source-batch", required=True, help="Stable identifier for this generation batch")
    parser.add_argument("--generation-prompt-version", default="", help="Prompt version recorded with every converted row")
    arguments = parser.parse_args()

    summary = convert_jsonl(
        arguments.raw_path,
        arguments.output_directory,
        source_batch=arguments.source_batch,
        generation_prompt_version=arguments.generation_prompt_version,
    )
    print(json.dumps(summary.__dict__, indent=2))


if __name__ == "__main__":
    main()
