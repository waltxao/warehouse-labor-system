from sqlalchemy import Integer, String, Date, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from app.database import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    iso_week: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    daily_records: Mapped[list["DailyRecord"]] = relationship(back_populates="weekly_report", cascade="all, delete-orphan")


class DailyRecord(Base):
    __tablename__ = "daily_records"
    __table_args__ = (UniqueConstraint("warehouse_id", "date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weekly_report_id: Mapped[int] = mapped_column(ForeignKey("weekly_reports.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=Mon ~ 6=Sat
    iso_week: Mapped[str] = mapped_column(String(10), nullable=False)
    system_headcount: Mapped[float] = mapped_column(Float, nullable=True)
    actual_attendance: Mapped[float] = mapped_column(Float, nullable=True)
    required_headcount_so: Mapped[float] = mapped_column(Float, nullable=True)
    labor_savings: Mapped[float] = mapped_column(Float, nullable=True)
    work_fulfillment_rate: Mapped[float] = mapped_column(Float, nullable=True)
    weekly_report: Mapped["WeeklyReport"] = relationship(back_populates="daily_records")
