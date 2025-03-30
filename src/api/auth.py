from src import config
from fastapi import Security, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader

api_key = config.get_settings().API_KEY
api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def get_api_key(request: Request, api_key_header: str = Security(api_key_header)):
    print(f"api_key_header: {api_key_header}, api_key: {api_key}")
    if api_key_header == api_key:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden"
        )
