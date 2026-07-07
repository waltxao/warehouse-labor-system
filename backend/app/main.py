import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select, text

from app.core.exceptions import AppException, app_exception_handler
from app.database import engine, Base, async_session
import app.models  # noqa: F401  确保所有模型被导入以注册到 Base.metadata
from app.models import WebhookConfig, Warehouse
from app.api.v1 import api_router
from app.services.webhook_service import push_all_to_wechat

logger = logging.getLogger(__name__)

# 模块级调度器，便于 lifespan 管理
scheduler = None


async def _ensure_webhook_schedule_columns():
    """SQLite: 确保 webhook_configs 表包含新增的定时推送相关列。

    create_all 不会修改已存在的表结构，因此对已存在的历史数据库
    需要用 ALTER TABLE 补齐 message_template / schedule_* 字段。
    """
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(webhook_configs)"))
        existing_cols = {row[1] for row in result.fetchall()}
        new_cols = {
            "message_template": "TEXT",
            "schedule_enabled": "BOOLEAN DEFAULT 0",
            "schedule_day": "INTEGER",
            "schedule_time": "VARCHAR(5)",
        }
        for col, coltype in new_cols.items():
            if col not in existing_cols:
                await conn.execute(
                    text(f"ALTER TABLE webhook_configs ADD COLUMN {col} {coltype}")
                )
                logger.info(f"已为 webhook_configs 补齐列: {col}")


async def check_scheduled_pushes():
    """每分钟检查是否有需要执行的定时推送"""
    now = datetime.now()
    current_day = now.weekday()  # 0=Monday
    current_time = now.strftime('%H:%M')

    try:
        async with async_session() as session:
            result = await session.execute(
                select(WebhookConfig, Warehouse)
                .join(Warehouse, WebhookConfig.warehouse_id == Warehouse.id)
                .where(
                    WebhookConfig.schedule_enabled == True,
                    WebhookConfig.schedule_day == current_day,
                    WebhookConfig.schedule_time == current_time,
                    WebhookConfig.is_active == True,
                )
            )
            rows = result.all()
            if rows:
                # 使用 isocalendar 生成 ISO 周次，与 excel_parser 保持一致（跨平台可靠）
                iso_year, iso_week_num, _ = now.isocalendar()
                iso_week = f"{iso_year}-W{iso_week_num:02d}"
                codes = [wh.code for _, wh in rows]
                logger.info(f"定时推送触发: iso_week={iso_week}, codes={codes}")
                await push_all_to_wechat(session, iso_week, codes)
    except Exception as e:
        logger.error(f"定时推送执行失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动创建缺失的表（SQLite，create_all 是幂等的）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 补齐历史数据库中 webhook_configs 的新增列
    await _ensure_webhook_schedule_columns()

    # 启动定时调度器（每分钟检查一次是否有需要执行的定时推送）
    global scheduler
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_scheduled_pushes,
        CronTrigger(minute="*"),
        id="check_scheduled_pushes",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("定时推送调度器已启动")

    yield

    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("定时推送调度器已关闭")


app = FastAPI(title="仓库人力数据分析系统", version="1.0.0", lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/api/v1/health")
async def health():
    return {"code": 0, "message": "success", "data": {"status": "ok"}}


app.include_router(api_router)

# 静态资源目录
static_dir = os.path.join(os.path.dirname(__file__), "static")

# SPA 回退：非 API 路径一律返回 index.html，由前端路由处理
if os.path.isdir(static_dir):
    # 先挂载静态资源（JS/CSS/图片等）
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(request: Request, full_path: str):
        """所有非 API 路径回退到 index.html，支持前端 SPA 路由"""
        # API 路径直接 404
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # 尝试匹配静态文件
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # 其他路径返回 index.html（SPA 路由）
        index_path = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)

        return JSONResponse({"detail": "Not Found"}, status_code=404)
