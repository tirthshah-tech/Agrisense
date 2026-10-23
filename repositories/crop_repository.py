"""
AgriSense - Crop Repository
Provides CRUD and filter operations for Crop and Season reference entities.
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timezone

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.crop import Crop
from models.season import Season

logger = logging.getLogger(__name__)


class CropRepository(BaseRepository):
    """Data access repository for Crops and Seasons."""

    def get_all(self) -> pd.DataFrame:
        """Retrieves all crops as a pandas DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    crops = session.query(Crop).all()
                    if crops:
                        return pd.DataFrame([c.to_dict() for c in crops])
            except Exception as e:
                logger.warning("Error fetching crops from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("crops.csv")

    # Backward compatibility alias
    def get_all_crops(self) -> pd.DataFrame:
        return self.get_all()

    def get_by_id(self, crop_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a specific crop by ID."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    crop = session.query(Crop).filter(Crop.crop_id == crop_id).first()
                    if crop:
                        return crop.to_dict()
            except Exception as e:
                logger.warning("Error fetching crop by ID from MySQL: %s", e)

        df = self.get_all()
        if df.empty:
            return None
        match = df[df["crop_id"] == crop_id]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def create(self, crop_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a new crop variety."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    crop = Crop(
                        crop_name=crop_data["crop_name"],
                        crop_category=crop_data["crop_category"],
                        ideal_season=crop_data["ideal_season"],
                        ideal_soil_type=crop_data["ideal_soil_type"],
                        typical_growth_days=crop_data.get("typical_growth_days", 120),
                        water_requirement_mm=crop_data.get("water_requirement_mm"),
                        standard_yield_kg_per_ha=crop_data.get("standard_yield_kg_per_ha"),
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(crop)
                    session.flush()
                    return crop.to_dict()
            except Exception as e:
                logger.error("Error creating crop in MySQL: %s", e)
                raise
        return crop_data

    def get_all_seasons(self) -> pd.DataFrame:
        """Retrieves all agricultural seasons."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    seasons = session.query(Season).all()
                    if seasons:
                        return pd.DataFrame([s.to_dict() for s in seasons])
            except Exception as e:
                logger.warning("Error fetching seasons from MySQL, using fallback: %s", e)

        return self.load_csv_fallback("seasons.csv")

    # Backward compatibility delegate to CropCycleRepository
    def get_all_crop_cycles(self) -> pd.DataFrame:
        from repositories.crop_cycle_repository import CropCycleRepository
        return CropCycleRepository().get_all()

    def get_cycles_enriched(self) -> pd.DataFrame:
        from repositories.crop_cycle_repository import CropCycleRepository
        return CropCycleRepository().get_cycles_enriched()
