from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from .config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate the API key in request header"""
    if api_key_header == settings.API_TOKEN:
        return api_key_header
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "APIKey"},
    ) 