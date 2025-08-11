import logging
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


logger = logging.getLogger(__name__)


class RequestTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.start_time = datetime.now(timezone.utc)
        response = await call_next(request)
        return response
