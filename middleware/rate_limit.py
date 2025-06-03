# # middleware/rate_limit.py

import time
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import structlog
from app.exceptions import RateLimitingError
from starlette.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.requests import Request as StarletteRequest
from starlette.types import Message

logger = structlog.get_logger()

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute=60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)

    def cleanup_old_requests(self):
        """Clean up old timestamps to avoid memory bloat."""
        current_time = time.time()
        for user_id, timestamps in list(self.request_counts.items()):
            self.request_counts[user_id] = [
                timestamp for timestamp in timestamps if current_time - timestamp < 60
            ]

    async def dispatch(self, request: Request, call_next):
        # Clone request body so it can be read again
        body = await request.body()

        # Parse user_id from JSON body
        user_id = "anonymous"
        try:
            json_body = await request.json()
            user_id = json_body.get("user_id", "anonymous")
        except Exception:
            pass  # Body is not JSON or user_id not provided

        now = time.time()
        self.cleanup_old_requests()

        # Rate limit check
        if len(self.request_counts[user_id]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for user_id: {user_id}")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded for user"},
            )

        self.request_counts[user_id].append(now)

        # Reconstruct request with original body (so downstream handlers can still read it)
        async def receive() -> Message:
            return {"type": "http.request", "body": body}

        request = StarletteRequest(request.scope, receive=receive)

        # Call next middleware
        response = await call_next(request)

        remaining = self.requests_per_minute - len(self.request_counts[user_id])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))

        return response


# import time
# from fastapi import HTTPException, Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from collections import defaultdict
# import structlog
# from app.exceptions import RateLimitingError
# from starlette.responses import JSONResponse

# logger = structlog.get_logger()

# class RateLimitMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, requests_per_minute=60):
#         super().__init__(app)
#         self.requests_per_minute = requests_per_minute
#         self.request_counts = defaultdict(list)

#     def cleanup_old_requests(self):
#         """Clean up old timestamps to avoid memory bloat."""
#         current_time = time.time()
#         for ip, timestamps in list(self.request_counts.items()):
#             self.request_counts[ip] = [timestamp for timestamp in timestamps if current_time - timestamp < 60]

#     async def dispatch(self, request: Request, call_next):
#         client_ip = request.client.host if request.client else "unknown"
#         now = time.time()
        
#         # Clean old requests before each check
#         self.cleanup_old_requests()

#         # Check rate limit
#         if len(self.request_counts[client_ip]) >= self.requests_per_minute:
#             logger.warning(f"Rate limit exceeded for IP: {client_ip}. Current count: {len(self.request_counts[client_ip])}")
#             return JSONResponse(
#             status_code=429,
#             content={"error": "Rate limit exceeded"}
#             )
#             # raise RateLimitingError(f"Rate limit exceeded for IP: {client_ip}")
#         # Record the current request
#         self.request_counts[client_ip].append(now)
        
#         # Process request
#         response = await call_next(request)
        
#         # Add rate limit headers
#         remaining = self.requests_per_minute - len(self.request_counts[client_ip])
#         response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
#         response.headers["X-RateLimit-Remaining"] = str(remaining)
#         response.headers["X-RateLimit-Reset"] = str(int(now + 60))
        
#         return response
