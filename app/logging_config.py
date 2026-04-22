from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars

from .pii import scrub_text

# Đường dẫn log file
LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))


class JsonlFileProcessor:
    """
    Ghi log ra file dạng JSONL (mỗi dòng 1 JSON)
    """
    def __call__(self, logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        rendered = structlog.processors.JSONRenderer()(logger, method_name, event_dict)

        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(rendered + "\n")

        return event_dict


def scrub_event(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Scrub PII trong payload và message
    """
    payload = event_dict.get("payload")

    if isinstance(payload, dict):
        event_dict["payload"] = {
            k: scrub_text(v) if isinstance(v, str) else v
            for k, v in payload.items()
        }

    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_dict["event"] = scrub_text(event_dict["event"])

    return event_dict


def configure_logging() -> None:
    """
    Setup structlog với:
    - JSON logging
    - Correlation ID (contextvars)
    - PII scrubbing
    - File output (JSONL)
    """

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
    )

    structlog.configure(
        processors=[
            # 1. Merge contextvars (lấy correlation_id từ middleware)
            merge_contextvars,

            # 2. Add level (info, error...)
            structlog.processors.add_log_level,

            # 3. Timestamp
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),

            # 4. 🔥 PII scrubbing (QUAN TRỌNG)
            scrub_event,

            # 5. Debug info
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,

            # 6. Ghi file
            JsonlFileProcessor(),

            # 7. Render JSON cuối cùng
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
        ),
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.typing.FilteringBoundLogger:
    """
    Lấy logger dùng trong toàn app
    """
    return structlog.get_logger()