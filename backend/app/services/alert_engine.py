from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AlertRule, AlertLog, DailyRecord, Warehouse

OPERATORS = {
    "gt": lambda a, b: a > b,
    "lt": lambda a, b: a < b,
    "gte": lambda a, b: a >= b,
    "lte": lambda a, b: a <= b,
    "eq": lambda a, b: a == b,
}

METRIC_FIELDS = {
    "attendance": "actual_attendance",
    "savings": "labor_savings",
    "fulfillment_rate": "work_fulfillment_rate",
    "required_so": "required_headcount_so",
    "system_headcount": "system_headcount",
}


async def run_alert_checks(db: AsyncSession, iso_week: str) -> int:
    """对指定周次的数据运行所有 active 告警规则。"""
    rules_result = await db.execute(select(AlertRule).where(AlertRule.is_active == True))
    rules = rules_result.scalars().all()

    count = 0
    for rule in rules:
        metric_field = METRIC_FIELDS.get(rule.metric)
        if not metric_field:
            continue

        # 确定检查范围
        if rule.scope == "all":
            wh_result = await db.execute(select(Warehouse).where(Warehouse.is_active == True))
            warehouse_ids = [w.id for w in wh_result.scalars().all()]
        else:
            warehouse_ids = [rule.warehouse_id] if rule.warehouse_id else []

        for wh_id in warehouse_ids:
            records_result = await db.execute(
                select(DailyRecord)
                .where(DailyRecord.warehouse_id == wh_id, DailyRecord.iso_week == iso_week)
                .order_by(DailyRecord.date)
            )
            records = records_result.scalars().all()

            if rule.condition_type == "threshold":
                for rec in records:
                    val = getattr(rec, metric_field, None)
                    if val is None:
                        continue
                    if OPERATORS[rule.operator](val, rule.threshold_value):
                        log = AlertLog(
                            alert_rule_id=rule.id,
                            warehouse_id=wh_id,
                            trigger_date=rec.date,
                            trigger_value=val,
                            status="active",
                        )
                        db.add(log)
                        count += 1

            elif rule.condition_type == "consecutive_days":
                consecutive = 0
                for rec in records:
                    val = getattr(rec, metric_field, None)
                    if val is None:
                        consecutive = 0
                        continue
                    if OPERATORS[rule.operator](val, rule.threshold_value):
                        consecutive += 1
                        if consecutive >= rule.consecutive_days:
                            log = AlertLog(
                                alert_rule_id=rule.id,
                                warehouse_id=wh_id,
                                trigger_date=rec.date,
                                trigger_value=val,
                                status="active",
                            )
                            db.add(log)
                            count += 1
                    else:
                        consecutive = 0

    await db.commit()
    return count
