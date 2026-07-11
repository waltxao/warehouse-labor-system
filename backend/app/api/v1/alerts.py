from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.models import User, AlertRule, AlertLog
from app.schemas.alert import AlertRuleCreate, AlertRuleResponse, AlertRuleUpdate
from app.schemas.common import ApiResponse
from app.core.exceptions import AppException

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("/rules")
async def list_rules(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertRule))
    rules = result.scalars().all()
    return ApiResponse[list[AlertRuleResponse]](data=[
        AlertRuleResponse(
            id=r.id, name=r.name, metric=r.metric, condition_type=r.condition_type,
            operator=r.operator, threshold_value=r.threshold_value, consecutive_days=r.consecutive_days,
            scope=r.scope, warehouse_id=r.warehouse_id, is_active=r.is_active
        ) for r in rules
    ])


@router.post("/rules")
async def create_rule(
    req: AlertRuleCreate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    rule = AlertRule(**req.model_dump(), created_by=user.id)
    db.add(rule)
    await db.commit()
    return ApiResponse[dict](data={"id": rule.id})


@router.patch("/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    req: AlertRuleUpdate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise AppException(404, "Alert rule not found")

    if req.name is not None:
        rule.name = req.name
    if req.is_active is not None:
        rule.is_active = req.is_active
    if req.threshold_value is not None:
        rule.threshold_value = req.threshold_value
    if req.consecutive_days is not None:
        rule.consecutive_days = req.consecutive_days

    await db.commit()
    return ApiResponse[dict](data={"id": rule.id})


@router.get("/logs")
async def list_logs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AlertLog).order_by(AlertLog.trigger_date.desc())
    result = await db.execute(query)
    logs = result.scalars().all()
    return ApiResponse[list[dict]](data=[{
        "id": log.id,
        "rule_id": log.alert_rule_id,
        "warehouse_id": log.warehouse_id,
        "trigger_date": log.trigger_date.isoformat(),
        "trigger_value": log.trigger_value,
        "status": log.status,
    } for log in logs])
