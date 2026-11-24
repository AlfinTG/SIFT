"""Local URL parsing only. This module never performs DNS or HTTP operations."""

import ipaddress
import re
from urllib.parse import urlparse

from app.schemas.analysis import EvidenceSignal, UrlInspection


URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,;:!?)]}"
SHORTENER_HOSTS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rb.gy"}


def extract_urls(text: str) -> list[str]:
    """Extract HTTP(S) URLs from text without dereferencing them."""

    return [match.group(0).rstrip(TRAILING_PUNCTUATION) for match in URL_PATTERN.finditer(text)]


def _signal(signal_id: str, evidence: str, reason: str, severity: str, action: str) -> EvidenceSignal:
    return EvidenceSignal(
        source="url",
        signal_id=signal_id,
        evidence=evidence,
        reason=reason,
        severity=severity,  # type: ignore[arg-type]
        recommended_action=action,
    )


def inspect_url(submitted_url: str) -> UrlInspection:
    """Analyze a URL's text structure using only Python's standard library."""

    candidate = submitted_url.strip()
    try:
        parsed = urlparse(candidate)
    except ValueError:
        return UrlInspection(submitted_url=submitted_url, valid=False, error="The URL could not be parsed safely.")

    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return UrlInspection(
            submitted_url=submitted_url,
            valid=False,
            error="Enter a complete HTTP or HTTPS URL with a host, for example https://example.com.",
        )

    host = parsed.hostname.lower()
    signals: list[EvidenceSignal] = []
    cautious_action = "Do not open the link from the message. Verify the claim through an independently found official channel."

    if parsed.username or parsed.password:
        signals.append(
            _signal(
                "embedded_url_credentials",
                parsed.netloc,
                "The URL contains a username or password component, which can obscure the actual destination host.",
                "high",
                cautious_action,
            )
        )

    is_ip_address = False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        is_ip_address = True
        signals.append(
            _signal(
                "ip_address_host",
                host,
                "The URL uses a numeric IP address instead of a domain name. This is a structural warning sign, not proof of harm.",
                "medium",
                cautious_action,
            )
        )

    if host in SHORTENER_HOSTS or any(host.endswith(f".{shortener}") for shortener in SHORTENER_HOSTS):
        signals.append(
            _signal(
                "url_shortener",
                host,
                "The URL uses a shortening service, which hides the final destination from this local inspector.",
                "medium",
                cautious_action,
            )
        )

    if "xn--" in host:
        signals.append(
            _signal(
                "punycode_host",
                host,
                "The host uses Punycode encoding. This can be legitimate, but it deserves careful review because visually similar domains are possible.",
                "medium",
                cautious_action,
            )
        )

    if not is_ip_address and len(host.split(".")) >= 4:
        signals.append(
            _signal(
                "deep_subdomain_structure",
                host,
                "The host has several subdomain labels. Long host structures can make the actual destination harder to recognize.",
                "low",
                cautious_action,
            )
        )

    if "%" in parsed.path or "%" in parsed.query:
        signals.append(
            _signal(
                "encoded_url_component",
                candidate,
                "The URL contains encoded components. Encoding is common on the web but can make a destination harder to inspect manually.",
                "low",
                cautious_action,
            )
        )

    return UrlInspection(submitted_url=submitted_url, host=host, scheme=parsed.scheme, valid=True, signals=signals)
