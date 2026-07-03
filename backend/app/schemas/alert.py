from pydantic import BaseModel


class AlertRuleCreate(BaseModel):
    name: str
    metric: str
    condition_type: str
    operator: str
    threshold_value: float | None = None
    consecutive_days: int | None = None
    scope: str = "all"
    warehouse_id: int | None = None


class AlertRuleResponse(BaseModel):
    id: int
    name: str
    metric: str
    condition_type: str
    operator: str
    threshold_value: float | None
    consecutive_days: int | None
    scope: str
    warehouse_id: int | None
    is_active: bool


class AlertRuleUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    threshold_value: float | None = None
    consecutive_days: int | None = None
