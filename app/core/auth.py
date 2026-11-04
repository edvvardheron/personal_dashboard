import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.config import settings

bearer = HTTPBearer(auto_error=False)

def require_api_key(creds=Depends(bearer)):
    if creds is None or not secrets.compare_digest(creds.credentials, settings.api_key):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")