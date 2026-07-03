from pydantic import BaseModel
from datetime import date


class ParseReportResponse(BaseModel):
    iso_week: str
    start_date: date
    end_date: date
    warehouses_found: list[str]
    new_warehouses: list[str]
    missing_warehouses: list[str]
    records_parsed: int
