from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base


class ThreeMonthAverage(Base):
    __tablename__ = "three_month_averages"
    __table_args__ = (UniqueConstraint("warehouse_id", "iso_week", "day_of_week"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    iso_week: Mapped[str] = mapped_column(String(10), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    average_value: Mapped[float] = mapped_column(Float, nullable=False)
    is_partial: Mapped[bool] = mapped_column(Boolean, default=False)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
