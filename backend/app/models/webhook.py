from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class WebhookConfig(Base):
    __tablename__ = "webhook_configs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), unique=True, nullable=False)
    webhook_url: Mapped[str] = mapped_column(String(500), nullable=False)
    notify_users: Mapped[str] = mapped_column(String(500), nullable=True)  # 手机号逗号分隔
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    message_template: Mapped[str] = mapped_column(Text, nullable=True)  # 推送文字模板，支持变量
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, default=False)  # 定时推送开关
    schedule_day: Mapped[int] = mapped_column(Integer, nullable=True)  # 周几推送 0=周一...6=周日
    schedule_time: Mapped[str] = mapped_column(String(5), nullable=True)  # 推送时间 HH:MM
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", backref="webhook_config")
