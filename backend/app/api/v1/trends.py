from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user
from app.models import User, Warehouse, DailyRecord, ThreeMonthAverage
from app.schemas.trend import TrendData, TrendPoint, ChartData
from app.schemas.common import ApiResponse
from app.core.exceptions import AppException

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])


async def _get_trend_data(warehouse_code: str, iso_week: str, db: AsyncSession) -> TrendData:
    """Internal helper: fetch trend data for a warehouse in a given ISO week."""
    wh = await db.execute(select(Warehouse).where(Warehouse.code == warehouse_code))
    warehouse = wh.scalar_one_or_none()
    if not warehouse:
        raise AppException(404, "Warehouse not found")

    records = await db.execute(
        select(DailyRecord)
        .where(DailyRecord.warehouse_id == warehouse.id, DailyRecord.iso_week == iso_week)
        .order_by(DailyRecord.date)
    )
    records_list = records.scalars().all()

    avgs = await db.execute(
        select(ThreeMonthAverage)
        .where(ThreeMonthAverage.warehouse_id == warehouse.id, ThreeMonthAverage.iso_week == iso_week)
    )
    avg_map = {a.day_of_week: a for a in avgs.scalars().all()}

    points = []
    for rec in records_list:
        avg = avg_map.get(rec.day_of_week)
        points.append(TrendPoint(
            date=rec.date,
            day_of_week=rec.day_of_week,
            actual_attendance=rec.actual_attendance,
            required_headcount_so=rec.required_headcount_so,
            three_month_average=avg.average_value if avg else None,
            is_partial=avg.is_partial if avg else True,
        ))

    return TrendData(
        warehouse_code=warehouse_code, iso_week=iso_week, points=points
    )


@router.get("/{warehouse_code}")
async def get_trend(
    warehouse_code: str,
    iso_week: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trend = await _get_trend_data(warehouse_code, iso_week, db)
    return ApiResponse[TrendData](data=trend)


@router.get("/{warehouse_code}/chart")
async def get_chart(
    warehouse_code: str,
    iso_week: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trend = await _get_trend_data(warehouse_code, iso_week, db)
    return ApiResponse[ChartData](data=ChartData(
        warehouse_code=warehouse_code,
        iso_week=iso_week,
        dates=[p.date.isoformat() for p in trend.points],
        attendance=[p.actual_attendance for p in trend.points],
        required_so=[p.required_headcount_so for p in trend.points],
        three_month_avg=[p.three_month_average for p in trend.points],
        is_partial=[p.is_partial for p in trend.points],
    ))
