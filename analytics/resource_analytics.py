"""
AgriSense - Resource Efficiency Analytics Module (SDG 12 & SDG 2)
Purely statistical resource productivity ratios, water intensity per kg yield,
fertilizer productivity, and irrigation method benchmarking. (Strictly non-AI/non-ML).
"""
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from repositories.resource_repository import ResourceRepository
from repositories.crop_repository import CropRepository
from repositories.yield_repository import YieldRepository


class ResourceAnalytics:
    """Statistical efficiency and intensity calculations for water, land, and agrochemical inputs."""

    def __init__(self):
        self.resource_repo = ResourceRepository()
        self.crop_repo = CropRepository()
        self.yield_repo = YieldRepository()

    def get_water_efficiency_by_method(self) -> pd.DataFrame:
        """
        Calculates water application intensity (liters per hectare)
        stratified by irrigation method (Drip, Sprinkler, Canal Flood, Tube Well).
        Highlights resource efficiency disparity under SDG 12.
        """
        irrig_df = self.resource_repo.get_all_irrigation_records()
        if irrig_df.empty:
            return pd.DataFrame()

        cycles_df = self.crop_repo.get_cycles_enriched()
        if cycles_df.empty:
            cycles_df = self.crop_repo.get_all_crop_cycles()

        area_col = "cultivated_area" if "cultivated_area" in cycles_df.columns else "cultivated_area_hectares"
        if area_col in cycles_df.columns:
            merged = irrig_df.merge(cycles_df[["cycle_id", area_col]], on="cycle_id", how="left")
            merged["cultivated_area"] = merged[area_col].fillna(2.0)
        else:
            merged = irrig_df.copy()
            merged["cultivated_area"] = 2.0

        merged["cultivated_area"] = merged["cultivated_area"].replace(0, np.nan).fillna(2.0)
        merged["liters_per_ha"] = merged["water_used_liters"] / merged["cultivated_area"]

        summary = merged.groupby("irrigation_method")["liters_per_ha"].agg(
            events="count",
            mean_liters_ha="mean",
            median_liters_ha="median",
            min_liters_ha="min",
            max_liters_ha="max",
            std_liters_ha="std",
        ).reset_index()

        summary["mean_m3_ha"] = (summary["mean_liters_ha"] / 1000.0).round(1)
        summary["median_m3_ha"] = (summary["median_liters_ha"] / 1000.0).round(1)
        summary["std_liters_ha"] = summary["std_liters_ha"].fillna(0).round(1)
        return summary.sort_values("mean_liters_ha")

    def get_water_productivity_ratio(self) -> pd.DataFrame:
        """
        Calculates Water Productivity:
        1. Liters of irrigation water consumed per Kilogram of crop yield produced (Water footprint).
        2. Kilograms of harvest yield produced per Cubic Meter (m3) of water consumed (Productivity).
        """
        irrig_df = self.resource_repo.get_all_irrigation_records()
        yields_df = self.yield_repo.get_all_yields()
        cycles_df = self.crop_repo.get_cycles_enriched()

        if irrig_df.empty or yields_df.empty:
            return pd.DataFrame()

        # Sum water per cycle
        water_per_cycle = irrig_df.groupby("cycle_id")["water_used_liters"].sum().reset_index()

        # Merge with yield and crop info
        prod = yields_df.merge(water_per_cycle, on="cycle_id", how="inner")
        if not cycles_df.empty and "crop_name" in cycles_df.columns:
            prod = prod.merge(cycles_df[["cycle_id", "crop_name"]].drop_duplicates("cycle_id"), on="cycle_id", how="left")

        # Zero-division guards
        prod["yield_kg"] = prod["yield_kg"].replace(0, np.nan)
        prod["water_used_liters"] = prod["water_used_liters"].replace(0, np.nan)

        prod["liters_per_kg_yield"] = (prod["water_used_liters"] / prod["yield_kg"]).round(2)
        prod["kg_yield_per_m3_water"] = (prod["yield_kg"] / (prod["water_used_liters"] / 1000.0)).round(2)

        stats = prod.groupby("crop_name").agg(
            completed_cycles=("cycle_id", "count"),
            avg_liters_per_kg=("liters_per_kg_yield", "mean"),
            avg_kg_per_m3=("kg_yield_per_m3_water", "mean"),
            total_harvest_kg=("yield_kg", "sum"),
            total_water_m3=("water_used_liters", lambda s: (s.sum() / 1000.0)),
        ).reset_index().round(2)

        return stats.sort_values("avg_kg_per_m3", ascending=False)

    def get_fertilizer_intensity_per_ha(self) -> pd.DataFrame:
        """Calculates kg of fertilizer applied per hectare across crops."""
        fert_df = self.resource_repo.get_all_fertilizer_records()
        cycles_df = self.crop_repo.get_cycles_enriched()

        if fert_df.empty or cycles_df.empty:
            return pd.DataFrame()

        fert_by_cycle = fert_df.groupby("cycle_id")["quantity_kg"].sum().reset_index()
        merged = fert_by_cycle.merge(cycles_df[["cycle_id", "crop_name", "cultivated_area"]].drop_duplicates("cycle_id"), on="cycle_id", how="inner")

        merged["cultivated_area"] = merged["cultivated_area"].replace(0, np.nan).fillna(1.0)
        merged["fert_kg_per_ha"] = merged["quantity_kg"] / merged["cultivated_area"]

        stats = merged.groupby("crop_name")["fert_kg_per_ha"].agg(
            mean_kg_ha="mean",
            median_kg_ha="median",
            min_kg_ha="min",
            max_kg_ha="max",
        ).reset_index().round(1)

        return stats.sort_values("mean_kg_ha", ascending=False)

    def get_fertilizer_productivity_ratio(self) -> pd.DataFrame:
        """
        Calculates Fertilizer Productivity:
        Kilograms of harvest output produced per Kilogram of fertilizer input applied (kg yield / kg fertilizer).
        """
        fert_df = self.resource_repo.get_all_fertilizer_records()
        yields_df = self.yield_repo.get_all_yields()
        cycles_df = self.crop_repo.get_cycles_enriched()

        if fert_df.empty or yields_df.empty:
            return pd.DataFrame()

        fert_by_cycle = fert_df.groupby("cycle_id")["quantity_kg"].sum().reset_index()
        merged = yields_df.merge(fert_by_cycle, on="cycle_id", how="inner")
        if not cycles_df.empty and "crop_name" in cycles_df.columns:
            merged = merged.merge(cycles_df[["cycle_id", "crop_name"]].drop_duplicates("cycle_id"), on="cycle_id", how="left")

        merged["quantity_kg"] = merged["quantity_kg"].replace(0, np.nan)
        merged["kg_yield_per_kg_fert"] = (merged["yield_kg"] / merged["quantity_kg"]).round(2)

        stats = merged.groupby("crop_name").agg(
            completed_cycles=("cycle_id", "count"),
            avg_kg_per_kg_fert=("kg_yield_per_kg_fert", "mean"),
            median_kg_per_kg_fert=("kg_yield_per_kg_fert", "median"),
            total_fert_applied_kg=("quantity_kg", "sum"),
            total_harvest_kg=("yield_kg", "sum"),
        ).reset_index().round(2)

        return stats.sort_values("avg_kg_per_kg_fert", ascending=False)

    def get_resource_efficiency_master_table(self) -> pd.DataFrame:
        """
        Builds a comprehensive, cycle-level resource efficiency master table combining:
        Yield, Cultivated Area, Land Productivity (kg/ha), Water Consumption, Water Productivity (kg/m3),
        Fertilizer Application, and Fertilizer Productivity (kg/kg).
        Includes zero-division guards and strict audit traceability.
        """
        yields_df = self.yield_repo.get_all_yields()
        cycles_df = self.crop_repo.get_cycles_enriched()
        irrig_df = self.resource_repo.get_all_irrigation_records()
        fert_df = self.resource_repo.get_all_fertilizer_records()

        if yields_df.empty or cycles_df.empty:
            return pd.DataFrame()

        # Aggregate inputs per cycle
        water_agg = irrig_df.groupby("cycle_id").agg(
            total_water_liters=("water_used_liters", "sum"),
            irrigation_events=("irrigation_id", "count"),
            primary_method=("irrigation_method", lambda s: s.mode().iloc[0] if not s.empty else "Standard"),
        ).reset_index() if not irrig_df.empty else pd.DataFrame(columns=["cycle_id", "total_water_liters", "irrigation_events", "primary_method"])

        fert_agg = fert_df.groupby("cycle_id").agg(
            total_fertilizer_kg=("quantity_kg", "sum"),
            fertilizer_events=("fertilizer_id", "count"),
        ).reset_index() if not fert_df.empty else pd.DataFrame(columns=["cycle_id", "total_fertilizer_kg", "fertilizer_events"])

        # Base merge on completed harvests
        master = yields_df.merge(cycles_df, on="cycle_id", how="inner")
        master = master.merge(water_agg, on="cycle_id", how="left")
        master = master.merge(fert_agg, on="cycle_id", how="left")

        # Fill missing resource inputs with 0.0
        master["total_water_liters"] = master["total_water_liters"].fillna(0.0)
        master["total_fertilizer_kg"] = master["total_fertilizer_kg"].fillna(0.0)
        master["irrigation_events"] = master["irrigation_events"].fillna(0).astype(int)
        master["fertilizer_events"] = master["fertilizer_events"].fillna(0).astype(int)
        master["primary_method"] = master["primary_method"].fillna("Not Specified")

        # Safe area column
        area_col = "cultivated_area" if "cultivated_area" in master.columns else "cultivated_area_hectares"
        master["area_ha"] = master[area_col].replace(0, np.nan).fillna(1.0)

        # 1. Land Productivity (kg / ha)
        master["land_productivity_kg_ha"] = (master["yield_kg"] / master["area_ha"]).round(1)

        # 2. Water Intensities & Productivity
        master["water_per_ha_m3"] = ((master["total_water_liters"] / 1000.0) / master["area_ha"]).round(1)
        master["water_productivity_kg_m3"] = np.where(
            master["total_water_liters"] > 0,
            (master["yield_kg"] / (master["total_water_liters"] / 1000.0)).round(2),
            0.0
        )

        # 3. Fertilizer Intensities & Productivity
        master["fert_per_ha_kg"] = (master["total_fertilizer_kg"] / master["area_ha"]).round(1)
        master["fert_productivity_kg_kg"] = np.where(
            master["total_fertilizer_kg"] > 0,
            (master["yield_kg"] / master["total_fertilizer_kg"]).round(2),
            0.0
        )

        select_cols = [
            "cycle_id", "farm_id", "farm_name", "crop_name", "season_name",
            "area_ha", "yield_kg", "land_productivity_kg_ha", "quality_grade",
            "total_water_liters", "water_per_ha_m3", "water_productivity_kg_m3", "primary_method",
            "total_fertilizer_kg", "fert_per_ha_kg", "fert_productivity_kg_kg"
        ]
        available_cols = [c for c in select_cols if c in master.columns]
        return master[available_cols].sort_values("yield_kg", ascending=False)
