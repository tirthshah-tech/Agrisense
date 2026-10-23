"""
AgriSense - Crop Cycle Repository
Provides CRUD and filter operations for CropCycle entities:
get_all(), get_by_id(), get_by_farm(), get_by_crop(), get_by_season(), create(), update().
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, date, timezone

from repositories.base_repository import BaseRepository
from database.mysql_connection import get_db_session
from models.crop_cycle import CropCycle
from models.crop import Crop
from models.season import Season
from models.farm import Farm

logger = logging.getLogger(__name__)


class CropCycleRepository(BaseRepository):
    """Data access repository for Crop Cycles."""

    def get_all(self) -> pd.DataFrame:
        """Retrieves all crop cycles as a pandas DataFrame."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    cycles = session.query(CropCycle).all()
                    if cycles:
                        return pd.DataFrame([cy.to_dict() for cy in cycles])
            except Exception as e:
                logger.warning("Error fetching crop cycles from MySQL, using fallback: %s", e)

        df = self.load_csv_fallback("crop_cycles.csv")
        if not df.empty and "cultivated_area_hectares" in df.columns and "cultivated_area" not in df.columns:
            df["cultivated_area"] = df["cultivated_area_hectares"]
        return df

    # Backward compatibility alias
    def get_all_crop_cycles(self) -> pd.DataFrame:
        return self.get_all()

    def get_by_id(self, cycle_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single crop cycle by ID."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    c = session.query(CropCycle).filter(CropCycle.cycle_id == cycle_id).first()
                    if c:
                        return c.to_dict()
            except Exception as e:
                logger.warning("Error fetching cycle by ID from MySQL: %s", e)

        df = self.get_all()
        if df.empty:
            return None
        match = df[df["cycle_id"] == cycle_id]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def get_by_farm(self, farm_id: int) -> pd.DataFrame:
        """Retrieves all crop cycles for a specific farm."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    cycles = session.query(CropCycle).filter(CropCycle.farm_id == farm_id).all()
                    if cycles:
                        return pd.DataFrame([cy.to_dict() for cy in cycles])
            except Exception as e:
                logger.warning("Error fetching cycles by farm from MySQL: %s", e)

        df = self.get_all()
        if df.empty or "farm_id" not in df.columns:
            return df
        return df[df["farm_id"] == farm_id]

    def get_by_crop(self, crop_id: int) -> pd.DataFrame:
        """Retrieves all crop cycles for a specific crop."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    cycles = session.query(CropCycle).filter(CropCycle.crop_id == crop_id).all()
                    if cycles:
                        return pd.DataFrame([cy.to_dict() for cy in cycles])
            except Exception as e:
                logger.warning("Error fetching cycles by crop from MySQL: %s", e)

        df = self.get_all()
        if df.empty or "crop_id" not in df.columns:
            return df
        return df[df["crop_id"] == crop_id]

    def get_by_season(self, season_id: int) -> pd.DataFrame:
        """Retrieves all crop cycles for a specific season."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    cycles = session.query(CropCycle).filter(CropCycle.season_id == season_id).all()
                    if cycles:
                        return pd.DataFrame([cy.to_dict() for cy in cycles])
            except Exception as e:
                logger.warning("Error fetching cycles by season from MySQL: %s", e)

        df = self.get_all()
        if df.empty or "season_id" not in df.columns:
            return df
        return df[df["season_id"] == season_id]

    def create(self, cycle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a new crop cycle in MySQL."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    cycle = CropCycle(
                        farm_id=cycle_data["farm_id"],
                        crop_id=cycle_data["crop_id"],
                        season_id=cycle_data["season_id"],
                        sowing_date=date.fromisoformat(str(cycle_data["sowing_date"])),
                        expected_harvest_date=date.fromisoformat(str(cycle_data["expected_harvest_date"])) if cycle_data.get("expected_harvest_date") else None,
                        actual_harvest_date=date.fromisoformat(str(cycle_data["actual_harvest_date"])) if cycle_data.get("actual_harvest_date") else None,
                        cultivated_area_hectares=cycle_data.get("cultivated_area_hectares") or cycle_data.get("cultivated_area"),
                        status=cycle_data.get("status", "Active"),
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(cycle)
                    session.flush()
                    return cycle.to_dict()
            except Exception as e:
                logger.error("Error creating crop cycle in MySQL: %s", e)
                raise
        return cycle_data

    def update(self, cycle_id: int, updates: Dict[str, Any]) -> bool:
        """Updates an existing crop cycle (e.g. marking actual harvest date and Harvested status)."""
        if self.is_mysql_available():
            try:
                with get_db_session() as session:
                    cycle = session.query(CropCycle).filter(CropCycle.cycle_id == cycle_id).first()
                    if not cycle:
                        return False
                    for key, val in updates.items():
                        if hasattr(cycle, key):
                            if "date" in key and isinstance(val, str):
                                val = date.fromisoformat(val)
                            setattr(cycle, key, val)
                    return True
            except Exception as e:
                logger.error("Error updating crop cycle in MySQL: %s", e)
                return False
        return True

    def get_cycles_enriched(self) -> pd.DataFrame:
        """
        Returns joined DataFrame of crop cycles enriched with Farm name,
        Crop name, Season name, and Year.
        """
        cycles_df = self.get_all()
        if cycles_df.empty:
            return cycles_df

        from repositories.crop_repository import CropRepository
        crop_repo = CropRepository()
        crops_df = crop_repo.get_all()
        seasons_df = crop_repo.get_all_seasons()
        farms_df = self.load_csv_fallback("farms.csv")

        merged = cycles_df.copy()
        if not crops_df.empty:
            merged = merged.merge(crops_df[["crop_id", "crop_name", "crop_category"]], on="crop_id", how="left")
        if not seasons_df.empty:
            merged = merged.merge(seasons_df[["season_id", "season_name", "year"]], on="season_id", how="left")
        if not farms_df.empty:
            merged = merged.merge(farms_df[["farm_id", "farm_name", "location", "area_hectares"]], on="farm_id", how="left")

        # Normalize column names for UI/analytics layer compatibility
        if "cultivated_area_hectares" in merged.columns and "cultivated_area" not in merged.columns:
            merged["cultivated_area"] = merged["cultivated_area_hectares"]
        # harvest_date: prefer actual, fall back to expected
        if "harvest_date" not in merged.columns:
            if "actual_harvest_date" in merged.columns:
                merged["harvest_date"] = merged["actual_harvest_date"]
            elif "expected_harvest_date" in merged.columns:
                merged["harvest_date"] = merged["expected_harvest_date"]
        # Derive year from sowing_date if not already present from seasons join
        if "year" not in merged.columns and "sowing_date" in merged.columns:
            merged["year"] = pd.to_datetime(merged["sowing_date"], errors="coerce").dt.year
        if "season_name" not in merged.columns:
            merged["season_name"] = "Unknown"

        return merged
