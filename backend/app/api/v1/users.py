from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import require_role
from app.core.security import hash_password
from app.models import User, UserWarehouseBinding
from app.schemas.user import UserCreate, UserUpdate, UserWithBindings
from app.schemas.common import ApiResponse
from app.core.exceptions import AppException

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("")
async def list_users(user: User = Depends(require_role("admin")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    data = []
    for u in users:
        bindings = await db.execute(
            select(UserWarehouseBinding).where(UserWarehouseBinding.user_id == u.id)
        )
        wh_ids = [b.warehouse_id for b in bindings.scalars().all()]
        data.append(UserWithBindings(
            id=u.id, username=u.username, role=u.role, is_active=u.is_active, warehouse_ids=wh_ids
        ))
    return ApiResponse[list[UserWithBindings]](data=data)


@router.post("")
async def create_user(
    req: UserCreate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise AppException(409, "Username already exists")
    new_user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=req.role,
    )
    db.add(new_user)
    await db.flush()
    for wh_id in req.warehouse_ids:
        db.add(UserWarehouseBinding(user_id=new_user.id, warehouse_id=wh_id))
    await db.commit()
    return ApiResponse[dict](data={"id": new_user.id})


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    req: UserUpdate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise AppException(404, "User not found")

    if req.is_active is not None:
        target.is_active = req.is_active
    if req.role is not None:
        target.role = req.role
    if req.warehouse_ids is not None:
        await db.execute(
            delete(UserWarehouseBinding).where(UserWarehouseBinding.user_id == user_id)
        )
        for wh_id in req.warehouse_ids:
            db.add(UserWarehouseBinding(user_id=user_id, warehouse_id=wh_id))

    await db.commit()
    return ApiResponse[dict](data={"id": user_id})
