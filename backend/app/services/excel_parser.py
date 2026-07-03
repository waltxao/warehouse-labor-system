import re
from datetime import datetime, date
from pathlib import Path
from openpyxl import load_workbook
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Warehouse, DailyRecord, WeeklyReport, UploadLog
from app.core.exceptions import AppException

WAREHOUSE_CODE_PATTERN = re.compile(r'^(\d{3,4}[A-Z]?|[A-Z]{2}\d{2})$')

METRIC_MAP = {
    "每日節省人數": "labor_savings",
    "每日节省人数": "labor_savings",
    "每日系统人数": "system_headcount",
    "每日系統人數": "system_headcount",
    "實際出勤人數": "actual_attendance",
    "实际出勤人数": "actual_attendance",
    "實際工作需求人數": "required_headcount_so",
    "实际工作需求人数": "required_headcount_so",
    "實際工作滿足率": "work_fulfillment_rate",
    "实际工作满足率": "work_fulfillment_rate",
}


class ParseReport:
    def __init__(self):
        self.iso_week: str = ""
        self.start_date: date = None
        self.end_date: date = None
        self.warehouses_found: list[str] = []
        self.new_warehouses: list[str] = []
        self.missing_warehouses: list[str] = []
        self.records_parsed: int = 0


async def parse_excel(file_path: str, db: AsyncSession, uploaded_by: int, force_overwrite: bool = False) -> ParseReport:
    wb = load_workbook(file_path, data_only=True)
    # 模糊匹配 sheet name
    sheet = None
    for ws in wb.worksheets:
        if "关键数据汇总" in ws.title or "關鍵數據匯總" in ws.title or "关键数据" in ws.title:
            sheet = ws
            break
    if not sheet:
        raise AppException(400, "找不到「关键数据汇总」Sheet")

    report = ParseReport()

    # 扫描表头行识别仓库代码列
    warehouse_cols: dict[int, str] = {}  # {col_index: warehouse_code}
    for row in sheet.iter_rows(min_row=1, max_row=5, values_only=False):
        for cell in row:
            val = str(cell.value).strip() if cell.value else ""
            if WAREHOUSE_CODE_PATTERN.match(val):
                warehouse_cols[cell.column] = val
                if val not in report.warehouses_found:
                    report.warehouses_found.append(val)

    if not warehouse_cols:
        raise AppException(400, "未识别到任何仓库代码")

    # 查询数据库已有仓库
    result = await db.execute(select(Warehouse))
    existing_warehouses = {w.code: w for w in result.scalars().all()}
    db_codes = set(existing_warehouses.keys())
    excel_codes = set(warehouse_cols.values())

    # 新仓库自动创建
    for code in excel_codes - db_codes:
        wh = Warehouse(code=code, name=code)
        db.add(wh)
        await db.flush()
        existing_warehouses[code] = wh
        report.new_warehouses.append(code)

    # 缺失仓库
    report.missing_warehouses = list(db_codes - excel_codes)

    # 扫描数据行
    metric_rows: list[tuple[str, int]] = []  # [(metric_field, row_index)]
    for row in sheet.iter_rows(min_row=1, values_only=False):
        project_cell = row[1] if len(row) > 1 else None  # B列 = 项目
        if project_cell and project_cell.value:
            val = str(project_cell.value).strip()
            if val in METRIC_MAP:
                metric_rows.append((METRIC_MAP[val], project_cell.row))

    # 解析每日数据
    all_dates: set[date] = set()
    parsed_records: dict[tuple[date, str], dict] = {}  # {(date, warehouse_code): {metric: value}}

    for metric_field, row_idx in metric_rows:
        # 在该指标行往下扫描 7 个数据行（周一~周日，忽略周日）
        for offset in range(1, 8):
            if row_idx + offset > sheet.max_row:
                break
            data_row = sheet[row_idx + offset]
            # A列或B列是日期
            date_cell = data_row[0] if data_row[0].value else (data_row[1] if len(data_row) > 1 and data_row[1].value else None)
            if not date_cell or not date_cell.value:
                continue

            row_date = _parse_date(date_cell.value)
            if not row_date:
                continue

            # 忽略周日
            if row_date.weekday() == 6:
                continue

            all_dates.add(row_date)
            dow = row_date.weekday() + 1  # 1=Mon ~ 6=Sat

            for col_idx, wh_code in warehouse_cols.items():
                cell_val = sheet.cell(row=row_idx + offset, column=col_idx).value
                if cell_val is None:
                    continue
                try:
                    val = float(cell_val)
                except (ValueError, TypeError):
                    continue

                key = (row_date, wh_code)
                if key not in parsed_records:
                    parsed_records[key] = {"date": row_date, "day_of_week": dow, "warehouse_code": wh_code}
                parsed_records[key][metric_field] = val

    if not all_dates:
        raise AppException(400, "未解析到任何日期数据")

    # 计算 ISO 周次
    report.start_date = min(all_dates)
    report.end_date = max(all_dates)
    iso_calendar = report.start_date.isocalendar()
    report.iso_week = f"{iso_calendar[0]}-W{iso_calendar[1]:02d}"

    # 检查冲突
    existing_report = await db.execute(
        select(WeeklyReport).where(WeeklyReport.iso_week == report.iso_week)
    )
    existing = existing_report.scalar_one_or_none()
    if existing and not force_overwrite:
        raise AppException(409, f"Week {report.iso_week} already exists", {"conflict": True, "iso_week": report.iso_week})

    if existing and force_overwrite:
        await db.execute(delete(DailyRecord).where(DailyRecord.weekly_report_id == existing.id))
        await db.execute(delete(WeeklyReport).where(WeeklyReport.id == existing.id))
        await db.flush()

    # 创建 weekly_report
    weekly_report = WeeklyReport(
        iso_week=report.iso_week,
        start_date=report.start_date,
        end_date=report.end_date,
        filename=Path(file_path).name,
        uploaded_by=uploaded_by,
    )
    db.add(weekly_report)
    await db.flush()

    # 创建 daily_records
    for (row_date, wh_code), data in parsed_records.items():
        wh = existing_warehouses[wh_code]
        record = DailyRecord(
            weekly_report_id=weekly_report.id,
            warehouse_id=wh.id,
            date=data["date"],
            day_of_week=data["day_of_week"],
            iso_week=report.iso_week,
            system_headcount=data.get("system_headcount"),
            actual_attendance=data.get("actual_attendance"),
            required_headcount_so=data.get("required_headcount_so"),
            labor_savings=data.get("labor_savings"),
            work_fulfillment_rate=data.get("work_fulfillment_rate"),
        )
        db.add(record)
        report.records_parsed += 1

    await db.commit()
    return report


def _parse_date(val) -> date | None:
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    s = str(val).strip()
    for fmt in ["%m/%d/%Y", "%Y/%m/%d", "%m/%d", "%Y-%m-%d"]:
        try:
            d = datetime.strptime(s, fmt).date()
            if fmt == "%m/%d":
                d = d.replace(year=datetime.now().year)
            return d
        except ValueError:
            continue
    return None
