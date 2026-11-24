"""Orchestration and documented evidence-fusion rules for the local MVP."""

from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, Assessment, EvidenceSignal, ModelStatus
from app.services.guidance import next_steps_for
from app.services.rules import analyze_message_rules
from app.services.url_inspector import extract_urls, inspect_url


LIMITATIONS = [
    "The ML classifier is not installed in this rules-only foundation; results do not include a model prediction.",
    "SIFT has not verified the sender's identity, domain ownership, website reputation, page contents, or whether a claimed event is real.",
    "URL inspection is local structural parsing only. SIFT does not open URLs, follow redirects, perform DNS lookups, or use live reputation checks.",
    "A low-indicator result does not mean a message or website is safe or verified.",
]


def _assessment(signals: list[EvidenceSignal]) -> Assessment:
    """Fuse deterministic evidence without converting it into a fraud probability.

    The highest observed severity determines the initial label. A critical explicit
    credential/payment signal outweighs all lower findings; model output is absent
    in this foundation, so every result remains explicitly uncertain.
    """

    severities = {signal.severity for signal in signals}
    if "critical" in severities:
        return Assessment(level="critical", summary="A critical warning sign was detected. Do not act on the request until you verify it independently.", uncertain=True)
    if "high" in severities:
        return Assessment(level="high", summary="Several warning signs or a high-concern indicator were detected.", uncertain=True)
    if "medium" in severities:
        return Assessment(level="moderate", summary="Some structural or contextual indicators deserve careful review.", uncertain=True)
    return Assessment(level="low_indicators", summary="Few or no strong indicators were detected by the available local rules. This does not verify safety.", uncertain=True)


def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the available local engines without retaining the submitted content."""

    rule_signals = analyze_message_rules(request.message)
    submitted_urls: list[str] = []
    if request.include_url_inspection:
        submitted_urls.extend(extract_urls(request.message))
        if request.url and request.url.strip():
            submitted_urls.append(request.url.strip())

    # Preserve first-seen order while avoiding duplicate inspections.
    unique_urls = list(dict.fromkeys(submitted_urls))
    inspections = [inspect_url(url) for url in unique_urls]
    url_signals = [signal for inspection in inspections for signal in inspection.signals]
    signals = [*rule_signals, *url_signals]

    return AnalyzeResponse(
        assessment=_assessment(signals),
        model=ModelStatus(limitation="The local classifier artifact is not available yet; the rules-only fallback is active."),
        signals=signals,
        urls=inspections,
        limitations=LIMITATIONS,
        next_steps=next_steps_for(request.incident_status),
    )
