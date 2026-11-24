"""Typed API contracts for the first, rules-only SIFT analysis slice."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


MAX_MESSAGE_LENGTH = 10_000
MAX_URL_LENGTH = 2_048

IncidentStatus = Literal[
    "received_only",
    "clicked_link",
    "shared_personal_data",
    "shared_credentials",
    "made_payment",
]
Severity = Literal["informational", "low", "medium", "high", "critical"]
SignalSource = Literal["ml", "rule", "url"]


class AnalyzeRequest(BaseModel):
    """User-provided content for local analysis.

    The message limit accommodates long pasted conversations while preventing an
    unbounded request from consuming the local service. A request must contain a
    message, a directly entered URL, or both.
    """

    message: str = Field(default="", max_length=MAX_MESSAGE_LENGTH)
    url: str | None = Field(default=None, max_length=MAX_URL_LENGTH)
    include_url_inspection: bool = True
    incident_status: IncidentStatus = "received_only"

    @model_validator(mode="after")
    def has_analyzable_content(self) -> "AnalyzeRequest":
        if not self.message.strip() and not (self.url and self.url.strip()):
            raise ValueError("Provide a message or URL to analyze.")
        return self


class EvidenceSignal(BaseModel):
    source: SignalSource
    signal_id: str
    evidence: str
    reason: str
    severity: Severity
    recommended_action: str


class UrlInspection(BaseModel):
    submitted_url: str
    host: str | None = None
    scheme: str | None = None
    valid: bool
    signals: list[EvidenceSignal] = Field(default_factory=list)
    error: str | None = None


class Assessment(BaseModel):
    level: Literal["low_indicators", "moderate", "high", "critical"]
    summary: str
    uncertain: bool


class ModelStatus(BaseModel):
    status: Literal["unavailable"] = "unavailable"
    label: None = None
    score: None = None
    score_name: None = None
    limitation: str


class AnalyzeResponse(BaseModel):
    assessment: Assessment
    model: ModelStatus
    signals: list[EvidenceSignal]
    urls: list[UrlInspection]
    limitations: list[str]
    next_steps: list[str]
