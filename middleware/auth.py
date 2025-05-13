# middleware/auth.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from app.config import API_KEY_NAME, API_KEY

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    # print("verify api key")
    """
    Verifies the provided API key against the expected API key.

    Args:
        api_key (str): The API key provided in the request header.

    Raises:
        HTTPException: If the API key is invalid or missing.

    Returns:
        str: The verified API key.
    """
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    return api_key 