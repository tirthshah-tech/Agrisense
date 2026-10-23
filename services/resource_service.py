"""
AgriSense - Resource Consumption Service (Water & Fertilizer)
Enforces SDG 12 analytics: Water consumption by method, fertilizer intensity, and resource efficiency.
"""
from typing import Dict, Any
import pandas as pd

from repositories.resource_repository import ResourceRepository


class ResourceService:
    """Service layer for irrigation water and fertilizer analytics."""

    def __init__(self):
        self.resource_repo = ResourceRepository()

    def get_water_metrics(self) -> Dict[str, Any]:
        """Calculates macro metrics for water consumption."""
        irrig_df = self.resource_repo.get_all_irrigation_records()
        if irrig_df.empty:
            return {
                "total_water_liters": 0.0,
                "total_water_m3": 0.0,
                "total_irrigation_events": 0,
                "avg_liters_per_event": 0.0,
            }

        total_liters = float(irrig_df["water_used_liters"].sum())
        events = len(irrig_df)
        return {
            "total_water_liters": round(total_liters, 2),
            "total_water_m3": round(total_liters / 1000.0, 1),
            "total_irrigation_events": events,
            "avg_liters_per_event": round(total_liters / events, 1) if events > 0 else 0.0,
        }

    def get_water_by_method(self) -> pd.DataFrame:
        """Returns total water consumption broken down by irrigation method."""
        irrig_df = self.resource_repo.get_all_irrigation_records()
        if irrig_df.empty or "irrigation_method" not in irrig_df.columns:
            return pd.DataFrame()

        grouped = irrig_df.groupby("irrigation_method").agg(
            events=("irrigation_id", "count"),
            total_liters=("water_used_liters", "sum"),
            avg_liters=("water_used_liters", "mean"),
        ).reset_index()
        grouped["total_m3"] = (grouped["total_liters"] / 1000.0).round(1)
        grouped["avg_m3"] = (grouped["avg_liters"] / 1000.0).round(2)
        return grouped

    def get_fertilizer_metrics(self) -> Dict[str, Any]:
        """Calculates macro metrics for fertilizer usage."""
        fert_df = self.resource_repo.get_all_fertilizer_records()
        if fert_df.empty:
            return {
                "total_fertilizer_kg": 0.0,
                "total_applications": 0,
                "avg_qty_kg": 0.0,
            }

        total_kg = float(fert_df["quantity_kg"].sum())
        apps = len(fert_df)
        return {
            "total_fertilizer_kg": round(total_kg, 1),
            "total_applications": apps,
            "avg_qty_kg": round(total_kg / apps, 1) if apps > 0 else 0.0,
        }

    def get_fertilizer_by_type(self) -> pd.DataFrame:
        """Returns fertilizer usage breakdown by fertilizer chemical type."""
        fert_df = self.resource_repo.get_all_fertilizer_records()
        if fert_df.empty or "fertilizer_type" not in fert_df.columns:
            return pd.DataFrame()

        grouped = fert_df.groupby("fertilizer_type").agg(
            applications=("fertilizer_id", "count"),
            total_kg=("quantity_kg", "sum"),
        ).reset_index()
        grouped["total_kg"] = grouped["total_kg"].round(1)
        return grouped.sort_values("total_kg", ascending=False)
