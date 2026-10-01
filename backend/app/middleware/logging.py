import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = request.url.path

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000.0
            logger.info(
                f"{client_ip} - \"{method} {url}\" {response.status_code} in {process_time:.2f}ms"
            )
            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000.0
            logger.error(
                f"{client_ip} - \"{method} {url}\" ERROR in {process_time:.2f}ms: {exc}",
                exc_info=True
            )
            raise exc
