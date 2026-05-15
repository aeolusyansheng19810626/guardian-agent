"""LLM client factory with fallback chain."""
from __future__ import annotations

from typing import Any, Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from config import (
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    GEMINI_FLASH,
    GEMINI_PRO,
    GROQ_API_KEY,
    GROQ_MODEL,
)


def get_gemini_pro(temperature: float = 0.2) -> BaseChatModel:
    return ChatOpenAI(
        model=GEMINI_PRO,
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL,
        temperature=temperature,
        timeout=90,
        max_retries=1,
    )


def get_gemini_flash(temperature: float = 0.2) -> BaseChatModel:
    return ChatOpenAI(
        model=GEMINI_FLASH,
        api_key=GEMINI_API_KEY,
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
