"""
AgriSense - Farm and Farmer Service
Coordinates business logic, entity aggregation, and summary statistics for Farms.
"""
from typing import Dict, Any, List, Optional
import pandas as pd

from repositories.farmer_repository import FarmerRepository
from repositories.farm_repository import FarmRepository


class FarmService:
    """Service layer for farms and farmers operations."""

    def __init__(self):
        self.farmer_repo = FarmerRepository()
        self.farm_repo = FarmRepository()

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates macro-level farm and farmer KPIs."""
        farmers_df = self.farmer_repo.get_all_farmers()
        farms_df = self.farm_repo.get_all_farms()

        total_farmers = len(farmers_df) if not farmers_df.empty else 0
        total_farms = len(farms_df) if not farms_df.empty else 0
        total_area = round(farms_df["area_hectares"].sum(), 2) if not farms_df.empty and "area_hectares" in farms_df.columns else 0.0
        avg_farm_size = round(farms_df["area_hectares"].mean(), 2) if total_farms > 0 else 0.0

        return {
            "total_farmers": total_farmers,
            "total_farms": total_farms,
            "total_cultivated_area_ha": total_area,
            "avg_farm_size_ha": avg_farm_size,
        }

    def get_farms_by_soil_type(self) -> pd.DataFrame:
        """Returns distribution of farms by soil type."""
        farms_df = self.farm_repo.get_all_farms()
        if farms_df.empty or "soil_type" not in farms_df.columns:
            return pd.DataFrame(columns=["soil_type", "count", "total_area_ha"])

        grouped = farms_df.groupby("soil_type").agg(
            count=("farm_id", "count"),
            total_area_ha=("area_hectares", "sum")
        ).reset_index()
        grouped["total_area_ha"] = grouped["total_area_ha"].round(2)
        return grouped

    def get_farms_by_irrigation_type(self) -> pd.DataFrame:
        """Returns distribution of farms by irrigation method."""
        farms_df = self.farm_repo.get_all_farms()
        if farms_df.empty or "irrigation_type" not in farms_df.columns:
            return pd.DataFrame(columns=["irrigation_type", "count", "total_area_ha"])

        grouped = farms_df.groupby("irrigation_type").agg(
            count=("farm_id", "count"),
            total_area_ha=("area_hectares", "sum")
        ).reset_index()
        grouped["total_area_ha"] = grouped["total_area_ha"].round(2)
        return grouped

    def get_farmers_by_district(self) -> pd.DataFrame:
        """Returns distribution of farmers across Maharashtra districts."""
        farmers_df = self.farmer_repo.get_all_farmers()
        if farmers_df.empty or "district" not in farmers_df.columns:
            return pd.DataFrame(columns=["district", "count"])

        return farmers_df["district"].value_counts().reset_index().rename(columns={"count": "farmer_count"})
