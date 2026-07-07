from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WebhookConfigBase(BaseModel):
    warehouse_id: int
    webhook_url: str
    notify_users: Optional[str] = None
    is_active: bool = True
    message_template: Optional[str] = None
    schedule_enabled: bool = False
    schedule_day: Optional[int] = None
    schedule_time: Optional[str] = None


class WebhookConfigCreate(WebhookConfigBase):
    pass


class WebhookConfigUpdate(BaseModel):
    webhook_url: Optional[str] = None
    notify_users: Optional[str] = None
    is_active: Optional[bool] = None
    message_template: Optional[str] = None
    schedule_enabled: Optional[bool] = None
    schedule_day: Optional[int] = None
    schedule_time: Optional[str] = None


class WebhookConfigResponse(WebhookConfigBase):
    id: int
    warehouse_code: str
    warehouse_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PushRequest(BaseModel):
    warehouse_code: str
    iso_week: str
    chart_base64: str  # PNG base64，不含 data:image/png;base64, 前缀


class PushAllRequest(BaseModel):
    iso_week: str
    warehouse_codes: list[str]


class PushResponse(BaseModel):
    success: bool
    message: str
