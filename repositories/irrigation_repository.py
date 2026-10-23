"""
AgriSense - Irrigation Repository
Provides data access methods for Irrigation records:
get_all(), get_by_farm(), get_date_range(), create().
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, date, timezone

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.irrigation_record import IrrigationRecord

logger = logging.getLogger(__name__)


class IrrigationRepository(BaseRepository):
    """Data access repository for Irrigation water usage records."""

    def get_all(self) -> pd.DataFrame:
        """Retrieves all irrigation records as a DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    records = session.query(IrrigationRecord).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching irrigation records from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("irrigation_records.csv")

    def get_by_farm(self, farm_id: int) -> pd.DataFrame:
        """Retrieves irrigation records for a specific farm."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    records = session.query(IrrigationRecord).filter(IrrigationRecord.farm_id == farm_id).order_by(IrrigationRecord.date).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching irrigation records by farm from MySQL: %s", e)

        df = self.get_all()
        if df.empty or "farm_id" not in df.columns:
            return df
        return df[df["farm_id"] == farm_id].sort_values("date")

    def get_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Retrieves irrigation records within a specific date range."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    s_dt = date.fromisoformat(start_date)
                    e_dt = date.fromisoformat(end_date)
                    records = session.query(IrrigationRecord).filter(
                        IrrigationRecord.date >= s_dt,
                        IrrigationRecord.date <= e_dt
                    ).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching irrigation records by date range from MySQL: %s", e)

        df = self.get_all()
        if df.empty or "date" not in df.columns:
            return df
        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        return df[mask]

    def create(self, record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a new irrigation log record."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    duration_min = record_data.get("duration_minutes")
                    if duration_min is None and "duration_hours" in record_data:
                        duration_min = int(float(record_data["duration_hours"]) * 60)

                    rec = IrrigationRecord(
                        farm_id=record_data["farm_id"],
                        cycle_id=record_data.get("cycle_id"),
                        date=date.fromisoformat(str(record_data["date"])),
                        water_used_liters=record_data["water_used_liters"],
                        irrigation_method=record_data["irrigation_method"],
                        duration_minutes=duration_min,
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(rec)
                    session.flush()
                    return rec.to_dict()
            except Exception as e:
                logger.error("Error creating irrigation record in MySQL: %s", e)
                raise
        return record_data
