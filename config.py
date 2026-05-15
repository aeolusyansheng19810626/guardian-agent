"""Centralized configuration for Guardian Agent."""
from __future__ import annotations

import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: Final[str | None] = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY: Final[str | None] = os.getenv("GROQ_API_KEY")

GCP_PROJECT: Final[str] = os.getenv("GOOGLE_CLOUD_PROJECT", "yansheng-project")
GCP_REGION: Final[str] = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

GEMINI_BASE_URL: Final[str] = (
    f"https://{GCP_REGION}-aiplatform.googleapis.com/v1beta1/"
    f"projects/{GCP_PROJECT}/locations/{GCP_REGION}/endpoints/openapi/"
)

GEMINI_PRO: Final[str] = "google/gemini-2.5-pro"
GEMINI_FLASH: Final[str] = "google/gemini-2.5-flash"
GROQ_MODEL: Final[str] = "llama-3.3-70b-versatile"

PASS_THRESHOLD: Final[int] = 80
CONDITIONAL_THRESHOLD: Final[int] = 60

DIMENSION_WEIGHTS_INCIDENT: Final[dict[str, float]] = {
    "completeness": 0.25,
    "quality": 0.30,
    "compliance": 0.15,
    "logic": 0.15,
    "prevention": 0.15,
}

DIMENSION_WEIGHTS_DELIVERY: Final[dict[str, float]] = {
    "completeness": 0.30,
    "quality": 0.35,
    "compliance": 0.18,
    "logic": 0.17,
}

DIMENSION_LABELS: Final[dict[str, str]] = {
    "completeness": "完整性",
    "quality": "质量",
    "compliance": "格式合规",
    "logic": "逻辑一致性",
    "prevention": "再発防止",
}

if os.getenv("LANGCHAIN_API_KEY"):
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "guardian-agent")


def get_weights(doc_type: str) -> dict[str, float]:
    return (
        DIMENSION_WEIGHTS_INCIDENT
        if doc_type == "incident"
        else DIMENSION_WEIGHTS_DELIVERY
    )


def active_dimensions(doc_type: str) -> list[str]:
    return list(get_weights(doc_type).keys())
