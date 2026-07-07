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
    PushResponse,
)
from app.schemas.common import ApiResponse
from app.core.exceptions import AppException
from app.services.webhook_service import push_chart_to_wechat

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
