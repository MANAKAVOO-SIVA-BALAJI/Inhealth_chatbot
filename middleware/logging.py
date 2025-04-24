# middleware/logging.py
import time
import logging
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# logger = logging.getLogger(__name__)
import structlog
logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client=request.client.host if request.client else None,
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                request_id=request_id,
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.error(
                "Request failed",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            raise