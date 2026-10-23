"""Yield repository for harvest records."""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.yield_record import YieldRecord

logger = logging.getLogger(__name__)


class YieldRepository(BaseRepository):
    """Data access repository for Harvest Yield."""

    def get_all_yields(self) -> pd.DataFrame:
        """Retrieves all harvest yield records as a DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    records = session.query(YieldRecord).all()
                    if records:
                        return pd.DataFrame([r.to_dict() for r in records])
            except Exception as e:
                logger.warning("Error fetching yields from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("yield_records.csv")
