# app/config.py
import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
import logging

# logger = logging.getLogger(__name__)
import structlog
logger = structlog.get_logger()

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_KEY: str = Field(..., env="API_KEY")
    API_KEY_NAME: str = Field("X-API-Key", env="API_KEY_NAME")
    
    # OpenAI settings
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    
    # Hasura settings
    HASURA_ADMIN_SECRET: str = Field(..., env="HASURA_ADMIN_SECRET")
    HASURA_GRAPHQL_URL: str = Field(..., env="HASURA_GRAPHQL_URL")
    HASURA_ROLE: str = Field("admin", env="HASURA_ROLE")
    
    # App settings
    # APP_DEBUG: bool = Field("False", env="APP_DEBUG")
    APP_DEBUG: bool = Field(False, env="APP_DEBUG")
    LOG_LEVEL: str = Field("DEBUG", env="LOG_LEVEL")

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    ALLOWED_ORIGINS: str

    @property
    def allowed_origins(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(',')
    
    class Config:
        env_file = "dev.env"
        case_sensitive = True
        extra = "allow" 

# Create settings instance
settings = Settings()
print("Allowed Origins:", settings.model_dump())
print("APP_Debug:", settings.APP_DEBUG)
print("Log Level:", settings.LOG_LEVEL)

OPENAI_API_KEY = settings.OPENAI_API_KEY
HASURA_ADMIN_SECRET = settings.HASURA_ADMIN_SECRET
HASURA_GRAPHQL_URL = settings.HASURA_GRAPHQL_URL
HASURA_ROLE = settings.HASURA_ROLE
API_KEY = settings.API_KEY
API_KEY_NAME = settings.API_KEY_NAME
APP_DEBUG = settings.APP_DEBUG
LOG_LEVEL = settings.LOG_LEVEL
RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
OPENAI_MODEL = settings.OPENAI_MODEL

