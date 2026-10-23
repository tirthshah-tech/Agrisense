"""
AgriSense - Weather & Environmental Analytics Service
Aggregates telemetry from meteorological stations in Maharashtra.
"""
from typing import Dict, Any
import pandas as pd

from repositories.observation_repository import ObservationRepository


class WeatherService:
    """Service layer for weather observations and climate analytics."""

    def __init__(self):
        self.obs_repo = ObservationRepository()

    @staticmethod
    def _normalize_weather_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes weather DataFrame columns so downstream code always has:
        'temperature', 'humidity', 'rainfall_mm', 'wind_speed_kmh'
        regardless of whether data came from MongoDB or the JSON fallback.
        """
        if df.empty:
            return df
        df = df.copy()
        if "temperature_c" in df.columns and "temperature" not in df.columns:
            df["temperature"] = df["temperature_c"]
        if "humidity_percentage" in df.columns and "humidity" not in df.columns:
            df["humidity"] = df["humidity_percentage"]
        if "wind_speed_kmh" not in df.columns and "wind_speed" in df.columns:
            df["wind_speed_kmh"] = df["wind_speed"]
        if "rainfall_mm" not in df.columns and "rainfall" in df.columns:
            df["rainfall_mm"] = df["rainfall"]
        return df

    def get_weather_summary(self) -> Dict[str, Any]:
        """Calculates central tendency values for meteorological readings."""
        df = self._normalize_weather_df(self.obs_repo.get_weather_observations())
        if df.empty or "temperature" not in df.columns:
            return {
                "total_observations": 0,
                "avg_temperature": 0.0,
                "avg_humidity": 0.0,
                "total_rainfall_mm": 0.0,
                "max_temp": 0.0,
                "min_temp": 0.0,
            }

        return {
            "total_observations": len(df),
            "avg_temperature": round(float(df["temperature"].mean()), 1),
            "avg_humidity": round(float(df["humidity"].mean()), 1) if "humidity" in df.columns else 0.0,
            "total_rainfall_mm": round(float(df["rainfall_mm"].sum()), 1) if "rainfall_mm" in df.columns else 0.0,
            "max_temp": round(float(df["temperature"].max()), 1),
            "min_temp": round(float(df["temperature"].min()), 1),
        }

    def get_district_weather_comparison(self) -> pd.DataFrame:
        """Returns mean weather parameters aggregated by district."""
        df = self._normalize_weather_df(self.obs_repo.get_weather_observations())
        if df.empty or "district" not in df.columns or "temperature" not in df.columns:
            return pd.DataFrame()

        agg_dict = {"avg_temp": ("temperature", "mean")}
        if "humidity" in df.columns:
            agg_dict["avg_humidity"] = ("humidity", "mean")
        if "rainfall_mm" in df.columns:
            agg_dict["total_rain"] = ("rainfall_mm", "sum")
        if "wind_speed_kmh" in df.columns:
            agg_dict["avg_wind"] = ("wind_speed_kmh", "mean")

        grouped = df.groupby("district").agg(**agg_dict).reset_index().round(1)
        return grouped
