from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from .config import settings

# API key header definition
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(API_KEY_HEADER)):
    """
    Validate API key from request header
    
    Args:
        api_key: API key from request header
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if api_key == settings.API_TOKEN:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key"
    ) 