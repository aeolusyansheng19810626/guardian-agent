"""LLM client factory with fallback chain."""
from __future__ import annotations

import json
from typing import Any, Callable

import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from config import (
    GCP_SA_JSON,
    GEMINI_BASE_URL,
    GEMINI_FLASH,
    GEMINI_PRO,
    GROQ_API_KEY,
    GROQ_MODEL,
)

_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
_creds = None


def _get_creds():
    """加载 Service Account 凭据：优先 JSON secret，回落到 ADC（本地文件路径或 gcloud）。"""
    global _creds
    if _creds is None:
        if GCP_SA_JSON:
            info = json.loads(GCP_SA_JSON)
            _creds = service_account.Credentials.from_service_account_info(
                info, scopes=_SCOPES,
            )
        else:
            # google.auth.default 自动处理 GOOGLE_APPLICATION_CREDENTIALS / gcloud ADC
            _creds, _ = google.auth.default(scopes=_SCOPES)
    if not _creds.valid:
        _creds.refresh(google.auth.transport.requests.Request())
    return _creds


def _gemini_access_token() -> str:
    return _get_creds().token


def get_gemini_pro(temperature: float = 0.2) -> BaseChatModel:
    return ChatOpenAI(
        model=GEMINI_PRO,
        api_key=_gemini_access_token(),
        base_url=GEMINI_BASE_URL,
        temperature=temperature,
        timeout=90,
        max_retries=1,
    )


def get_gemini_flash(temperature: float = 0.2) -> BaseChatModel:
    return ChatOpenAI(
        model=GEMINI_FLASH,
        api_key=_gemini_access_token(),
        base_url=GEMINI_BASE_URL,
        temperature=temperature,
        timeout=60,
        max_retries=1,
    )


def get_groq(temperature: float = 0.2) -> BaseChatModel:
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        timeout=60,
        max_retries=1,
    )


def invoke_with_fallback(
    builders: list[tuple[str, Callable[[], BaseChatModel]]],
    messages: list[BaseMessage] | str,
    structured_schema: Any | None = None,
    on_fallback: Callable[[str, str, Exception], None] | None = None,
) -> Any:
    """按顺序尝试 builders，失败则回退到下一个。

    builders: [(label, factory)] 例 [("gemini-pro", get_gemini_pro), ...]
    on_fallback(failed_label, next_label, err) 用于通知 UI。
    """
    last_err: Exception | None = None
    for idx, (label, factory) in enumerate(builders):
        try:
            llm = factory()
            if structured_schema is not None:
                llm = llm.with_structured_output(structured_schema)
            return llm.invoke(messages)
        except Exception as err:  # noqa: BLE001
            last_err = err
            if on_fallback and idx + 1 < len(builders):
                next_label = builders[idx + 1][0]
                try:
                    on_fallback(label, next_label, err)
                except Exception:  # noqa: BLE001
                    pass
            continue
    raise RuntimeError(f"All LLMs failed: {last_err}")


def default_chain_pro_first() -> list[tuple[str, Callable[[], BaseChatModel]]]:
    return [
        ("gemini-pro", get_gemini_pro),
        ("gemini-flash", get_gemini_flash),
        ("groq", get_groq),
    ]


def default_chain_flash_first() -> list[tuple[str, Callable[[], BaseChatModel]]]:
    return [
        ("gemini-flash", get_gemini_flash),
        ("gemini-pro", get_gemini_pro),
        ("groq", get_groq),
    ]


def default_chain_groq_first() -> list[tuple[str, Callable[[], BaseChatModel]]]:
    return [
        ("groq", get_groq),
        ("gemini-flash", get_gemini_flash),
        ("gemini-pro", get_gemini_pro),
    ]
