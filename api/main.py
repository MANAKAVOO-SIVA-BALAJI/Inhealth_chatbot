# api/main.py

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router
from app.config import settings
from middleware.logging import RequestLoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.auth import verify_api_key
from app.exceptions import ChatbotException
import time
import os

# Configure logging
from logging.config import dictConfig
import logging
import structlog

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "json": {
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["json"], "level": settings.LOG_LEVEL},
    },
}


dictConfig(logging_config)
# from custom_logging.config import setup_logging
# logger = setup_logging()

from custom_logging.config import configure_logging

configure_logging()
logger = structlog.get_logger()
# logger = logging.getLogger(__name__)

app = FastAPI(
    title="Blood Bank Chatbot API",
    description="API for interacting with the Blood Bank Chatbot",
    version="1.0.0",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"] , #settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware, 
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
)

# Include routers
app.include_router(
    router,
    prefix="/api/v1",
    dependencies=[Depends(verify_api_key)] if not settings.APP_DEBUG else None
)

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

# # Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "detail": str(exc) if settings.APP_DEBUG else "An internal server error occurred."
        }
    )

# ChatbotException handler
@app.exception_handler(ChatbotException)
async def chatbot_exception_handler(request: Request, exc: ChatbotException):
    logger.error(f"Chatbot exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "error_type": type(exc).__name__}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Blood Bank Chatbot API")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Blood Bank Chatbot API")
 