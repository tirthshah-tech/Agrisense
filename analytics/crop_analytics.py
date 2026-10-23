"""
AgriSense - Crop Analytics Module
Statistical analysis of crop cycle duration, acreage distribution, and seasonal patterns.
Purely analytical / statistical (NO machine learning).
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from repositories.crop_repository import CropRepository


class CropAnalytics:
    """Statistical analytics for crop cycles and seasons."""

    def __init__(self):
        self.crop_repo = CropRepository()

    def get_cycle_duration_stats(self) -> pd.DataFrame:
        """
        Calculates descriptive statistics (mean, median, min, max, std)
        of crop cycle duration in days for completed/harvested cycles.
        """
        df = self.crop_repo.get_cycles_enriched()
        if df.empty or "sowing_date" not in df.columns or "harvest_date" not in df.columns:
            return pd.DataFrame()

        harvested = df[df["status"] == "Harvested"].copy()
        if harvested.empty:
            return pd.DataFrame()

        harvested["sowing"] = pd.to_datetime(harvested["sowing_date"])
        harvested["harvest"] = pd.to_datetime(harvested["harvest_date"])
        harvested["duration_days"] = (harvested["harvest"] - harvested["sowing"]).dt.days

        stats = harvested.groupby("crop_name")["duration_days"].agg(
            mean_days="mean",
            median_days="median",
            min_days="min",
            max_days="max",
            std_days="std"
        ).reset_index()

        stats["mean_days"] = stats["mean_days"].round(1)
        stats["std_days"] = stats["std_days"].fillna(0).round(1)
        return stats.sort_values("mean_days", ascending=False)

    def get_crop_area_share(self) -> pd.DataFrame:
        """Calculates percentage share of total cultivated area per crop."""
        df = self.crop_repo.get_cycles_enriched()
        if df.empty or "cultivated_area" not in df.columns or "crop_name" not in df.columns:
            return pd.DataFrame()

        total_area = df["cultivated_area"].sum()
        grouped = df.groupby("crop_name")["cultivated_area"].sum().reset_index()
        grouped["area_share_pct"] = ((grouped["cultivated_area"] / total_area) * 100).round(2)
        return grouped.sort_values("cultivated_area", ascending=False)
