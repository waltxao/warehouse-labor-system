from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.schemas.common import ApiResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AppException
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise AppException(401, "Invalid credentials")
    if not user.is_active:
        raise AppException(401, "Account disabled")
    token_data = {"sub": str(user.id)}
    return ApiResponse[TokenResponse](
        data=TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )
    )


@router.post("/refresh")
async def refresh(req: RefreshRequest):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AppException(401, "Invalid refresh token")
    token_data = {"sub": payload["sub"]}
    return ApiResponse[TokenResponse](
        data=TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )
    )


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return ApiResponse[UserResponse](
        data=UserResponse(id=user.id, username=user.username, role=user.role, is_active=user.is_active)
    )
