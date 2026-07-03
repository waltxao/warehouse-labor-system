from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.models import User, Warehouse, UserWarehouseBinding
from app.schemas.warehouse import WarehouseResponse, WarehouseCreate
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/warehouses", tags=["warehouses"])


@router.get("")
async def list_warehouses(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role == "viewer":
        # 仅返回绑定的仓库
        result = await db.execute(
            select(Warehouse)
            .join(UserWarehouseBinding, UserWarehouseBinding.warehouse_id == Warehouse.id)
            .where(UserWarehouseBinding.user_id == user.id)
        )
    else:
        result = await db.execute(select(Warehouse))
    warehouses = result.scalars().all()
    return ApiResponse[list[WarehouseResponse]](
        data=[WarehouseResponse(id=w.id, code=w.code, name=w.name, is_active=w.is_active) for w in warehouses]
    )


@router.post("")
async def create_warehouse(
    req: WarehouseCreate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    wh = Warehouse(code=req.code, name=req.name or req.code)
    db.add(wh)
    await db.commit()
    return ApiResponse[WarehouseResponse](
        data=WarehouseResponse(id=wh.id, code=wh.code, name=wh.name, is_active=wh.is_active)
    )
