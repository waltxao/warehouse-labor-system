from datetime import date, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import DailyRecord, ThreeMonthAverage, Warehouse


async def compute_averages(db: AsyncSession, iso_week: str) -> int:
    """计算指定 ISO 周次的近3月需求人力平均值。
    滚动窗口：往前推 3 个月，取同一星期几的实际工作需求人数(SO)求平均。
    """
    # 解析 iso_week (如 "2026-W24")
    year, week_num = iso_week.split("-W")
    year, week_num = int(year), int(week_num)

    # 当前周的日期范围
    jan1 = date(year, 1, 4)  # ISO 周定义：1月4日总是在第1周
    week1_monday = jan1 - timedelta(days=jan1.weekday())
    current_monday = week1_monday + timedelta(weeks=week_num - 1)

    # 3 个月前的日期
    three_months_ago = current_monday - timedelta(days=90)

    # 查询所有仓库
    wh_result = await db.execute(select(Warehouse).where(Warehouse.is_active == True))
    warehouses = wh_result.scalars().all()

    count = 0
    for wh in warehouses:
        for dow in range(1, 7):  # 周一~周六
            # 查询该仓库在过去3个月中同星期几的所有 SO 需求数据
            result = await db.execute(
                select(DailyRecord.required_headcount_so)
                .where(
                    DailyRecord.warehouse_id == wh.id,
                    DailyRecord.day_of_week == dow,
                    DailyRecord.date >= three_months_ago,
                    DailyRecord.date < current_monday,
                    DailyRecord.required_headcount_so.isnot(None),
                )
            )
            values = [v for v in result.scalars().all() if v is not None]

            if not values:
                continue

            avg = sum(values) / len(values)
            is_partial = len(values) < 12  # 约3个月每周一天 ~= 12~13 个样本
            sample_count = len(values)

            # 删除旧记录（如果存在）
            await db.execute(
                delete(ThreeMonthAverage)
                .where(
                    ThreeMonthAverage.warehouse_id == wh.id,
                    ThreeMonthAverage.iso_week == iso_week,
                    ThreeMonthAverage.day_of_week == dow,
                )
            )

            avg_record = ThreeMonthAverage(
                warehouse_id=wh.id,
                iso_week=iso_week,
                day_of_week=dow,
                average_value=round(avg, 2),
                is_partial=is_partial,
                sample_count=sample_count,
            )
            db.add(avg_record)
            count += 1

    await db.commit()
    return count
