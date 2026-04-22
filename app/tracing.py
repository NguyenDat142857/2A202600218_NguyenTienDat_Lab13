from __future__ import annotations

import os
from typing import Any, Callable, Optional

# ==============================
# SAFE IMPORT (fallback nếu chưa cài langfuse)
# ==============================

try:
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except Exception:  # pragma: no cover
    LANGFUSE_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()


# ==============================
# CONFIG CHECK
# ==============================

def tracing_enabled() -> bool:
    """
    Check if Langfuse is properly configured
    """
    return bool(
        LANGFUSE_AVAILABLE and
        os.getenv("LANGFUSE_PUBLIC_KEY") and
        os.getenv("LANGFUSE_SECRET_KEY")
    )


# ==============================
# TRACE METADATA HELPERS
# ==============================

def set_trace_metadata(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> None:
    """
    Attach metadata to current trace
    """
    if not tracing_enabled():
        return

    langfuse_context.update_current_trace(
        user_id=user_id,
        session_id=session_id,
        tags=tags or [],
        metadata={
            "request_id": request_id
        }
    )


def set_observation_metadata(
    *,
    input_data: Any = None,
    output_data: Any = None,
    model: Optional[str] = None,
) -> None:
    """
    Attach metadata to current span/observation
    """
    if not tracing_enabled():
        return

    langfuse_context.update_current_observation(
        input=input_data,
        output=output_data,
        metadata={
            "model": model
        }
    )


# ==============================
# DECORATORS (CLEAN WRAPPER)
# ==============================

def trace_agent(name: str = "agent") -> Callable:
    """
    Decorator for main agent pipeline
    """

    def decorator(func: Callable):
        if not tracing_enabled():
            return func

        return observe(name=name)(func)

    return decorator


def trace_step(name: str) -> Callable:
    """
    Decorator for sub-steps (LLM, RAG, etc.)
    """

    def decorator(func: Callable):
        if not tracing_enabled():
            return func

        return observe(name=name)(func)

    return decorator