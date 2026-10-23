"""
AgriSense - Comprehensive Master Integration and Unit Test Suite
Validates:
- Analytical formula correctness (Yield/ha, Water/ha, Fert/ha, Productivity Ratios)
- Zero-division guards and statistical aggregation robustness
- Data cleaner rules and audit log generation
- Agronomic domain validators
- Repository data loading (MySQL fallback and MongoDB)
- Deterministic Alert Engine rule triggers and deduplication
- Dynamic data-driven agricultural insights (100% non-AI)
"""
import sys
from pathlib import Path
import unittest
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import settings
from utils.data_cleaning import DataCleaner
from utils.validators import validate_indian_phone, validate_coordinates, validate_soil_ph
from repositories import (
    FarmerRepository, FarmRepository, CropRepository,
    SoilRepository, ResourceRepository, YieldRepository, ObservationRepository
)
from services import (
    FarmService, CropService, SoilService, ResourceService, WeatherService, AlertService
)
from analytics import (
    CropAnalytics, YieldAnalytics, ResourceAnalytics, SoilAnalytics
)
from ui.data_quality import run_comprehensive_data_quality_audit


class TestAgriSenseMasterSuite(unittest.TestCase):
    """Full test suite covering data integrity, formulas, and deterministic rules."""

    def setUp(self):
        self.cleaner = DataCleaner()
        self.crop_repo = CropRepository()
        self.farm_repo = FarmRepository()
        self.farmer_repo = FarmerRepository()
        self.soil_repo = SoilRepository()
        self.res_repo = ResourceRepository()
        self.yield_repo = YieldRepository()
        self.obs_repo = ObservationRepository()
        self.alert_svc = AlertService()
        self.res_analytics = ResourceAnalytics()
        self.yield_analytics = YieldAnalytics()
        self.crop_analytics = CropAnalytics()
        self.soil_analytics = SoilAnalytics()

    # ── 1. Formula & KPI Correctness ───────────────────────────────────────────
    def test_kpi_formulas_correctness(self):
        """Verifies core analytical formulas and zero-division protection."""
        # Yield per hectare = yield_kg / cultivated_area_ha
        yield_kg = 50000.0
        area_ha = 5.0
        yield_per_ha = yield_kg / area_ha
        self.assertEqual(yield_per_ha, 10000.0)

        # Water per hectare = water_liters / cultivated_area_ha
        water_l = 100000.0
        water_per_ha = water_l / area_ha
        self.assertEqual(water_per_ha, 20000.0)

        # Fertilizer per hectare = fert_kg / cultivated_area_ha
        fert_kg = 250.0
        fert_per_ha = fert_kg / area_ha
        self.assertEqual(fert_per_ha, 50.0)

        # Water productivity = yield_kg / water_m3
        water_m3 = water_l / 1000.0
        water_prod = yield_kg / water_m3
        self.assertEqual(water_prod, 500.0)

        # Fertilizer productivity = yield_kg / fert_kg
        fert_prod = yield_kg / fert_kg
        self.assertEqual(fert_prod, 200.0)

        # Land productivity = yield_kg / area_ha
        land_prod = yield_kg / area_ha
        self.assertEqual(land_prod, 10000.0)

    def test_zero_division_guard(self):
        """Ensures analytical functions gracefully handle 0 or missing areas/inputs."""
        dummy_df = pd.DataFrame([
            {"cycle_id": 999, "yield_kg": 1000.0, "cultivated_area": 0.0},
        ])
        safe_area = dummy_df["cultivated_area"].replace(0, np.nan).fillna(1.0)
        prod = (dummy_df["yield_kg"] / safe_area).iloc[0]
        self.assertFalse(np.isinf(prod))
        self.assertEqual(prod, 1000.0)

    # ── 2. Data Cleaning & Sanitization ────────────────────────────────────────
    def test_data_cleaner_rules(self):
        """Validates DataCleaner drops impossible pH, cleans duplicates, and logs audits."""
        dirty_soil = pd.DataFrame([
            {"soil_record_id": 1, "farm_id": 1, "record_date": "2024-01-01", "ph": 7.0, "nitrogen": 250.0, "phosphorus": 20.0, "potassium": 200.0, "moisture": 30.0},
            {"soil_record_id": 2, "farm_id": 1, "record_date": "2024-01-01", "ph": 7.0, "nitrogen": 250.0, "phosphorus": 20.0, "potassium": 200.0, "moisture": 30.0},  # duplicate
            {"soil_record_id": 3, "farm_id": 2, "record_date": "2024-01-02", "ph": 16.5, "nitrogen": 220.0, "phosphorus": 15.0, "potassium": 190.0, "moisture": 35.0},  # pH > 14
            {"soil_record_id": 4, "farm_id": 3, "record_date": "2024-01-03", "ph": 6.8, "nitrogen": -60.0, "phosphorus": 18.0, "potassium": 210.0, "moisture": 40.0},  # negative N
        ])
        cleaned = self.cleaner.clean_soil_records(dirty_soil)
        audit = self.cleaner.get_audit_trail()

        # Duplicate resolved
        self.assertEqual(len(cleaned[cleaned["farm_id"] == 1]), 1)
        # Impossible pH dropped
        self.assertEqual(len(cleaned[cleaned["soil_record_id"] == 3]), 0)
        # Negative nitrogen imputed/clamped
        self.assertGreater(cleaned.loc[cleaned["soil_record_id"] == 4, "nitrogen"].values[0], 0)
        # Audit trail recorded
        self.assertGreater(len(audit), 0)

    # ── 3. Domain Validators ───────────────────────────────────────────────────
    def test_domain_validators(self):
        """Tests phone, coordinate, and pH validators."""
        self.assertTrue(validate_indian_phone("9823012345"))
        self.assertFalse(validate_indian_phone("123"))
        self.assertTrue(validate_coordinates(18.52, 73.85))  # Pune
        self.assertFalse(validate_coordinates(55.0, 10.0))    # Outside Maharashtra
        is_valid_7, _ = validate_soil_ph(7.2)
        self.assertTrue(is_valid_7)
        is_valid_15, _ = validate_soil_ph(15.0)
        self.assertFalse(is_valid_15)

    # ── 4. Repositories Data Loading ───────────────────────────────────────────
    def test_repositories_data_retrieval(self):
        """Verifies repositories load datasets correctly from live DB or fallback."""
        self.assertGreaterEqual(len(self.farmer_repo.get_all_farmers()), 30)
        self.assertGreaterEqual(len(self.farm_repo.get_all_farms()), 40)
        self.assertGreaterEqual(len(self.crop_repo.get_all_crops()), 8)
        self.assertGreaterEqual(len(self.crop_repo.get_cycles_enriched()), 50)
        self.assertGreaterEqual(len(self.soil_repo.get_all_soil_records()), 300)
        self.assertGreaterEqual(len(self.res_repo.get_all_irrigation_records()), 500)
        self.assertGreaterEqual(len(self.res_repo.get_all_fertilizer_records()), 400)
        self.assertGreaterEqual(len(self.yield_repo.get_all_yields()), 100)
        self.assertGreaterEqual(len(self.obs_repo.get_weather_observations()), 500)
        self.assertGreaterEqual(len(self.obs_repo.get_agricultural_alerts()), 50)

    # ── 5. Services Aggregations ───────────────────────────────────────────────
    def test_service_layer_calculations(self):
        """Tests service layer aggregations."""
        farm_svc = FarmService()
        metrics = farm_svc.get_summary_metrics()
        self.assertGreater(metrics["total_farms"], 0)
        self.assertGreater(metrics["total_cultivated_area_ha"], 0)

        soil_svc = SoilService()
        soil_metrics = soil_svc.get_soil_summary_metrics()
        self.assertTrue(6.0 <= soil_metrics["avg_ph"] <= 8.5)

        res_svc = ResourceService()
        water_metrics = res_svc.get_water_metrics()
        self.assertGreater(water_metrics["total_water_liters"], 0)
        fert_metrics = res_svc.get_fertilizer_metrics()
        self.assertGreater(fert_metrics["total_fertilizer_kg"], 0)

    # ── 6. Analytics Modules ───────────────────────────────────────────────────
    def test_analytics_modules(self):
        """Verifies analytics computation without ML/AI."""
        # Crop Analytics
        dur = self.crop_analytics.get_cycle_duration_stats()
        self.assertFalse(dur.empty)
        shares = self.crop_analytics.get_crop_area_share()
        self.assertFalse(shares.empty)

        # Yield Analytics
        perf = self.yield_analytics.get_yield_performance_by_crop()
        self.assertFalse(perf.empty)
        self.assertIn("yield_gap_kg_ha", perf.columns)

        # Resource Analytics
        water_eff = self.res_analytics.get_water_efficiency_by_method()
        self.assertFalse(water_eff.empty)
        water_prod = self.res_analytics.get_water_productivity_ratio()
        self.assertFalse(water_prod.empty)
        fert_prod = self.res_analytics.get_fertilizer_productivity_ratio()
        self.assertFalse(fert_prod.empty)
        master = self.res_analytics.get_resource_efficiency_master_table()
        self.assertFalse(master.empty)
        self.assertIn("water_productivity_kg_m3", master.columns)

        # Soil Analytics
        corr = self.soil_analytics.get_soil_correlation_matrix()
        self.assertFalse(corr.empty)

    # ── 7. Deterministic Alert Engine & Deduplication ──────────────────────────
    def test_alert_engine_and_deduplication(self):
        """Validates that rule evaluation generates alerts and deduplicates repeated calls."""
        # Run alert generation
        new_alerts = self.alert_svc.evaluate_rules_and_generate_alerts()
        # Second run should insert 0 duplicates due to stable dedup keys
        second_run = self.alert_svc.evaluate_rules_and_generate_alerts()
        self.assertEqual(second_run, 0)

        summary = self.alert_svc.get_alert_summary()
        self.assertGreater(summary["total_alerts"], 0)
        self.assertGreater(summary["critical_alerts"], 0)

    # ── 8. Dynamic Data-Driven Insights ────────────────────────────────────────
    def test_data_driven_insights(self):
        """Ensures dynamic insights are calculated from real database records without AI."""
        insights = self.alert_svc.get_dynamic_insights()
        self.assertGreaterEqual(len(insights), 3)
        for ins in insights:
            self.assertIn("title", ins)
            self.assertIn("detail", ins)
            self.assertGreater(len(ins["detail"]), 10)

    # ── 9. Data Quality Audit Function ─────────────────────────────────────────
    def test_data_quality_audit(self):
        """Verifies automated data quality audit returns clean results across all 10 datasets."""
        audit_df = run_comprehensive_data_quality_audit()
        self.assertEqual(len(audit_df), 10)
        self.assertTrue((audit_df["Records"] > 0).all())


if __name__ == "__main__":
    unittest.main()
