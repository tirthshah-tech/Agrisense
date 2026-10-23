"""
AgriSense - Deterministic Rule-Based Alert & Agricultural Insights Service
Monitors agricultural telemetry and production records against deterministic agronomic rules.
Strictly non-AI / non-ML: all alerts and insights are based on configurable thresholds,
statistical aggregations, and historical comparisons.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from repositories.observation_repository import ObservationRepository
from repositories.resource_repository import ResourceRepository
from repositories.soil_repository import SoilRepository
from repositories.yield_repository import YieldRepository
from repositories.crop_repository import CropRepository


# ─── Configurable Agronomic Thresholds ──────────────────────────────────────────
DEFAULT_THRESHOLDS = {
    # Water Rules
    "water_single_event_warning_l": 15000.0,
    "water_single_event_critical_l": 25000.0,
    "water_per_ha_critical_l": 12000000.0,  # 12,000 m3/ha

    # Fertilizer Rules
    "fert_single_event_warning_kg": 220.0,
    "fert_single_event_critical_kg": 350.0,
    "fert_per_ha_critical_kg": 400.0,

    # Soil Rules
    "soil_moisture_critical_pct": 20.0,
    "soil_moisture_warning_pct": 25.0,
    "soil_ph_acidic_min": 6.0,
    "soil_ph_alkaline_max": 8.0,
    "soil_ph_severe_acidic": 5.2,
    "soil_ph_severe_alkaline": 8.7,

    # Yield Rules
    "yield_benchmark_warning_pct": 75.0,   # < 75% standard
    "yield_benchmark_critical_pct": 50.0,  # < 50% standard

    # Weather Over-irrigation Rule
    "over_irrigation_rain_threshold_mm": 25.0,
}


class AlertService:
    """Service layer for agricultural alert processing, rule evaluation, and insights."""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.obs_repo = ObservationRepository()
        self.resource_repo = ResourceRepository()
        self.soil_repo = SoilRepository()
        self.yield_repo = YieldRepository()
        self.crop_repo = CropRepository()
        self.thresholds = thresholds or DEFAULT_THRESHOLDS

    def get_alert_summary(self) -> Dict[str, Any]:
        """Calculates alert statistics by status and severity."""
        df = self.obs_repo.get_agricultural_alerts()
        if df.empty:
            return {
                "total_alerts": 0,
                "open_alerts": 0,
                "critical_alerts": 0,
                "warning_alerts": 0,
                "info_alerts": 0,
                "resolved_alerts": 0,
            }

        total = len(df)
        open_count = len(df[df["status"] == "Open"]) if "status" in df.columns else 0
        critical = len(df[df["severity"] == "Critical"]) if "severity" in df.columns else 0
        warning = len(df[df["severity"] == "Warning"]) if "severity" in df.columns else 0
        info = len(df[df["severity"] == "Info"]) if "severity" in df.columns else 0
        resolved = len(df[df["status"] == "Resolved"]) if "status" in df.columns else 0

        return {
            "total_alerts": total,
            "open_alerts": open_count,
            "critical_alerts": critical,
            "warning_alerts": warning,
            "info_alerts": info,
            "resolved_alerts": resolved,
        }

    def get_alerts_by_type(self) -> pd.DataFrame:
        """Returns distribution of alerts by alert rule type."""
        df = self.obs_repo.get_agricultural_alerts()
        if df.empty or "alert_type" not in df.columns:
            return pd.DataFrame()

        return df["alert_type"].value_counts().reset_index().rename(columns={"count": "alert_count"})

    def evaluate_rules_and_generate_alerts(self) -> int:
        """
        Executes deterministic rules against live database/fallback data.
        Generates alerts with severity and deduplication keys, upserting them into MongoDB.
        Returns count of new alerts generated.
        """
        new_alerts: List[Dict[str, Any]] = []
        now_str = datetime.now(timezone.utc).isoformat()

        # 1. Soil Health Evaluation
        soil_df = self.soil_repo.get_all_soil_records()
        if not soil_df.empty:
            moisture_col = "moisture_percentage" if "moisture_percentage" in soil_df.columns else "moisture"
            for _, row in soil_df.iterrows():
                farm_id = int(row["farm_id"])
                rec_date = str(row.get("record_date", "2024-01-01"))

                # Moisture check
                if moisture_col in row and pd.notnull(row[moisture_col]):
                    m = float(row[moisture_col])
                    if m < self.thresholds["soil_moisture_critical_pct"]:
                        new_alerts.append({
                            "farm_id": farm_id,
                            "alert_type": "Soil Moisture Deficit",
                            "severity": "Critical",
                            "trigger_rule": f"Moisture < {self.thresholds['soil_moisture_critical_pct']}%",
                            "metric_value": f"{m:.1f}%",
                            "threshold_value": f"{self.thresholds['soil_moisture_critical_pct']}%",
                            "status": "Open",
                            "timestamp": rec_date,
                            "dedup_key": f"{farm_id}_soil_moist_{rec_date}",
                        })
                    elif m < self.thresholds["soil_moisture_warning_pct"]:
                        new_alerts.append({
                            "farm_id": farm_id,
                            "alert_type": "Low Soil Moisture",
                            "severity": "Warning",
                            "trigger_rule": f"Moisture < {self.thresholds['soil_moisture_warning_pct']}%",
                            "metric_value": f"{m:.1f}%",
                            "threshold_value": f"{self.thresholds['soil_moisture_warning_pct']}%",
                            "status": "Open",
                            "timestamp": rec_date,
                            "dedup_key": f"{farm_id}_soil_moist_warn_{rec_date}",
                        })

                # pH check
                if "ph" in row and pd.notnull(row["ph"]):
                    ph = float(row["ph"])
                    if ph < self.thresholds["soil_ph_acidic_min"]:
                        sev = "Critical" if ph < self.thresholds["soil_ph_severe_acidic"] else "Warning"
                        new_alerts.append({
                            "farm_id": farm_id,
                            "alert_type": "Soil Acidity",
                            "severity": sev,
                            "trigger_rule": f"pH < {self.thresholds['soil_ph_acidic_min']}",
                            "metric_value": f"pH {ph:.2f}",
                            "threshold_value": f"Min {self.thresholds['soil_ph_acidic_min']}",
                            "status": "Open",
                            "timestamp": rec_date,
                            "dedup_key": f"{farm_id}_soil_ph_acid_{rec_date}",
                        })
                    elif ph > self.thresholds["soil_ph_alkaline_max"]:
                        sev = "Critical" if ph > self.thresholds["soil_ph_severe_alkaline"] else "Warning"
                        new_alerts.append({
                            "farm_id": farm_id,
                            "alert_type": "Soil Alkalinity",
                            "severity": sev,
                            "trigger_rule": f"pH > {self.thresholds['soil_ph_alkaline_max']}",
                            "metric_value": f"pH {ph:.2f}",
                            "threshold_value": f"Max {self.thresholds['soil_ph_alkaline_max']}",
                            "status": "Open",
                            "timestamp": rec_date,
                            "dedup_key": f"{farm_id}_soil_ph_alk_{rec_date}",
                        })

        # 2. Water / Irrigation Evaluation
        irrig_df = self.resource_repo.get_all_irrigation_records()
        if not irrig_df.empty:
            for _, row in irrig_df.iterrows():
                farm_id = int(row["farm_id"])
                irrig_id = row.get("irrigation_id", 0)
                dt = str(row.get("date", "2024-01-01"))
                vol = float(row.get("water_used_liters", 0.0))

                if vol > self.thresholds["water_single_event_critical_l"]:
                    new_alerts.append({
                        "farm_id": farm_id,
                        "alert_type": "Excessive Water Application",
                        "severity": "Critical",
                        "trigger_rule": f"Water > {self.thresholds['water_single_event_critical_l']:,.0f} L",
                        "metric_value": f"{vol:,.0f} L",
                        "threshold_value": f"{self.thresholds['water_single_event_critical_l']:,.0f} L",
                        "status": "Open",
                        "timestamp": dt,
                        "dedup_key": f"{farm_id}_irrig_crit_{irrig_id}",
                    })
                elif vol > self.thresholds["water_single_event_warning_l"]:
                    new_alerts.append({
                        "farm_id": farm_id,
                        "alert_type": "High Irrigation Consumption",
                        "severity": "Warning",
                        "trigger_rule": f"Water > {self.thresholds['water_single_event_warning_l']:,.0f} L",
                        "metric_value": f"{vol:,.0f} L",
                        "threshold_value": f"{self.thresholds['water_single_event_warning_l']:,.0f} L",
                        "status": "Open",
                        "timestamp": dt,
                        "dedup_key": f"{farm_id}_irrig_warn_{irrig_id}",
                    })

        # 3. Fertilizer Evaluation
        fert_df = self.resource_repo.get_all_fertilizer_records()
        if not fert_df.empty:
            for _, row in fert_df.iterrows():
                farm_id = int(row["farm_id"])
                fert_id = row.get("fertilizer_id", 0)
                dt = str(row.get("date", "2024-01-01"))
                qty = float(row.get("quantity_kg", 0.0))

                if qty > self.thresholds["fert_single_event_critical_kg"]:
                    new_alerts.append({
                        "farm_id": farm_id,
                        "alert_type": "Excessive Agrochemical Application",
                        "severity": "Critical",
                        "trigger_rule": f"Dosage > {self.thresholds['fert_single_event_critical_kg']} kg",
                        "metric_value": f"{qty:.1f} kg",
                        "threshold_value": f"{self.thresholds['fert_single_event_critical_kg']} kg",
                        "status": "Open",
                        "timestamp": dt,
                        "dedup_key": f"{farm_id}_fert_crit_{fert_id}",
                    })
                elif qty > self.thresholds["fert_single_event_warning_kg"]:
                    new_alerts.append({
                        "farm_id": farm_id,
                        "alert_type": "High Fertilizer Dosage",
                        "severity": "Warning",
                        "trigger_rule": f"Dosage > {self.thresholds['fert_single_event_warning_kg']} kg",
                        "metric_value": f"{qty:.1f} kg",
                        "threshold_value": f"{self.thresholds['fert_single_event_warning_kg']} kg",
                        "status": "Open",
                        "timestamp": dt,
                        "dedup_key": f"{farm_id}_fert_warn_{fert_id}",
                    })

        # 4. Harvest Yield Gap Evaluation
        yields_df = self.yield_repo.get_all_yields()
        crops_df = self.crop_repo.get_all_crops()
        cycles_df = self.crop_repo.get_cycles_enriched()

        if not yields_df.empty and not crops_df.empty and not cycles_df.empty:
            std_map = dict(zip(crops_df["crop_name"], crops_df["standard_yield_kg_per_ha"]))
            joined = yields_df.merge(cycles_df[["cycle_id", "crop_name", "farm_id"]], on="cycle_id", how="left")
            for _, row in joined.iterrows():
                c_name = row.get("crop_name")
                std_yield = std_map.get(c_name)
                act_yield = row.get("yield_per_hectare")
                farm_id = row.get("farm_id")
                y_id = row.get("yield_id", 0)
                dt = str(row.get("harvest_date", "2024-01-01"))

                if std_yield and act_yield and std_yield > 0 and pd.notnull(farm_id):
                    ratio = (float(act_yield) / float(std_yield)) * 100.0
                    if ratio < self.thresholds["yield_benchmark_critical_pct"]:
                        new_alerts.append({
                            "farm_id": int(farm_id),
                            "alert_type": "Critical Yield Deficit",
                            "severity": "Critical",
                            "trigger_rule": f"Yield < {self.thresholds['yield_benchmark_critical_pct']}% of benchmark",
                            "metric_value": f"{act_yield:,.0f} kg/ha ({ratio:.1f}%)",
                            "threshold_value": f"{std_yield:,.0f} kg/ha",
                            "status": "Open",
                            "timestamp": dt,
                            "dedup_key": f"{farm_id}_yield_crit_{y_id}",
                        })
                    elif ratio < self.thresholds["yield_benchmark_warning_pct"]:
                        new_alerts.append({
                            "farm_id": int(farm_id),
                            "alert_type": "Yield Benchmark Gap",
                            "severity": "Warning",
                            "trigger_rule": f"Yield < {self.thresholds['yield_benchmark_warning_pct']}% of benchmark",
                            "metric_value": f"{act_yield:,.0f} kg/ha ({ratio:.1f}%)",
                            "threshold_value": f"{std_yield:,.0f} kg/ha",
                            "status": "Open",
                            "timestamp": dt,
                            "dedup_key": f"{farm_id}_yield_warn_{y_id}",
                        })

        # Save to repository with deduplication
        inserted = self.obs_repo.save_agricultural_alerts(new_alerts)
        return inserted

    def get_dynamic_insights(self) -> List[Dict[str, str]]:
        """
        Calculates 100% deterministic, explainable data insights grounded in real database records.
        No artificial intelligence or machine learning is utilized.
        """
        insights = []

        # 1. Top Yielding Crop
        yields_df = self.yield_repo.get_all_yields()
        cycles_df = self.crop_repo.get_cycles_enriched()
        if not yields_df.empty and not cycles_df.empty:
            merged = yields_df.merge(cycles_df[["cycle_id", "crop_name"]], on="cycle_id", how="left")
            if "crop_name" in merged.columns and "yield_per_hectare" in merged.columns:
                crop_yields = merged.groupby("crop_name")["yield_per_hectare"].mean().reset_index()
                if not crop_yields.empty:
                    top_crop = crop_yields.sort_values("yield_per_hectare", ascending=False).iloc[0]
                    insights.append({
                        "icon": "🏆",
                        "title": "Highest Yielding Variety",
                        "detail": f"{top_crop['crop_name']} achieved the highest average yield of {top_crop['yield_per_hectare']:,.0f} kg/ha across harvested cycles.",
                    })

        # 2. Irrigation Method Efficiency Disparity (SDG 12)
        irrig_df = self.resource_repo.get_all_irrigation_records()
        if not irrig_df.empty and "irrigation_method" in irrig_df.columns:
            method_means = irrig_df.groupby("irrigation_method")["water_used_liters"].mean()
            if "Drip" in method_means.index and "Canal Flood" in method_means.index:
                drip_val = method_means["Drip"]
                flood_val = method_means["Canal Flood"]
                if flood_val > 0:
                    pct_saving = ((flood_val - drip_val) / flood_val) * 100.0
                    insights.append({
                        "icon": "💧",
                        "title": "Irrigation Water Stewardship",
                        "detail": f"Drip irrigation consumed an average of {drip_val:,.0f} L/event, delivering {pct_saving:.1f}% water savings compared to traditional Canal Flood ({flood_val:,.0f} L/event).",
                    })

        # 3. Soil Health Summary (SDG 2)
        soil_df = self.soil_repo.get_all_soil_records()
        if not soil_df.empty and "nitrogen" in soil_df.columns:
            low_n_count = (soil_df["nitrogen"] < 280).sum()
            total_samples = len(soil_df)
            pct_low = (low_n_count / total_samples) * 100.0
            avg_ph = soil_df["ph"].mean()
            insights.append({
                "icon": "🧪",
                "title": "Soil Fertility Index",
                "detail": f"Average soil pH across parcels is {avg_ph:.2f}. {pct_low:.1f}% of surveyed soils exhibit Nitrogen deficits (< 280 kg/ha), requiring targeted basal nutrition.",
            })

        # 4. Agrochemical Consumption Intensity
        fert_df = self.resource_repo.get_all_fertilizer_records()
        if not fert_df.empty and "fertilizer_type" in fert_df.columns:
            top_fert = fert_df.groupby("fertilizer_type")["quantity_kg"].sum().sort_values(ascending=False).reset_index().iloc[0]
            insights.append({
                "icon": "🌿",
                "title": "Primary Nutrient Input",
                "detail": f"{top_fert['fertilizer_type']} accounts for the largest agrochemical volume at {top_fert['quantity_kg']:,.0f} kg applied across crop cycles.",
            })

        # 5. Active Alert Pressure
        alert_summary = self.get_alert_summary()
        if alert_summary["total_alerts"] > 0:
            crit = alert_summary["critical_alerts"]
            open_a = alert_summary["open_alerts"]
            insights.append({
                "icon": "🚨",
                "title": "Field Alert Status",
                "detail": f"{open_a} open monitoring alerts detected across farms ({crit} critical severity items requiring field intervention).",
            })

        return insights
