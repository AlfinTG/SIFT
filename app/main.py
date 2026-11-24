from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import analyze


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="SIFT",
    description="Local, explainable scam-message and suspicious-URL analysis.",
    version="0.1.0",
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sift"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_content(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze pasted content locally using the currently available engines."""

    return analyze(request)


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
