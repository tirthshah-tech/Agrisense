"""
AgriSense - Crop & Cycle Service
Business logic for crops, seasonal rotation, cycle status, and crop distribution.
"""
from typing import Dict, Any, List
import pandas as pd

from repositories.crop_repository import CropRepository


class CropService:
    """Service layer for Crops and Crop Cycles."""

    def __init__(self):
        self.crop_repo = CropRepository()

    def get_crop_summary(self) -> Dict[str, Any]:
        """Calculates macro metrics for crops and cycles."""
        crops_df = self.crop_repo.get_all_crops()
        cycles_df = self.crop_repo.get_all_crop_cycles()

        total_crops = len(crops_df) if not crops_df.empty else 0
        total_cycles = len(cycles_df) if not cycles_df.empty else 0
        active_cycles = len(cycles_df[cycles_df["status"] == "Active"]) if not cycles_df.empty and "status" in cycles_df.columns else 0
        harvested_cycles = len(cycles_df[cycles_df["status"] == "Harvested"]) if not cycles_df.empty and "status" in cycles_df.columns else 0

        return {
            "total_crops": total_crops,
            "total_cycles": total_cycles,
            "active_cycles": active_cycles,
            "harvested_cycles": harvested_cycles,
        }

    def get_cycles_by_crop(self) -> pd.DataFrame:
        """Returns cycle counts and cultivated area grouped by crop name."""
        enriched = self.crop_repo.get_cycles_enriched()
        if enriched.empty or "crop_name" not in enriched.columns:
            return pd.DataFrame()

        grouped = enriched.groupby(["crop_name", "crop_category"]).agg(
            cycle_count=("cycle_id", "count"),
            total_cultivated_ha=("cultivated_area", "sum")
        ).reset_index()
        grouped["total_cultivated_ha"] = grouped["total_cultivated_ha"].round(2)
        return grouped.sort_values("total_cultivated_ha", ascending=False)
