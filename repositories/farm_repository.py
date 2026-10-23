"""
AgriSense - Farm Repository
Provides CRUD and filter operations for Farm landholding entities.
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timezone

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.farm import Farm

logger = logging.getLogger(__name__)


class FarmRepository(BaseRepository):
    """Data access repository for Farms."""

    def get_all(self) -> pd.DataFrame:
        """Retrieves all farms as a pandas DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farms = session.query(Farm).all()
                    if farms:
                        return pd.DataFrame([f.to_dict() for f in farms])
            except Exception as e:
                logger.warning("Error fetching farms from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("farms.csv")

    # Backward compatibility alias
    def get_all_farms(self) -> pd.DataFrame:
        return self.get_all()

    def get_by_id(self, farm_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single farm by its ID."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farm = session.query(Farm).filter(Farm.farm_id == farm_id).first()
                    if farm:
                        return farm.to_dict()
            except Exception as e:
                logger.warning("Error fetching farm by ID from MySQL: %s", e)

        df = self.get_all()
        if df.empty:
            return None
        match = df[df["farm_id"] == farm_id]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def get_farm_by_id(self, farm_id: int) -> Optional[Dict[str, Any]]:
        return self.get_by_id(farm_id)

    def get_by_farmer(self, farmer_id: int) -> pd.DataFrame:
        """Retrieves all farms owned by a specific farmer."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farms = session.query(Farm).filter(Farm.farmer_id == farmer_id).all()
                    if farms:
                        return pd.DataFrame([f.to_dict() for f in farms])
            except Exception as e:
                logger.warning("Error fetching farms by farmer from MySQL: %s", e)

        df = self.get_all()
        if df.empty:
            return df
        return df[df["farmer_id"] == farmer_id]

    def get_farms_by_farmer(self, farmer_id: int) -> pd.DataFrame:
        return self.get_by_farmer(farmer_id)

    def create(self, farm_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a new farm landholding in MySQL."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farm = Farm(
                        farmer_id=farm_data["farmer_id"],
                        farm_name=farm_data["farm_name"],
                        area_hectares=farm_data["area_hectares"],
                        soil_type=farm_data["soil_type"],
                        irrigation_type=farm_data["irrigation_type"],
                        location=farm_data.get("location"),
                        latitude=farm_data.get("latitude"),
                        longitude=farm_data.get("longitude"),
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(farm)
                    session.flush()
                    return farm.to_dict()
            except Exception as e:
                logger.error("Error creating farm in MySQL: %s", e)
                raise
        return farm_data

    def update(self, farm_id: int, updates: Dict[str, Any]) -> bool:
        """Updates an existing farm record."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farm = session.query(Farm).filter(Farm.farm_id == farm_id).first()
                    if not farm:
                        return False
                    for key, val in updates.items():
                        if hasattr(farm, key):
                            setattr(farm, key, val)
                    return True
            except Exception as e:
                logger.error("Error updating farm in MySQL: %s", e)
                return False
        return True

    def delete(self, farm_id: int) -> bool:
        """Deletes a farm record."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    farm = session.query(Farm).filter(Farm.farm_id == farm_id).first()
                    if not farm:
                        return False
                    session.delete(farm)
                    return True
            except Exception as e:
                logger.error("Error deleting farm in MySQL: %s", e)
                return False
        return True

    def get_soil_types(self) -> List[str]:
        """Returns sorted list of distinct soil types."""
        df = self.get_all()
        if df.empty or "soil_type" not in df.columns:
            return []
        return sorted(df["soil_type"].dropna().unique().tolist())

    def get_irrigation_types(self) -> List[str]:
        """Returns sorted list of distinct irrigation types."""
        df = self.get_all()
        if df.empty or "irrigation_type" not in df.columns:
            return []
        return sorted(df["irrigation_type"].dropna().unique().tolist())
