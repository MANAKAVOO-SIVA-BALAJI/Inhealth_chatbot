# api/main.py

# api/main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router
from app.config import settings
from middleware.logging import RequestLoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.auth import verify_api_key
from app.exceptions import ChatbotException, RateLimitingError, UnexpectedError
from pydantic import ValidationError, BaseModel
import os
import time
import structlog
import uuid
from contextlib import asynccontextmanager
from logging.config import dictConfig
from custom_logging.config import configure_logging

# Logging Configuration
os.makedirs("logs", exist_ok=True)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "formatter": "json",  # or "default"
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "json",
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
        },
        "httpcore": {"level": "WARNING"},
        "httpx": {"level": "WARNING"},
        "openai": {"level": "WARNING"},
    },
}


dictConfig(logging_config)
configure_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Inhlth Chatbot API")
    yield
    logger.info("Shutting down Inhlth Chatbot API")

app = FastAPI(
    title="Inhlth Chatbot API",
    description="API to chat with live data",
    version="1.0.0",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
)

app.include_router(
    router,
    prefix="/v1",
    dependencies=[Depends(verify_api_key)] if not settings.APP_DEBUG else []
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "Development")
    }

class ErrorResponse(BaseModel):
    error: str
    detail: str

@app.exception_handler(ChatbotException)
async def chatbot_exception_handler(request: Request, exc: ChatbotException):
    logger.error(f"Chatbot exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "error_type": type(exc).__name__}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="HTTP Error", detail=exc.detail).dict()
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation error occurred: {exc.errors()}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error="Validation Error", detail=str(exc.errors())).dict()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=False)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="An unexpected error occurred",
            detail=str(exc) if settings.APP_DEBUG else "Internal server error"
        ).dict()
    )

