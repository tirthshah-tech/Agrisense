
import pandas as pd
import numpy as np
from typing import Dict, Any

from repositories.soil_repository import SoilRepository


class SoilAnalytics:
    """Statistical analytics for soil fertility, correlations, and soil comparisons."""

    def __init__(self):
        self.soil_repo = SoilRepository()

    def _get_soil_records(self) -> pd.DataFrame:
        """Retrieve soil records safely from the repository."""
        df = self.soil_repo.get_all_soil_records()

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        return df

    def get_soil_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate Pearson correlations between available numeric soil
        parameters. Returns an empty DataFrame when data is insufficient.
        """
        df = self._get_soil_records()

        if df.empty:
            return pd.DataFrame()

        candidate_columns = [
            "ph",
            "nitrogen",
            "phosphorus",
            "potassium",
            "moisture",
            "soil_moisture",
            "moisture_pct",
            "organic_carbon",
            "electrical_conductivity",
        ]

        num_cols = [
            col for col in candidate_columns
            if col in df.columns
        ]

        # Avoid counting multiple names for the same measurement.
        moisture_names = [
            col for col in ["moisture", "soil_moisture", "moisture_pct"]
            if col in num_cols
        ]
        if len(moisture_names) > 1:
            num_cols = [
                col for col in num_cols if col not in moisture_names
            ] + [moisture_names[0]]

        if len(num_cols) < 2:
            return pd.DataFrame()

        clean_subset = df[num_cols].apply(
            pd.to_numeric, errors="coerce"
        ).dropna()

        if len(clean_subset) < 2:
            return pd.DataFrame()

        return clean_subset.corr().round(2)

    def get_soil_type_comparisons(self) -> pd.DataFrame:
        """
        Summarize soil records by soil type, including sample count
        and average moisture when a supported moisture column exists.
        """
        df = self._get_soil_records()

        if df.empty or "soil_type" not in df.columns:
            return pd.DataFrame(
                columns=["soil_type", "sample_count", "avg_moisture"]
            )

        # Detect the moisture field actually present in the repository data.
        moisture_candidates = [
            "moisture",
            "soil_moisture",
            "moisture_pct",
            "moisture_percent",
            "moisture_level",
        ]

        moisture_col = next(
            (col for col in moisture_candidates if col in df.columns),
            None,
        )

        aggregations = {
            "sample_count": (
                "soil_record_id"
                if "soil_record_id" in df.columns
                else "soil_type",
                "count",
            )
        }

        if moisture_col is not None:
            df[moisture_col] = pd.to_numeric(
                df[moisture_col], errors="coerce"
            )
            aggregations["avg_moisture"] = (moisture_col, "mean")

        result = (
            df.groupby("soil_type", dropna=False)
            .agg(**aggregations)
            .reset_index()
        )

        numeric_columns = result.select_dtypes(
            include="number"
        ).columns

        result[numeric_columns] = result[numeric_columns].round(2)

        return result
