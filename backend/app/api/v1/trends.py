from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user
from app.models import User, Warehouse, DailyRecord, ThreeMonthAverage, WeeklyReport
from app.schemas.trend import TrendData, TrendPoint, ChartData, SummaryData, WeekInfo
from app.schemas.common import ApiResponse
from app.core.exceptions import AppException
from datetime import datetime

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])

WEEKDAY_NAMES = {
    1: "星期一", 2: "星期二", 3: "星期三",
    4: "星期四", 5: "星期五", 6: "星期六",
}


@router.get("/weeks/list")
async def list_weeks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取所有已上传的周次列表"""
    result = await db.execute(
        select(WeeklyReport.iso_week, WeeklyReport.start_date, WeeklyReport.end_date)
        .order_by(WeeklyReport.iso_week.desc())
    )
    weeks = []
    for row in result.all():
        start_str = row.start_date.strftime("%m/%d") if row.start_date else ""
        end_str = row.end_date.strftime("%m/%d") if row.end_date else ""
        weeks.append({
            "iso_week": row.iso_week,
            "label": f"{row.iso_week} ({start_str}-{end_str})",
            "start_date": row.start_date.isoformat() if row.start_date else None,
            "end_date": row.end_date.isoformat() if row.end_date else None,
        })
    return {"code": 0, "message": "success", "data": weeks}


async def _get_trend_data(warehouse_code: str, iso_week: str, db: AsyncSession) -> TrendData:
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
    avg_map = {}
    for a in avgs.scalars().all():
        if a.day_of_week not in avg_map:
            avg_map[a.day_of_week] = a

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


@router.get("/summary/{iso_week}")
async def get_summary(
    iso_week: str,
    warehouse: str = Query("", description="仓库代码，留空则汇总全部"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定周次的汇总数据（可按仓库筛选）"""
    # 获取周次的日期范围
    wr = await db.execute(
        select(WeeklyReport).where(WeeklyReport.iso_week == iso_week)
    )
    weekly_report = wr.scalar_one_or_none()

    # 如果指定了仓库，先查仓库ID
    warehouse_id = None
    if warehouse:
        wh_result = await db.execute(
            select(Warehouse).where(Warehouse.code == warehouse)
        )
        wh_obj = wh_result.scalar_one_or_none()
        if wh_obj:
            warehouse_id = wh_obj.id

    # 构建日常记录查询
    record_query = select(
        DailyRecord.day_of_week,
        DailyRecord.date,
        func.sum(DailyRecord.actual_attendance).label("attendance_sum"),
        func.sum(DailyRecord.required_headcount_so).label("required_sum"),
    ).where(DailyRecord.iso_week == iso_week)

    if warehouse_id:
        record_query = record_query.where(DailyRecord.warehouse_id == warehouse_id)

    record_query = record_query.group_by(DailyRecord.day_of_week, DailyRecord.date)
    record_query = record_query.order_by(DailyRecord.date)
    records = await db.execute(record_query)
    rec_rows = records.all()

    # 构建三月均值查询
    if warehouse_id:
        avg_query = select(
            ThreeMonthAverage.day_of_week,
            ThreeMonthAverage.average_value.label("avg_sum"),
        ).where(
            ThreeMonthAverage.warehouse_id == warehouse_id,
            ThreeMonthAverage.iso_week == iso_week,
        )
    else:
        avg_query = select(
            ThreeMonthAverage.day_of_week,
            func.sum(ThreeMonthAverage.average_value).label("avg_sum"),
        ).where(
            ThreeMonthAverage.iso_week == iso_week
        ).group_by(
            ThreeMonthAverage.day_of_week
        )

    avg_query = avg_query.order_by(ThreeMonthAverage.day_of_week)
    avgs = await db.execute(avg_query)
    avg_map = {}
    for row in avgs.all():
        if row.day_of_week not in avg_map:
            avg_map[row.day_of_week] = row.avg_sum

    days = []
    day_labels = []
    attendance_sums = []
    required_so_sums = []
    avg_sums = []

    for rec in rec_rows:
        dow = rec.day_of_week
        date_str = rec.date.strftime("%m/%d") if rec.date else ""
        weekday = WEEKDAY_NAMES.get(dow, f"Day{dow}")
        day_labels.append(f"{date_str} {weekday}")
        attendance_sums.append(round(rec.attendance_sum, 2) if rec.attendance_sum else 0)
        required_so_sums.append(round(rec.required_sum, 2) if rec.required_sum else 0)
        avg_sums.append(round(avg_map.get(dow, 0), 2))

    # 如果没有数据，返回空结构
    if not day_labels:
        day_labels = ["", "", "", "", "", ""]
        attendance_sums = [0, 0, 0, 0, 0, 0]
        required_so_sums = [0, 0, 0, 0, 0, 0]
        avg_sums = [0, 0, 0, 0, 0, 0]

    start_str = weekly_report.start_date.strftime("%m/%d") if weekly_report and weekly_report.start_date else ""
    end_str = weekly_report.end_date.strftime("%m/%d") if weekly_report and weekly_report.end_date else ""

    return {
        "code": 0,
        "message": "success",
        "data": {
            "iso_week": iso_week,
            "start_date": weekly_report.start_date.isoformat() if weekly_report and weekly_report.start_date else None,
            "end_date": weekly_report.end_date.isoformat() if weekly_report and weekly_report.end_date else None,
            "date_range": f"{start_str}-{end_str}",
            "days": day_labels,
            "attendance_sums": attendance_sums,
            "required_so_sums": required_so_sums,
            "avg_sums": avg_sums,
        }
    }


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
