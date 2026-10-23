"""
AgriSense - Soil Repository
Provides data access methods for Soil health records:
get_all(), get_by_farm(), get_date_range(), create().
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, date, timezone

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.soil_record import SoilRecord

logger = logging.getLogger(__name__)


class SoilRepository(BaseRepository):
    """Data access repository for Soil health records."""

    def get_all(self) -> pd.DataFrame:
        """Retrieves all soil monitoring records as a pandas DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    records = session.query(SoilRecord).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching soil records from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("soil_records.csv")

    # Backward compatibility alias
    def get_all_soil_records(self) -> pd.DataFrame:
        return self.get_all()

    def get_by_farm(self, farm_id: int) -> pd.DataFrame:
        """Retrieves soil records for a specific farm."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    records = session.query(SoilRecord).filter(SoilRecord.farm_id == farm_id).order_by(SoilRecord.record_date).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching soil records by farm from MySQL: %s", e)

        df = self.get_all()
        if df.empty or "farm_id" not in df.columns:
            return df
        return df[df["farm_id"] == farm_id].sort_values("record_date")

    def get_soil_by_farm(self, farm_id: int) -> pd.DataFrame:
        return self.get_by_farm(farm_id)

    def get_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Retrieves soil records within a specific date range."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    s_dt = date.fromisoformat(start_date)
                    e_dt = date.fromisoformat(end_date)
                    records = session.query(SoilRecord).filter(
                        SoilRecord.record_date >= s_dt,
                        SoilRecord.record_date <= e_dt
                    ).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching soil records by date range from MySQL: %s", e)

        df = self.get_all()
        if df.empty or "record_date" not in df.columns:
            return df
        mask = (df["record_date"] >= start_date) & (df["record_date"] <= end_date)
        return df[mask]

    def create(self, record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a new soil laboratory measurement record."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    rec = SoilRecord(
                        farm_id=record_data["farm_id"],
                        record_date=date.fromisoformat(str(record_data["record_date"])),
                        ph=record_data["ph"],
                        nitrogen=record_data["nitrogen"],
                        phosphorus=record_data["phosphorus"],
                        potassium=record_data["potassium"],
                        moisture_percentage=record_data.get("moisture_percentage") or record_data.get("moisture"),
                        organic_carbon=record_data.get("organic_carbon"),
                        electrical_conductivity=record_data.get("electrical_conductivity"),
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(rec)
                    session.flush()
                    return rec.to_dict()
            except Exception as e:
                logger.error("Error creating soil record in MySQL: %s", e)
                raise
        return record_data
