from pydantic import BaseModel


class AIAnalysisRequest(BaseModel):
    type: str  # weekly_compare / multi_warehouse / monthly_trend / anomaly_detection
    warehouse_codes: list[str]
    iso_week: str


class AIAnalysisResponse(BaseModel):
    report: str
    log_id: int
