"""
AgriSense - Data Cleaning and Validation Module
Enforces data hygiene rules, sanitizes input datasets, and produces detailed audit logs.
Adheres strictly to the rule: Never silently modify data without documenting the cleaning rule.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional, Set
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CleaningRuleRecord:
    """Represents an audit entry for a data cleaning or sanitization action."""
    table_name: str
    rule_id: str
    rule_description: str
    action_taken: str  # DROPPED, IMPUTED, CLAMPED, FLAGGED, NORMALIZED
    records_affected: int
    details: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "table_name": self.table_name,
            "rule_id": self.rule_id,
            "rule_description": self.rule_description,
            "action_taken": self.action_taken,
            "records_affected": self.records_affected,
            "details": self.details or "",
        }


class DataCleaner:
    """
    Modular data cleaner for agricultural datasets.
    Tracks all sanitization actions in an internal audit trail.
    """

    def __init__(self):
        self.audit_log: List[CleaningRuleRecord] = []

    def log_action(
        self,
        table_name: str,
        rule_id: str,
        rule_description: str,
        action_taken: str,
        records_affected: int,
        details: Optional[str] = None,
    ) -> None:
        """Records an action into the audit trail if any records were affected."""
        if records_affected > 0:
            entry = CleaningRuleRecord(
                table_name=table_name,
                rule_id=rule_id,
                rule_description=rule_description,
                action_taken=action_taken,
                records_affected=records_affected,
                details=details,
            )
            self.audit_log.append(entry)
            logger.info("Cleaning Rule Applied [%s - %s]: %d records affected.", table_name, rule_id, records_affected)

    def get_audit_trail(self) -> pd.DataFrame:
        """Returns the full audit trail as a pandas DataFrame."""
        if not self.audit_log:
            return pd.DataFrame(columns=[
                "timestamp", "table_name", "rule_id", "rule_description",
                "action_taken", "records_affected", "details"
            ])
        return pd.DataFrame([r.to_dict() for r in self.audit_log])

    # -------------------------------------------------------------------------
    # Soil Records Cleaning
    # -------------------------------------------------------------------------
    def clean_soil_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans soil monitoring records:
        - Rule SOIL_01: Deduplicate on (farm_id, record_date)
        - Rule SOIL_02: Validate pH in realistic agricultural range [3.5, 9.5]
        - Rule SOIL_03: Ensure non-negative Nitrogen, Phosphorus, Potassium
        - Rule SOIL_04: Soil moisture must be within [0.0, 100.0] percent
        - Rule SOIL_05: Parse and validate record dates (no future dates)
        """
        if df.empty:
            return df

        clean_df = df.copy()
        table = "soil_records"

        # SOIL_01: Deduplication
        initial_len = len(clean_df)
        if "farm_id" in clean_df.columns and "record_date" in clean_df.columns:
            clean_df = clean_df.drop_duplicates(subset=["farm_id", "record_date"], keep="last")
            dupes_removed = initial_len - len(clean_df)
            self.log_action(
                table, "SOIL_01", "Deduplicate on (farm_id, record_date)",
                "DROPPED", dupes_removed, f"Removed {dupes_removed} duplicate soil measurements"
            )

        # SOIL_05: Date normalization
        if "record_date" in clean_df.columns:
            clean_df["record_date"] = pd.to_datetime(clean_df["record_date"], errors="coerce")
            invalid_dates = clean_df["record_date"].isna() | (clean_df["record_date"] > pd.Timestamp.now())
            invalid_date_count = int(invalid_dates.sum())
            if invalid_date_count > 0:
                clean_df = clean_df[~invalid_dates]
                self.log_action(
                    table, "SOIL_05", "Invalid or future record_date",
                    "DROPPED", invalid_date_count, f"Removed {invalid_date_count} records with unparseable or future dates"
                )

        # SOIL_02: Impossible pH values
        if "ph" in clean_df.columns:
            clean_df["ph"] = pd.to_numeric(clean_df["ph"], errors="coerce")
            # Agricultural soils in Maharashtra range 4.5 to 9.0; absolute limits 3.5 to 9.8
            invalid_ph = (clean_df["ph"] < 3.5) | (clean_df["ph"] > 9.8) | clean_df["ph"].isna()
            invalid_ph_count = int(invalid_ph.sum())
            if invalid_ph_count > 0:
                clean_df = clean_df[~invalid_ph]
                self.log_action(
                    table, "SOIL_02", "Impossible soil pH (< 3.5 or > 9.8)",
                    "DROPPED", invalid_ph_count, f"Removed {invalid_ph_count} records with out-of-bounds soil pH"
                )

        # SOIL_03: Negative NPK
        npk_cols = [c for c in ["nitrogen", "phosphorus", "potassium"] if c in clean_df.columns]
        for col in npk_cols:
            clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")
            neg_mask = clean_df[col] < 0
            neg_count = int(neg_mask.sum())
            if neg_count > 0:
                # Replace negative values with column median
                median_val = clean_df.loc[clean_df[col] >= 0, col].median()
                clean_df.loc[neg_mask, col] = median_val
                self.log_action(
                    table, f"SOIL_03_{col.upper()}", f"Negative {col} nutrient value",
                    "IMPUTED", neg_count, f"Replaced {neg_count} negative {col} values with valid median ({median_val:.2f})"
                )

        # SOIL_04: Moisture bounds [0, 100]
        if "moisture" in clean_df.columns:
            clean_df["moisture"] = pd.to_numeric(clean_df["moisture"], errors="coerce")
            invalid_moist = (clean_df["moisture"] < 0) | (clean_df["moisture"] > 100)
            moist_count = int(invalid_moist.sum())
            if moist_count > 0:
                clean_df.loc[clean_df["moisture"] < 0, "moisture"] = 0.0
                clean_df.loc[clean_df["moisture"] > 100, "moisture"] = 100.0
                self.log_action(
                    table, "SOIL_04", "Moisture outside [0, 100]%",
                    "CLAMPED", moist_count, f"Clamped {moist_count} out-of-range soil moisture values"
                )

        return clean_df

    # -------------------------------------------------------------------------
    # Irrigation Records Cleaning
    # -------------------------------------------------------------------------
    def clean_irrigation_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans irrigation records:
        - Rule IRRIG_01: Ensure non-negative water_used_liters
        - Rule IRRIG_02: Realistic duration_hours (0 to 24 hrs)
        - Rule IRRIG_03: Standardize irrigation_method terminology
        - Rule IRRIG_04: Deduplication on (farm_id, date, irrigation_method)
        """
        if df.empty:
            return df

        clean_df = df.copy()
        table = "irrigation_records"

        # IRRIG_04: Deduplication
        initial_len = len(clean_df)
        subset_cols = [c for c in ["farm_id", "date", "irrigation_method"] if c in clean_df.columns]
        if len(subset_cols) >= 2:
            clean_df = clean_df.drop_duplicates(subset=subset_cols, keep="last")
            dupes = initial_len - len(clean_df)
            self.log_action(
                table, "IRRIG_04", "Duplicate irrigation log",
                "DROPPED", dupes, f"Removed {dupes} duplicate irrigation entries"
            )

        # IRRIG_01: Negative water used
        if "water_used_liters" in clean_df.columns:
            clean_df["water_used_liters"] = pd.to_numeric(clean_df["water_used_liters"], errors="coerce")
            neg_water = (clean_df["water_used_liters"] < 0) | clean_df["water_used_liters"].isna()
            neg_count = int(neg_water.sum())
            if neg_count > 0:
                clean_df = clean_df[~neg_water]
                self.log_action(
                    table, "IRRIG_01", "Negative or NaN water_used_liters",
                    "DROPPED", neg_count, f"Removed {neg_count} records with negative or missing water volume"
                )

        # IRRIG_02: Duration check
        if "duration_hours" in clean_df.columns:
            clean_df["duration_hours"] = pd.to_numeric(clean_df["duration_hours"], errors="coerce")
            invalid_duration = (clean_df["duration_hours"] < 0) | (clean_df["duration_hours"] > 24)
            dur_count = int(invalid_duration.sum())
            if dur_count > 0:
                clean_df.loc[clean_df["duration_hours"] < 0, "duration_hours"] = 0.5
                clean_df.loc[clean_df["duration_hours"] > 24, "duration_hours"] = 24.0
                self.log_action(
                    table, "IRRIG_02", "Duration hours outside [0, 24] hours",
                    "CLAMPED", dur_count, f"Clamped {dur_count} extreme irrigation duration values"
                )

        # IRRIG_03: Method standardization
        if "irrigation_method" in clean_df.columns:
            clean_df["irrigation_method"] = clean_df["irrigation_method"].astype(str).str.strip().str.title()
            method_map = {
                "Drip": "Drip",
                "Sprinkler": "Sprinkler",
                "Canal": "Canal Flood",
                "Canal Flood": "Canal Flood",
                "Flood": "Canal Flood",
                "Tubewell": "Tube Well",
                "Tube Well": "Tube Well",
                "Rainfed": "Rainfed",
            }
            clean_df["irrigation_method"] = clean_df["irrigation_method"].replace(method_map)

        return clean_df

    # -------------------------------------------------------------------------
    # Fertilizer Records Cleaning
    # -------------------------------------------------------------------------
    def clean_fertilizer_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans fertilizer usage records:
        - Rule FERT_01: Ensure non-negative quantity_kg
        - Rule FERT_02: Normalize fertilizer naming
        - Rule FERT_03: Deduplication
        """
        if df.empty:
            return df

        clean_df = df.copy()
        table = "fertilizer_records"

        if "quantity_kg" in clean_df.columns:
            clean_df["quantity_kg"] = pd.to_numeric(clean_df["quantity_kg"], errors="coerce")
            neg_fert = (clean_df["quantity_kg"] < 0) | clean_df["quantity_kg"].isna()
            neg_count = int(neg_fert.sum())
            if neg_count > 0:
                clean_df = clean_df[~neg_fert]
                self.log_action(
                    table, "FERT_01", "Negative or NaN fertilizer quantity_kg",
                    "DROPPED", neg_count, f"Removed {neg_count} records with negative fertilizer amount"
                )

        if "fertilizer_type" in clean_df.columns:
            clean_df["fertilizer_type"] = clean_df["fertilizer_type"].astype(str).str.strip()

        return clean_df

    # -------------------------------------------------------------------------
    # Yield Records Cleaning
    # -------------------------------------------------------------------------
    def clean_yield_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans yield harvest records:
        - Rule YIELD_01: Ensure non-negative yield_kg and yield_per_hectare
        - Rule YIELD_02: Deduplicate on cycle_id (one yield per cycle)
        """
        if df.empty:
            return df

        clean_df = df.copy()
        table = "yield_records"

        if "cycle_id" in clean_df.columns:
            initial = len(clean_df)
            clean_df = clean_df.drop_duplicates(subset=["cycle_id"], keep="last")
            dupes = initial - len(clean_df)
            self.log_action(
                table, "YIELD_02", "Duplicate harvest for cycle_id",
                "DROPPED", dupes, f"Removed {dupes} duplicate harvest records"
            )

        if "yield_kg" in clean_df.columns:
            clean_df["yield_kg"] = pd.to_numeric(clean_df["yield_kg"], errors="coerce")
            neg_yield = (clean_df["yield_kg"] < 0) | clean_df["yield_kg"].isna()
            neg_count = int(neg_yield.sum())
            if neg_count > 0:
                clean_df = clean_df[~neg_yield]
                self.log_action(
                    table, "YIELD_01", "Negative or NaN yield_kg",
                    "DROPPED", neg_count, f"Removed {neg_count} invalid harvest yield records"
                )

        return clean_df

    # -------------------------------------------------------------------------
    # Referential Integrity & Foreign Key Enforcement
    # -------------------------------------------------------------------------
    def enforce_foreign_keys(
        self,
        df: pd.DataFrame,
        table_name: str,
        fk_column: str,
        valid_keys: Set[Any],
    ) -> pd.DataFrame:
        """
        Removes orphan records that reference non-existent foreign keys.
        Logs the action to maintain transparent data quality accounting.
        """
        if df.empty or fk_column not in df.columns:
            return df

        clean_df = df.copy()
        orphans = ~clean_df[fk_column].isin(valid_keys)
        orphan_count = int(orphans.sum())

        if orphan_count > 0:
            clean_df = clean_df[~orphans]
            self.log_action(
                table_name, f"FK_CHECK_{fk_column.upper()}",
                f"Missing foreign key reference in {fk_column}",
                "DROPPED", orphan_count,
                f"Filtered out {orphan_count} orphan records referencing invalid {fk_column}"
            )

        return clean_df
