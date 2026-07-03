import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, async_session
from app.core.deps import require_role
from app.models import User, UploadLog
from app.services.excel_parser import parse_excel
from app.services.average_calculator import compute_averages
from app.services.alert_engine import run_alert_checks
from app.schemas.upload import ParseReportResponse
from app.schemas.common import ApiResponse
from app.config import settings
from app.core.exceptions import AppException

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


async def _bg_compute_averages(iso_week: str):
    """后台任务：创建独立 session 计算近3月均值。"""
    async with async_session() as session:
        await compute_averages(session, iso_week)


async def _bg_run_alert_checks(iso_week: str):
    """后台任务：创建独立 session 运行告警检查。"""
    async with async_session() as session:
        await run_alert_checks(session, iso_week)


@router.post("")
async def upload_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(None),
    force_overwrite: bool = Query(False),
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    if not file or not file.filename:
        raise AppException(400, "No file provided")

    # 安全处理文件名
    filename = os.path.basename(file.filename)
    if not filename:
        raise AppException(400, "Invalid filename")

    # 保存文件
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 解析 Excel
    report = await parse_excel(file_path, db, user.id, force_overwrite)

    # 后台任务：计算3月均值 + 运行告警检查（使用独立 session）
    background_tasks.add_task(_bg_compute_averages, report.iso_week)
    background_tasks.add_task(_bg_run_alert_checks, report.iso_week)

    # 记录上传日志
    log = UploadLog(
        filename=filename,
        file_size=os.path.getsize(file_path),
        status="parsed",
        new_warehouses=str(report.new_warehouses),
        missing_warehouses=str(report.missing_warehouses),
        uploaded_by=user.id,
    )
    db.add(log)
    await db.commit()

    return ApiResponse[ParseReportResponse](data=ParseReportResponse(
        iso_week=report.iso_week,
        start_date=report.start_date,
        end_date=report.end_date,
        warehouses_found=report.warehouses_found,
        new_warehouses=report.new_warehouses,
        missing_warehouses=report.missing_warehouses,
        records_parsed=report.records_parsed,
    ))
