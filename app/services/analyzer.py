"""Orchestration and documented evidence-fusion rules for the local MVP."""

from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, Assessment, EvidenceSignal, ModelStatus
from app.services.classifier import MLInferenceResult, run_ml_inference
from app.services.guidance import next_steps_for
from app.services.rules import analyze_message_rules
from app.services.url_inspector import extract_urls, inspect_url


LIMITATIONS = [
    "A local ML signal is used only when its trained artifact is available. Model scores are not calibrated fraud probabilities.",
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
        return Assessment(level="critical", summary="A critical warning sign was detected. Do not act on the request until you verify it independently.", uncertain=True, contributing_sources=sorted({signal.source for signal in signals}))
    if "high" in severities:
        return Assessment(level="high", summary="Several warning signs or a high-concern indicator were detected.", uncertain=True, contributing_sources=sorted({signal.source for signal in signals}))
    if "medium" in severities:
        return Assessment(level="moderate", summary="Some structural, contextual, or model indicators deserve careful review.", uncertain=True, contributing_sources=sorted({signal.source for signal in signals}))
    return Assessment(level="low_indicators", summary="Few or no strong indicators were detected by the available local checks. This does not verify safety.", uncertain=True, contributing_sources=sorted({signal.source for signal in signals}))


def _model_status(result: MLInferenceResult) -> ModelStatus:
    return ModelStatus(
        available=result.available,
        status=result.status,  # type: ignore[arg-type]
        prediction=result.prediction,  # type: ignore[arg-type]
        score=result.score,
        score_name=result.score_name,  # type: ignore[arg-type]
        model_version=result.model_version,
        limitation=result.limitation,
        limitations=[result.limitation] if result.limitation else [],
    )


def _ml_signal(result: MLInferenceResult) -> EvidenceSignal | None:
    """Represent a SCAM prediction as supporting evidence, never as text proof."""

    if not result.available or result.prediction != "SCAM" or result.score is None:
        return None
    return EvidenceSignal(
        source="ml",
        signal_id="model_scam_signal",
        evidence="",
        reason="The local text model found a scam-like pattern. Treat this as a supporting signal alongside the evidence shown elsewhere.",
        severity="medium",
        recommended_action="Do not rely on the model score alone. Verify the claim through an independently found official channel.",
    )


def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the available local engines without retaining the submitted content."""

    rule_signals = analyze_message_rules(request.message)
    inference = run_ml_inference(request.message)
    submitted_urls: list[str] = []
    if request.include_url_inspection:
        submitted_urls.extend(extract_urls(request.message))
        if request.url and request.url.strip():
            submitted_urls.append(request.url.strip())

    # Preserve first-seen order while avoiding duplicate inspections.
    unique_urls = list(dict.fromkeys(submitted_urls))
    inspections = [inspect_url(url) for url in unique_urls]
    url_signals = [signal for inspection in inspections for signal in inspection.signals]
    model_signal = _ml_signal(inference)
    signals = [*rule_signals, *url_signals, *([model_signal] if model_signal else [])]

    return AnalyzeResponse(
        assessment=_assessment(signals),
        model=_model_status(inference),
        signals=signals,
        urls=inspections,
        limitations=LIMITATIONS,
        next_steps=next_steps_for(request.incident_status),
    )
