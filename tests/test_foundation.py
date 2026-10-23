"""
AgriSense - Comprehensive Foundation Test Suite
Validates configuration, models, data cleaner, repositories, services, and analytics.
"""
import sys
from pathlib import Path

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
import pandas as pd

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


class TestAgriSenseFoundation(unittest.TestCase):

    def test_settings_paths(self):
        """Verify directories exist and settings initialize."""
        self.assertTrue(settings.paths.raw_data_dir.exists())
        self.assertTrue(settings.paths.assets_dir.exists())

    def test_data_cleaner_rules(self):
        """Verify that the DataCleaner audits and enforces cleaning rules."""
        cleaner = DataCleaner()
        
        # Test soil pH outlier
        dirty_soil = pd.DataFrame([
            {"soil_record_id": 1, "farm_id": 1, "record_date": "2024-01-01", "ph": 7.0, "nitrogen": 250.0, "phosphorus": 20.0, "potassium": 200.0, "moisture": 30.0},
            {"soil_record_id": 2, "farm_id": 1, "record_date": "2024-01-01", "ph": 7.0, "nitrogen": 250.0, "phosphorus": 20.0, "potassium": 200.0, "moisture": 30.0}, # duplicate
            {"soil_record_id": 3, "farm_id": 2, "record_date": "2024-01-02", "ph": 15.5, "nitrogen": 220.0, "phosphorus": 15.0, "potassium": 190.0, "moisture": 35.0}, # invalid pH
            {"soil_record_id": 4, "farm_id": 3, "record_date": "2024-01-03", "ph": 6.8, "nitrogen": -50.0, "phosphorus": 18.0, "potassium": 210.0, "moisture": 40.0}, # negative N
        ])
        
        clean_soil = cleaner.clean_soil_records(dirty_soil)
        audit = cleaner.get_audit_trail()
        
        # Check that duplicate was removed (only 1 record left for farm 1)
        farm_1_records = clean_soil[clean_soil["farm_id"] == 1]
        self.assertEqual(len(farm_1_records), 1)
        # Check that impossible pH (15.5) was dropped
        self.assertEqual(len(clean_soil[clean_soil["soil_record_id"] == 3]), 0)
        # Check that negative nitrogen was imputed
        cleaned_n = clean_soil.loc[clean_soil["soil_record_id"] == 4, "nitrogen"].values[0]
        self.assertGreater(cleaned_n, 0)
        # Verify audit records were generated
        self.assertGreater(len(audit), 0)

    def test_validators(self):
        """Verify agronomic and domain validators."""
        self.assertTrue(validate_indian_phone("9823012345"))
        self.assertFalse(validate_indian_phone("12345"))
        self.assertTrue(validate_coordinates(18.52, 73.85))
        self.assertFalse(validate_coordinates(50.0, 10.0))  # Not in Maharashtra

    def test_repositories_data_loading(self):
        """Verify that repositories correctly query fallback CSV/JSON archives."""
        farmers = FarmerRepository().get_all_farmers()
        self.assertGreaterEqual(len(farmers), 30)

        farms = FarmRepository().get_all_farms()
        self.assertGreaterEqual(len(farms), 40)

        crops = CropRepository().get_all_crops()
        self.assertGreaterEqual(len(crops), 8)

        soil = SoilRepository().get_all_soil_records()
        self.assertGreaterEqual(len(soil), 300)

        irrig = ResourceRepository().get_all_irrigation_records()
        self.assertGreaterEqual(len(irrig), 500)

        fert = ResourceRepository().get_all_fertilizer_records()
        self.assertGreaterEqual(len(fert), 400)

        yields = YieldRepository().get_all_yields()
        self.assertGreaterEqual(len(yields), 100)

        weather = ObservationRepository().get_weather_observations()
        self.assertGreaterEqual(len(weather), 500)

    def test_services_calculations(self):
        """Verify service layer aggregations."""
        farm_svc = FarmService()
        metrics = farm_svc.get_summary_metrics()
        self.assertGreater(metrics["total_farmers"], 0)
        self.assertGreater(metrics["total_cultivated_area_ha"], 0)

        soil_svc = SoilService()
        soil_metrics = soil_svc.get_soil_summary_metrics()
        self.assertTrue(6.0 <= soil_metrics["avg_ph"] <= 8.5)

        res_svc = ResourceService()
        water_metrics = res_svc.get_water_metrics()
        self.assertGreater(water_metrics["total_water_liters"], 0)

    def test_analytics_layer(self):
        """Verify analytical statistical outputs without ML."""
        yield_analytics = YieldAnalytics()
        perf = yield_analytics.get_yield_performance_by_crop()
        self.assertFalse(perf.empty)
        self.assertIn("yield_gap_kg_ha", perf.columns)

        res_analytics = ResourceAnalytics()
        water_eff = res_analytics.get_water_efficiency_by_method()
        self.assertFalse(water_eff.empty)

        soil_analytics = SoilAnalytics()
        corr = soil_analytics.get_soil_correlation_matrix()
        self.assertFalse(corr.empty)


if __name__ == "__main__":
    unittest.main()
