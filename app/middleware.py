from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Clear contextvars (tránh leak giữa các request)
        clear_contextvars()

        # 2. Lấy x-request-id từ header hoặc tạo mới
        request_id = request.headers.get("x-request-id")
        if not request_id:
            request_id = f"req-{uuid.uuid4().hex[:8]}"

        # 3. Bind vào structlog context
        bind_contextvars(correlation_id=request_id)

        # 4. Gắn vào request.state để dùng ở nơi khác
        request.state.correlation_id = request_id

        # 5. Đo thời gian xử lý
        start_time = time.perf_counter()

        # 6. Gọi request tiếp theo
        response = await call_next(request)

        # 7. Tính latency (ms)
        process_time_ms = (time.perf_counter() - start_time) * 1000

        # 8. Add headers vào response
        response.headers["x-request-id"] = request_id
        response.headers["x-response-time-ms"] = f"{process_time_ms:.2f}"

        return response