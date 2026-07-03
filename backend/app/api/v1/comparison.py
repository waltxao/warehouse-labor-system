from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import require_role
from app.models import User, Warehouse, DailyRecord
from app.schemas.comparison import ComparisonRequest, ComparisonData
from app.schemas.common import ApiResponse
from app.core.exceptions import AppException

router = APIRouter(prefix="/api/v1/comparison", tags=["comparison"])

METRIC_MAP = {
    "attendance": "actual_attendance",
    "required_so": "required_headcount_so",
    "savings": "labor_savings",
    "fulfillment_rate": "work_fulfillment_rate",
}


@router.post("")
async def compare(
    req: ComparisonRequest,
    user: User = Depends(require_role("global_viewer", "admin")),
    db: AsyncSession = Depends(get_db),
):
    if len(req.warehouse_codes) > 6:
        raise AppException(400, "最多对比 6 个仓库")
    metric_field = METRIC_MAP.get(req.metric, "actual_attendance")

    warehouses_data = []
    for code in req.warehouse_codes:
        wh = await db.execute(select(Warehouse).where(Warehouse.code == code))
        warehouse = wh.scalar_one_or_none()
        if not warehouse:
            raise AppException(404, f"Warehouse {code} not found")

        records = await db.execute(
            select(DailyRecord)
            .where(DailyRecord.warehouse_id == warehouse.id, DailyRecord.iso_week == req.iso_week)
            .order_by(DailyRecord.date)
        )
        values = [{"date": r.date.isoformat(), "value": getattr(r, metric_field)} for r in records.scalars().all()]
        warehouses_data.append({"code": code, "values": values})

    return ApiResponse[ComparisonData](data=ComparisonData(
        iso_week=req.iso_week, metric=req.metric, warehouses=warehouses_data
    ))
