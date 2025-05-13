# # middleware/rate_limit.py

import time
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import structlog
from app.exceptions import RateLimitingError

logger = structlog.get_logger()

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute=60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)

    def cleanup_old_requests(self):
        """Clean up old timestamps to avoid memory bloat."""
        current_time = time.time()
        for ip, timestamps in list(self.request_counts.items()):
            self.request_counts[ip] = [timestamp for timestamp in timestamps if current_time - timestamp < 60]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean old requests before each check
        self.cleanup_old_requests()

        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}. Current count: {len(self.request_counts[client_ip])}")
            raise RateLimitingError(f"Rate limit exceeded for IP: {client_ip}")

            # raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Record the current request
        self.request_counts[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.request_counts[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))
        
        return response


# import time
# from fastapi import Request, HTTPException
# from starlette.middleware.base import BaseHTTPMiddleware
# from collections import defaultdict
# import logging
# from app.exceptions import *


# # logger = logging.getLogger(__name__)
# import structlog
# logger = structlog.get_logger()
# class RateLimitMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware for rate limiting requests based on client IP.

#     Attributes:
#         requests_per_minute (int): The maximum number of requests allowed per minute.
#         request_counts (defaultdict): A dictionary to track request timestamps for each client IP.
#     """

#     def __init__(self, app, requests_per_minute=60):
#         """
#         Initializes the RateLimitMiddleware with the given app and rate limit.

#         Args:
#             app: The FastAPI application instance.
#             requests_per_minute (int): The maximum number of requests allowed per minute.
#         """
#         super().__init__(app)
#         self.requests_per_minute = requests_per_minute
#         self.request_counts = defaultdict(list)
        
#     async def dispatch(self, request: Request, call_next):
#         """
#         Processes incoming requests and applies rate limiting.

#         Args:
#             request (Request): The incoming request object.
#             call_next: The next middleware or route handler.

#         Returns:
#             Response: The response object after processing the request.

#         Raises:
#             HTTPException: If the rate limit is exceeded.
#         """
#         client_ip = request.client.host if request.client else "unknown"
#         now = time.time()
        
#         # Clean old requests
#         self.request_counts[client_ip] = [
#             req_time for req_time in self.request_counts[client_ip] 
#             if now - req_time < 60
#         ]
        
#         # Check rate limit
#         if len(self.request_counts[client_ip]) >= self.requests_per_minute:
#             logger.warning(f"Rate limit exceeded for IP: {client_ip}")
#             raise RateLimitingError(f"Rate limit exceeded for IP: {client_ip}")
        
#             # raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
#         # Add current request
#         self.request_counts[client_ip].append(now)
        
#         # Process request
#         response = await call_next(request)
        
#         # Add rate limit headers
#         remaining = self.requests_per_minute - len(self.request_counts[client_ip])
#         response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
#         response.headers["X-RateLimit-Remaining"] = str(remaining)
#         response.headers["X-RateLimit-Reset"] = str(int(now + 60))
        
#         return response