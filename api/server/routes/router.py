from core.config import BEARER_TOKEN
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from server.routes import chat, health, ids


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials


router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(
    chat.router, tags=["chat"], dependencies=[Depends(validate_token)]
)
router.include_router(ids.router, tags=["ids"], dependencies=[Depends(validate_token)])
