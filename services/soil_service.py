"""
AgriSense - Soil Health Service
Calculates soil statistical distributions, nutrient ratings, and pH categorization.
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from repositories.soil_repository import SoilRepository
from utils.helpers import classify_soil_ph, classify_soil_nutrient


class SoilService:
    """Service layer for Soil Health analytics."""

    def __init__(self):
        self.soil_repo = SoilRepository()

    def get_soil_summary_metrics(self) -> Dict[str, Any]:
        """Calculates central tendency and dispersion metrics for soil health."""
        df = self.soil_repo.get_all_soil_records()
        if df.empty:
            return {
                "total_records": 0,
                "avg_ph": 0.0,
                "avg_nitrogen": 0.0,
                "avg_phosphorus": 0.0,
                "avg_potassium": 0.0,
                "avg_moisture": 0.0,
            }

        # Column may be 'moisture_percentage' (CSV/ORM) or 'moisture' (legacy)
        moisture_col = "moisture_percentage" if "moisture_percentage" in df.columns else "moisture"

        return {
            "total_records": len(df),
            "avg_ph": round(float(df["ph"].mean()), 2),
            "avg_nitrogen": round(float(df["nitrogen"].mean()), 1),
            "avg_phosphorus": round(float(df["phosphorus"].mean()), 1),
            "avg_potassium": round(float(df["potassium"].mean()), 1),
            "avg_moisture": round(float(df[moisture_col].mean()), 1),
        }

    def get_ph_distribution(self) -> pd.DataFrame:
        """Categorizes soil records into agronomic pH bands."""
        df = self.soil_repo.get_all_soil_records()
        if df.empty or "ph" not in df.columns:
            return pd.DataFrame()

        df_copy = df.copy()
        df_copy["ph_band"] = df_copy["ph"].apply(classify_soil_ph)
        counts = df_copy["ph_band"].value_counts().reset_index()
        counts.columns = ["ph_band", "sample_count"]
        return counts

    def get_npk_deficiency_rates(self) -> Dict[str, float]:
        """Calculates percentage of samples below optimal threshold (Low status)."""
        df = self.soil_repo.get_all_soil_records()
        if df.empty:
            return {"N_low_pct": 0.0, "P_low_pct": 0.0, "K_low_pct": 0.0}

        n_low = (df["nitrogen"] < 280).mean() * 100
        p_low = (df["phosphorus"] < 10).mean() * 100
        k_low = (df["potassium"] < 110).mean() * 100

        return {
            "N_low_pct": round(float(n_low), 1),
            "P_low_pct": round(float(p_low), 1),
            "K_low_pct": round(float(k_low), 1),
        }
