"""
AgriSense - Yield Analytics Module
Statistical analysis of crop harvest productivity, yield gap against standard benchmarks,
and quartile distributions. Purely data-driven (NO machine learning).
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from repositories.yield_repository import YieldRepository
from repositories.crop_repository import CropRepository


class YieldAnalytics:
    """Yield productivity and benchmark analytics."""

    def __init__(self):
        self.yield_repo = YieldRepository()
        self.crop_repo = CropRepository()

    def get_enriched_yields(self) -> pd.DataFrame:
        """Joins yield records with cycle details, crop metadata, and farm locations."""
        yields_df = self.yield_repo.get_all_yields()
        if yields_df.empty:
            return yields_df

        cycles_df = self.crop_repo.get_cycles_enriched()
        if cycles_df.empty:
            return yields_df

        merged = yields_df.merge(cycles_df, on="cycle_id", how="left")
        return merged

    def get_yield_performance_by_crop(self) -> pd.DataFrame:
        """
        Calculates mean, median, min, max, std of yield per hectare by crop,
        and evaluates the yield gap compared to agricultural reference standards.
        """
        df = self.get_enriched_yields()
        if df.empty or "crop_name" not in df.columns or "yield_per_hectare" not in df.columns:
            return pd.DataFrame()

        crops_df = self.crop_repo.get_all_crops()
        std_map = dict(zip(crops_df["crop_name"], crops_df["standard_yield_kg_per_ha"])) if not crops_df.empty else {}

        stats = df.groupby("crop_name")["yield_per_hectare"].agg(
            sample_count="count",
            mean_kg_ha="mean",
            median_kg_ha="median",
            min_kg_ha="min",
            max_kg_ha="max",
            std_kg_ha="std",
        ).reset_index()

        stats["standard_kg_ha"] = stats["crop_name"].map(std_map)
        stats["yield_gap_kg_ha"] = (stats["standard_kg_ha"] - stats["mean_kg_ha"]).round(1)
        stats["achievement_pct"] = ((stats["mean_kg_ha"] / stats["standard_kg_ha"]) * 100).round(1)

        stats["mean_kg_ha"] = stats["mean_kg_ha"].round(1)
        stats["std_kg_ha"] = stats["std_kg_ha"].fillna(0).round(1)
        return stats.sort_values("mean_kg_ha", ascending=False)

    def get_quality_grade_breakdown(self) -> pd.DataFrame:
        """Calculates proportion of harvested output categorized by quality grade."""
        df = self.yield_repo.get_all_yields()
        if df.empty or "quality_grade" not in df.columns:
            return pd.DataFrame()

        total = len(df)
        counts = df["quality_grade"].value_counts().reset_index()
        counts.columns = ["quality_grade", "count"]
        counts["percentage"] = ((counts["count"] / total) * 100).round(1)
        return counts
