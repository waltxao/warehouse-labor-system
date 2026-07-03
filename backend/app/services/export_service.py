import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Warehouse, DailyRecord
from app.core.exceptions import AppException


async def export_excel(db: AsyncSession, warehouse_code: str, iso_week: str) -> bytes:
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

    wb = Workbook()
    ws = wb.active
    ws.title = f"{warehouse_code}_{iso_week}"
    ws.append(["日期", "星期", "系统人数", "实际出勤", "需求SO", "节省人数", "满足率"])
    for r in records_list:
        ws.append([
            str(r.date),
            r.day_of_week,
            r.system_headcount,
            r.actual_attendance,
            r.required_headcount_so,
            r.labor_savings,
            r.work_fulfillment_rate,
        ])

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


async def export_pdf(db: AsyncSession, warehouse_code: str, iso_week: str) -> bytes:
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

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph(f"{warehouse_code} - {iso_week}", styles["Title"]), Spacer(1, 20)]

    data = [["日期", "出勤", "需求SO", "节省", "满足率"]]
    for r in records_list:
        data.append([
            str(r.date),
            str(r.actual_attendance or ""),
            str(r.required_headcount_so or ""),
            str(r.labor_savings or ""),
            str(r.work_fulfillment_rate or ""),
        ])
    elements.append(Table(data))
    doc.build(elements)
    return buf.getvalue()
