from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import require_role
from app.models import User, Warehouse, WebhookConfig
from app.schemas.webhook import (
    WebhookConfigCreate,
    WebhookConfigUpdate,
    WebhookConfigResponse,
    PushRequest,
    PushAllRequest,
    PushResponse,
)
from app.schemas.common import ApiResponse
from app.core.exceptions import AppException
from app.services.webhook_service import push_chart_to_wechat, push_all_to_wechat

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.get("")
async def list_webhooks(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WebhookConfig, Warehouse)
        .join(Warehouse, WebhookConfig.warehouse_id == Warehouse.id)
    )
    rows = result.all()
    data = [
        WebhookConfigResponse(
            id=cfg.id,
            warehouse_id=cfg.warehouse_id,
            webhook_url=cfg.webhook_url,
            notify_users=cfg.notify_users,
            is_active=cfg.is_active,
            message_template=cfg.message_template,
            schedule_enabled=cfg.schedule_enabled,
            schedule_day=cfg.schedule_day,
            schedule_time=cfg.schedule_time,
            warehouse_code=wh.code,
            warehouse_name=wh.name,
            created_at=cfg.created_at,
            updated_at=cfg.updated_at,
        )
        for cfg, wh in rows
    ]
    return ApiResponse[list[WebhookConfigResponse]](data=data)


@router.post("")
async def create_webhook(
    req: WebhookConfigCreate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    # 校验仓库存在
    wh_result = await db.execute(select(Warehouse).where(Warehouse.id == req.warehouse_id))
    warehouse = wh_result.scalar_one_or_none()
    if not warehouse:
        raise AppException(404, "仓库不存在")

    # 如果 warehouse_id 已存在配置则更新
    existing = await db.execute(
        select(WebhookConfig).where(WebhookConfig.warehouse_id == req.warehouse_id)
    )
    config = existing.scalar_one_or_none()
    if config:
        config.webhook_url = req.webhook_url
        config.notify_users = req.notify_users
        config.is_active = req.is_active
        config.message_template = req.message_template
        config.schedule_enabled = req.schedule_enabled
        config.schedule_day = req.schedule_day
        config.schedule_time = req.schedule_time
    else:
        config = WebhookConfig(**req.model_dump())
        db.add(config)
    await db.commit()
    await db.refresh(config)
    return ApiResponse[dict](data={"id": config.id})


@router.put("/{webhook_id}")
async def update_webhook(
    webhook_id: int,
    req: WebhookConfigUpdate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(WebhookConfig).where(WebhookConfig.id == webhook_id))
    config = result.scalar_one_or_none()
    if not config:
        raise AppException(404, "Webhook 配置不存在")
    if req.webhook_url is not None:
        config.webhook_url = req.webhook_url
    if req.notify_users is not None:
        config.notify_users = req.notify_users
    if req.is_active is not None:
        config.is_active = req.is_active
    if req.message_template is not None:
        config.message_template = req.message_template
    if req.schedule_enabled is not None:
        config.schedule_enabled = req.schedule_enabled
    if req.schedule_day is not None:
        config.schedule_day = req.schedule_day
    if req.schedule_time is not None:
        config.schedule_time = req.schedule_time
    await db.commit()
    return ApiResponse[dict](data={"id": config.id})


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(WebhookConfig).where(WebhookConfig.id == webhook_id))
    config = result.scalar_one_or_none()
    if not config:
        raise AppException(404, "Webhook 配置不存在")
    await db.delete(config)
    await db.commit()
    return ApiResponse[dict](data={"id": webhook_id})


@router.post("/push")
async def push_chart(
    req: PushRequest,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await push_chart_to_wechat(
        db=db,
        warehouse_code=req.warehouse_code,
        iso_week=req.iso_week,
        chart_base64=req.chart_base64,
    )
    return ApiResponse[PushResponse](
        data=PushResponse(success=result["success"], message=result["message"])
    )


@router.post("/push-all")
async def push_all(
    req: PushAllRequest,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    if not req.iso_week:
        raise AppException(400, "请提供周次")
    result = await push_all_to_wechat(db=db, iso_week=req.iso_week, warehouse_codes=req.warehouse_codes)
    return ApiResponse[dict](data=result)
