import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from structlog import get_logger, threadlocal

logger = get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Bind base fields for every request
        threadlocal.clear_threadlocal()
        threadlocal.bind_threadlocal(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            client_ip=request.client.host if request.client else "unknown"
        )

        # Try to parse body for optional context
        try:
            if request.method == "POST":
                body = await request.json()
                logger.debug("Parsed request body keys", keys=list(body.keys()))

                # Bind only if present
                threadlocal.bind_threadlocal(
                    user_id=body.get("user_id"),
                    role=body.get("role"),
                    company_id=body.get("company_id"),
                    session_id=body.get("session_id")
                )
        except Exception:
            logger.warning("Failed to parse request body for additional context")

        # Log request started
        logger.info("Request started")

        start_time = time.time()

        try:
            response = await call_next(request)
            duration = round((time.time() - start_time) * 1000, 2)

            logger.info(
                "Request completed",
                status_code=response.status_code,
                process_time_ms=duration,
            )
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            logger.error(
                "Request failed",
                error=str(e),
                exc_info=True
            )
            raise

# import time
# import logging
# import uuid
# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware

# # logger = logging.getLogger(__name__)
# import structlog
# logger = structlog.get_logger()

# class RequestLoggingMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware for logging requests and responses with unique request IDs.
#     """

#     async def dispatch(self, request: Request, call_next):
#         """
#         Processes incoming requests, logs details, and adds a unique request ID.

#         Args:
#             request (Request): The incoming request object.
#             call_next: The next middleware or route handler.

#         Returns:
#             Response: The response object after processing the request.

#         Raises:
#             Exception: If an error occurs during request processing.
#         """
#         request_id = str(uuid.uuid4())
#         request.state.request_id = request_id
#         user_id = getattr(request.state, "user_id", "anonymous")

#         # Bind context to structlog's threadlocal storage
#         structlog.threadlocal.clear_threadlocal()
#         structlog.threadlocal.bind_threadlocal(
#             request_id=request_id,
#             user_id=user_id,
#             path=str(request.url.path),
#             method=request.method,
#         )
        
#         # Start timer
#         start_time = time.time()
        
#         # Log request
#         logger.info(
#             "Request started",
#             request_id=request_id,
#             method=request.method,
#             url=str(request.url),
#             client=request.client.host if request.client else None,
#         )
        
#         # Process request
#         try:
#             response = await call_next(request)
            
#             # Log response
#             process_time = time.time() - start_time
#             logger.info(
#                 "Request completed",
#                 request_id=request_id,
#                 status_code=response.status_code,
#                 process_time_ms=round(process_time * 1000, 2),
#             )
            
#             # Add request ID to response headers
#             response.headers["X-Request-ID"] = request_id
#             return response
#         except Exception as e:
#             logger.error(
#                 "Request failed",
#                 request_id=request_id,
#                 error=str(e),
#                 exc_info=False
#             )
#             raise