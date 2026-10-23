"""Resource consumption repository (Irrigation water & Fertilizer)."""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.irrigation_record import IrrigationRecord
from models.fertilizer_record import FertilizerRecord

logger = logging.getLogger(__name__)


class ResourceRepository(BaseRepository):
    """Data access repository for Water and Fertilizer consumption."""

    def get_all_irrigation_records(self) -> pd.DataFrame:
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

    def get_all_fertilizer_records(self) -> pd.DataFrame:
        """Retrieves all fertilizer usage records as a DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    records = session.query(FertilizerRecord).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching fertilizer records from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("fertilizer_records.csv")
