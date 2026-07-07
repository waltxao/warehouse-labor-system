import base64
import hashlib
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WebhookConfig, Warehouse, DailyRecord
from app.core.exceptions import AppException


async def push_chart_to_wechat(
    db: AsyncSession,
    warehouse_code: str,
    iso_week: str,
    chart_base64: str,
) -> dict:
    # 1. 查仓库
    wh_result = await db.execute(select(Warehouse).where(Warehouse.code == warehouse_code))
    warehouse = wh_result.scalar_one_or_none()
    if not warehouse:
        raise AppException(404, f"仓库 {warehouse_code} 不存在")

    # 2. 查 webhook 配置
    cfg_result = await db.execute(
        select(WebhookConfig).where(WebhookConfig.warehouse_id == warehouse.id)
    )
    config = cfg_result.scalar_one_or_none()
    if not config:
        raise AppException(404, f"仓库 {warehouse_code} 未配置企业微信 Webhook")
    if not config.is_active:
        raise AppException(400, f"仓库 {warehouse_code} 的 Webhook 配置已禁用")

    # 3. 查询该周数据用于摘要
    records_result = await db.execute(
        select(DailyRecord)
        .where(DailyRecord.warehouse_id == warehouse.id, DailyRecord.iso_week == iso_week)
        .order_by(DailyRecord.date)
    )
    records = records_result.scalars().all()

    # 4. 构建数据摘要
    total_attendance = sum(r.actual_attendance or 0 for r in records)
    total_required = sum(r.required_headcount_so or 0 for r in records)
    if records:
        start_date = str(records[0].date)
        end_date = str(records[-1].date)
    else:
        start_date = end_date = iso_week

    summary = f"以上{start_date}-{end_date} {warehouse_code}倉實際出勤人數與實際需求人力情況"
    summary += f"\n出勤人次：{total_attendance}"
    summary += f"\n需求人力：{total_required}"
    summary += f"\n請留意"

    # 5. 通知人员手机号列表
    mentioned_mobiles = []
    if config.notify_users:
        mentioned_mobiles = [p.strip() for p in config.notify_users.split(",") if p.strip()]

    # 6. 发送图片消息（企业微信群机器人支持 base64 图片）
    # 确保 base64 不含前缀
    if "base64," in chart_base64:
        chart_base64 = chart_base64.split("base64,")[1]

    md5_hash = hashlib.md5(base64.b64decode(chart_base64)).hexdigest()

    image_payload = {
        "msgtype": "image",
        "image": {
            "base64": chart_base64,
            "md5": md5_hash
        }
    }

    # 7. 发送文字消息（含 @mention）
    text_payload = {
        "msgtype": "text",
        "text": {
            "content": summary,
            "mentioned_mobile_list": mentioned_mobiles
        }
    }

    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        # 发送图片
        img_resp = await client.post(config.webhook_url, json=image_payload)
        img_data = img_resp.json()
        results.append({"type": "image", "status": img_resp.status_code, "data": img_data})
        if img_resp.status_code != 200 or img_data.get("errcode") != 0:
            raise AppException(500, f"图片消息发送失败: {img_data}")

        # 发送文字
        text_resp = await client.post(config.webhook_url, json=text_payload)
        text_data = text_resp.json()
        results.append({"type": "text", "status": text_resp.status_code, "data": text_data})
        if text_resp.status_code != 200 or text_data.get("errcode") != 0:
            raise AppException(500, f"文字消息发送失败: {text_data}")

    return {"success": True, "message": "推送成功", "details": results}
