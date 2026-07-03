from pydantic import BaseModel
from datetime import date


class TrendPoint(BaseModel):
    date: date
    day_of_week: int
    actual_attendance: float | None
    required_headcount_so: float | None
    three_month_average: float | None
    is_partial: bool


class TrendData(BaseModel):
    warehouse_code: str
    iso_week: str
    points: list[TrendPoint]


class ChartData(BaseModel):
    warehouse_code: str
    iso_week: str
    dates: list[str]
    attendance: list[float | None]
    required_so: list[float | None]
    three_month_avg: list[float | None]
    is_partial: list[bool]
