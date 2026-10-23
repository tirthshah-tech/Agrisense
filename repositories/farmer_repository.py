"""
AgriSense - Farmer Repository
Provides CRUD and filter operations for Farmer entities with hybrid DB/fallback support.
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timezone

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.farmer import Farmer

logger = logging.getLogger(__name__)


class FarmerRepository(BaseRepository):
    """Data access repository for Farmers."""

    def get_all(self) -> pd.DataFrame:
        """Retrieves all farmers as a pandas DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farmers = session.query(Farmer).all()
                    if farmers:
                        return pd.DataFrame([f.to_dict() for f in farmers])
            except Exception as e:
                logger.warning("Error fetching farmers from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("farmers.csv")

    # Backward compatibility alias
    def get_all_farmers(self) -> pd.DataFrame:
        return self.get_all()

    def get_by_id(self, farmer_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a specific farmer by primary key ID."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    f = session.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
                    if f:
                        return f.to_dict()
            except Exception as e:
                logger.warning("Error fetching farmer by id from MySQL: %s", e)

        df = self.get_all()
        if df.empty:
            return None
        match = df[df["farmer_id"] == farmer_id]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def get_farmer_by_id(self, farmer_id: int) -> Optional[Dict[str, Any]]:
        """Backward compatibility alias."""
        return self.get_by_id(farmer_id)

    def create(self, farmer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a new farmer record in MySQL or appends to local cache."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farmer = Farmer(
                        name=farmer_data["name"],
                        phone=farmer_data["phone"],
                        village=farmer_data["village"],
                        district=farmer_data["district"],
                        state=farmer_data.get("state", "Maharashtra"),
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(farmer)
                    session.flush()
                    return farmer.to_dict()
            except Exception as e:
                logger.error("Error creating farmer in MySQL: %s", e)
                raise
        return farmer_data

    def update(self, farmer_id: int, updates: Dict[str, Any]) -> bool:
        """Updates an existing farmer's details."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farmer = session.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
                    if not farmer:
                        return False
                    for key, val in updates.items():
                        if hasattr(farmer, key):
                            setattr(farmer, key, val)
                    return True
            except Exception as e:
                logger.error("Error updating farmer in MySQL: %s", e)
                return False
        return True

    def delete(self, farmer_id: int) -> bool:
        """Deletes a farmer by ID."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farmer = session.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
                    if not farmer:
                        return False
                    session.delete(farmer)
                    return True
            except Exception as e:
                logger.error("Error deleting farmer in MySQL: %s", e)
                return False
        return True

    def get_districts(self) -> List[str]:
        """Returns sorted list of distinct districts."""
        df = self.get_all()
        if df.empty or "district" not in df.columns:
            return []
        return sorted(df["district"].dropna().unique().tolist())
