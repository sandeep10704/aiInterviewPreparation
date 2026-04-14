# app/core/security.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.firebase import verify_token

security = HTTPBearer()


# For HTTP routes (already correct)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    decoded = verify_token(token)

    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return decoded["uid"]


# 🔥 For WebSocket (NEW)
async def get_current_user_ws(token: str):
    decoded = verify_token(token)

    if not decoded:
        raise Exception("Invalid or expired token")

    return decoded["uid"]