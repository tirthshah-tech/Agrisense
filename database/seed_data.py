"""
AgriSense - Comprehensive Synthetic Data Generator & Database Seeder (Prompt 2)
Generates realistic agricultural analytics datasets focused on Maharashtra, India.
Features modular generator functions, deterministic domain relationships, and reproducible random state.
Outputs clean CSV/JSON archives into data/raw/ and seeds live MySQL & MongoDB databases.

NOTE: All generated data is SYNTHETIC and designed specifically for demonstration,
academic evaluation, and statistical analytics benchmarking without AI/ML.
"""
import os
import sys
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np

from config.settings import settings

# Fixed seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

DISTRICTS_MAHARASHTRA = [
    {"district": "Pune", "lat": 18.5204, "lon": 73.8567, "villages": ["Baramati", "Shirur", "Indapur", "Khed", "Junnar", "Daund"]},
    {"district": "Nashik", "lat": 19.9975, "lon": 73.7898, "villages": ["Niphad", "Dindori", "Yeola", "Sinnar", "Kalwan", "Malegaon"]},
    {"district": "Ahmednagar", "lat": 19.0952, "lon": 74.7496, "villages": ["Rahata", "Sangamner", "Kopargaon", "Shrirampur", "Newasa", "Parner"]},
    {"district": "Satara", "lat": 17.6805, "lon": 73.9997, "villages": ["Karad", "Phaltan", "Wai", "Koregaon", "Khandala", "Patan"]},
    {"district": "Solapur", "lat": 17.6599, "lon": 75.9064, "villages": ["Pandharpur", "Barshi", "Malshiras", "Karmala", "Madha", "Mohol"]},
    {"district": "Kolhapur", "lat": 16.7050, "lon": 74.2433, "villages": ["Shirol", "Hatkanangle", "Karveer", "Radhanagari", "Panhala", "Gadhinglaj"]},
    {"district": "Nagpur", "lat": 21.1458, "lon": 79.0882, "villages": ["Katol", "Kalmeshwar", "Ramtek", "Umred", "Saoner", "Hingna"]},
    {"district": "Jalgaon", "lat": 21.0077, "lon": 75.5626, "villages": ["Raver", "Yawal", "Chopda", "Bhusawal", "Jamner", "Pachora"]},
]

FIRST_NAMES = [
    "Ramesh", "Suresh", "Rajesh", "Anand", "Sunil", "Nitin", "Santosh", "Sachin",
    "Ganesh", "Mahesh", "Vijay", "Pravin", "Deepak", "Vikram", "Amol", "Dattatray",
    "Vikas", "Sanjay", "Balasaheb", "Ashok", "Kishor", "Arun", "Pradip", "Tukaram",
    "Pandurang", "Eknath", "Namdeo", "Baban", "Shankar", "Vishnu", "Umesh", "Rohit",
    "Ajay", "Sandip", "Kailas", "Tanaji", "Sudhir", "Bhausaheb", "Devidas", "Chandrakant"
]

LAST_NAMES = [
    "Patil", "Shinde", "Deshmukh", "Jadhav", "Chavan", "Kulkarni", "Pawar", "More",
    "Kadam", "Gaikwad", "Bhosale", "Thorat", "Jagtap", "Sawant", "Kale", "Ghadge",
    "Salunkhe", "Wagh", "Mane", "Shirke", "Kharat", "Bankar", "Auti", "Tambe"
]

# 12 Maharashtra Crops with agronomic requirements
CROPS_CATALOG = [
    {"name": "Sugarcane", "category": "Cash Crop", "season": "Perennial", "soil": "Deep Black", "days": 365, "water_mm": 1800.0, "std_yield": 85000.0},
    {"name": "Cotton", "category": "Cash Crop", "season": "Kharif", "soil": "Medium Black", "days": 165, "water_mm": 700.0, "std_yield": 2200.0},
    {"name": "Soybean", "category": "Oilseed", "season": "Kharif", "soil": "Medium Black", "days": 95, "water_mm": 500.0, "std_yield": 2500.0},
    {"name": "Onion", "category": "Vegetable", "season": "Rabi", "soil": "Red Sandy Loam", "days": 115, "water_mm": 450.0, "std_yield": 22000.0},
    {"name": "Tomato", "category": "Vegetable", "season": "Rabi", "soil": "Red Sandy Loam", "days": 105, "water_mm": 600.0, "std_yield": 32000.0},
    {"name": "Wheat", "category": "Cereal", "season": "Rabi", "soil": "Alluvial", "days": 120, "water_mm": 450.0, "std_yield": 4000.0},
    {"name": "Rice", "category": "Cereal", "season": "Kharif", "soil": "Alluvial", "days": 125, "water_mm": 1200.0, "std_yield": 4500.0},
    {"name": "Maize", "category": "Cereal", "season": "Kharif", "soil": "Medium Black", "days": 105, "water_mm": 550.0, "std_yield": 5500.0},
    {"name": "Potato", "category": "Vegetable", "season": "Rabi", "soil": "Alluvial", "days": 90, "water_mm": 500.0, "std_yield": 24000.0},
    {"name": "Groundnut", "category": "Oilseed", "season": "Kharif", "soil": "Red Sandy Loam", "days": 110, "water_mm": 550.0, "std_yield": 2800.0},
    {"name": "Tur (Pigeon Pea)", "category": "Pulse", "season": "Kharif", "soil": "Medium Black", "days": 155, "water_mm": 600.0, "std_yield": 1800.0},
    {"name": "Chickpea (Gram)", "category": "Pulse", "season": "Rabi", "soil": "Deep Black", "days": 100, "water_mm": 350.0, "std_yield": 2000.0},
]

# Multiple seasons across 2023-2026 (12 seasons)
SEASONS_CATALOG = [
    {"season_id": 1, "name": "Kharif", "year": 2023, "start": date(2023, 6, 15), "end": date(2023, 10, 31)},
    {"season_id": 2, "name": "Rabi", "year": 2023, "start": date(2023, 11, 1), "end": date(2024, 3, 31)},
    {"season_id": 3, "name": "Summer", "year": 2024, "start": date(2024, 4, 1), "end": date(2024, 6, 10)},
    {"season_id": 4, "name": "Kharif", "year": 2024, "start": date(2024, 6, 15), "end": date(2024, 10, 31)},
    {"season_id": 5, "name": "Rabi", "year": 2024, "start": date(2024, 11, 1), "end": date(2025, 3, 31)},
    {"season_id": 6, "name": "Summer", "year": 2025, "start": date(2025, 4, 1), "end": date(2025, 6, 10)},
    {"season_id": 7, "name": "Kharif", "year": 2025, "start": date(2025, 6, 15), "end": date(2025, 10, 31)},
    {"season_id": 8, "name": "Rabi", "year": 2025, "start": date(2025, 11, 1), "end": date(2026, 3, 31)},
    {"season_id": 9, "name": "Summer", "year": 2026, "start": date(2026, 4, 1), "end": date(2026, 6, 10)},
    {"season_id": 10, "name": "Annual 2023", "year": 2023, "start": date(2023, 1, 1), "end": date(2023, 12, 31)},
    {"season_id": 11, "name": "Annual 2024", "year": 2024, "start": date(2024, 1, 1), "end": date(2024, 12, 31)},
    {"season_id": 12, "name": "Annual 2025", "year": 2025, "start": date(2025, 1, 1), "end": date(2025, 12, 31)},
]

SOIL_TYPES = ["Deep Black", "Medium Black", "Red Sandy Loam", "Alluvial", "Laterite"]
IRRIGATION_TYPES = ["Drip", "Sprinkler", "Canal Flood", "Tube Well"]
FERTILIZER_TYPES = ["Urea", "DAP", "NPK 10:26:26", "MOP", "SSP", "Neem Coated Urea", "FYM Compost"]


# -----------------------------------------------------------------------------
# Modular Generators (Prompt 2 Section 8)
# -----------------------------------------------------------------------------

def generate_farmers(count: int = 40) -> List[Dict[str, Any]]:
    """Generates 40 realistic farmers in Maharashtra."""
    farmers = []
    used_phones = set()
    for i in range(1, count + 1):
        dist_info = random.choice(DISTRICTS_MAHARASHTRA)
        fname = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        lname = LAST_NAMES[(i * 3) % len(LAST_NAMES)]
        name = f"{fname} {lname}"

        while True:
            phone = f"9{random.randint(700000000, 999999999)}"
            if phone not in used_phones:
                used_phones.add(phone)
                break

        village = random.choice(dist_info["villages"])
        district = dist_info["district"]

        farmers.append({
            "farmer_id": i,
            "name": name,
            "phone": phone,
            "village": village,
            "district": district,
            "state": "Maharashtra",
            "created_at": (datetime(2023, 1, 10, tzinfo=timezone.utc) + timedelta(days=i * 4)).isoformat(),
        })
    return farmers


def generate_farms(farmers: List[Dict[str, Any]], count: int = 55) -> List[Dict[str, Any]]:
    """Generates 55 landholdings linked to farmers."""
    farms = []
    dist_map = {d["district"]: d for d in DISTRICTS_MAHARASHTRA}

    # First, give 1 farm to each farmer
    for i in range(1, len(farmers) + 1):
        f = farmers[i - 1]
        dist_info = dist_map.get(f["district"], DISTRICTS_MAHARASHTRA[0])
        farm_name = f"{f['name'].split()[0]}'s {random.choice(['Krishi Farm', 'Wadi Plot', 'Bagayat Field', 'Green Acres', 'Sheti Plot'])}"
        area = round(random.uniform(1.2, 14.5), 2)
        soil = random.choice(SOIL_TYPES)
        irrig = random.choice(IRRIGATION_TYPES)
        lat = round(dist_info["lat"] + random.uniform(-0.12, 0.12), 6)
        lon = round(dist_info["lon"] + random.uniform(-0.12, 0.12), 6)

        farms.append({
            "farm_id": i,
            "farmer_id": f["farmer_id"],
            "farm_name": farm_name,
            "area_hectares": area,
            "soil_type": soil,
            "irrigation_type": irrig,
            "location": f"{f['village']}, {f['district']}",
            "latitude": lat,
            "longitude": lon,
            "created_at": (datetime(2023, 1, 15, tzinfo=timezone.utc) + timedelta(days=i * 2)).isoformat(),
        })

    # Additional farms for remaining count
    for j in range(len(farmers) + 1, count + 1):
        parent_farmer = random.choice(farmers)
        dist_info = dist_map.get(parent_farmer["district"], DISTRICTS_MAHARASHTRA[0])
        farm_name = f"{parent_farmer['name'].split()[0]}'s Parcel #{j}"
        area = round(random.uniform(1.5, 9.8), 2)
        soil = random.choice(SOIL_TYPES)
        irrig = random.choice(IRRIGATION_TYPES)
        lat = round(dist_info["lat"] + random.uniform(-0.15, 0.15), 6)
        lon = round(dist_info["lon"] + random.uniform(-0.15, 0.15), 6)

        farms.append({
            "farm_id": j,
            "farmer_id": parent_farmer["farmer_id"],
            "farm_name": farm_name,
            "area_hectares": area,
            "soil_type": soil,
            "irrigation_type": irrig,
            "location": f"{parent_farmer['village']}, {parent_farmer['district']}",
            "latitude": lat,
            "longitude": lon,
            "created_at": (datetime(2023, 2, 1, tzinfo=timezone.utc) + timedelta(days=j * 2)).isoformat(),
        })
    return farms


def generate_crops() -> List[Dict[str, Any]]:
    """Generates 12 crops with typical growth days and agronomic benchmarks."""
    crops = []
    for i, c in enumerate(CROPS_CATALOG, 1):
        crops.append({
            "crop_id": i,
            "crop_name": c["name"],
            "crop_category": c["category"],
            "ideal_season": c["season"],
            "ideal_soil_type": c["soil"],
            "typical_growth_days": c["days"],
            "water_requirement_mm": c["water_mm"],
            "standard_yield_kg_per_ha": c["std_yield"],
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc).isoformat(),
        })
    return crops


def generate_seasons() -> List[Dict[str, Any]]:
    """Generates 12 agricultural seasons across Kharif, Rabi, and Summer."""
    seasons = []
    for s in SEASONS_CATALOG:
        seasons.append({
            "season_id": s["season_id"],
            "season_name": s["name"],
            "year": s["year"],
            "start_date": s["start"].isoformat(),
            "end_date": s["end"].isoformat(),
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc).isoformat(),
        })
    return seasons


def generate_crop_cycles(
    farms: List[Dict[str, Any]],
    crops: List[Dict[str, Any]],
    seasons: List[Dict[str, Any]],
    target_count: int = 180,
) -> List[Dict[str, Any]]:
    """Generates 180+ crop cycles with expected & actual harvest dates and cultivated area."""
    cycles = []
    cycle_id = 1
    crop_map = {c["crop_id"]: c for c in crops}

    # Only seasonal cycles for regular planting (seasons 1 to 9)
    seasonal_seasons = [s for s in seasons if s["season_id"] <= 9]

    while len(cycles) < target_count:
        for farm in farms:
            if len(cycles) >= target_count:
                break

            # Pick 3 to 4 sequential seasons for this farm
            chosen_seasons = random.sample(seasonal_seasons, k=min(3, len(seasonal_seasons)))
            for s in sorted(chosen_seasons, key=lambda x: (x["year"], x["season_id"])):
                if len(cycles) >= target_count:
                    break

                # Pick crop matching season or perennial
                s_name = s["season_name"]
                matching_crops = [c for c in crops if c["ideal_season"] in (s_name, "Perennial")]
                crop = random.choice(matching_crops) if matching_crops else random.choice(crops)

                start_dt = date.fromisoformat(s["start_date"])
                sowing = start_dt + timedelta(days=random.randint(3, 20))
                expected_days = crop["typical_growth_days"]
                expected_harvest = sowing + timedelta(days=expected_days)

                # Determine completion status based on season date vs current simulation date
                if s["year"] <= 2024 or (s["year"] == 2025 and s["season_name"] in ("Kharif", "Rabi")):
                    status = "Harvested"
                    # Actual harvest has realistic deviation ±10 days
                    actual_harvest = expected_harvest + timedelta(days=random.randint(-8, 12))
                elif sowing < date(2026, 1, 1):
                    status = "Active"
                    actual_harvest = None
                else:
                    status = "Planned"
                    actual_harvest = None

                cultivated_area = round(farm["area_hectares"] * random.uniform(0.65, 1.0), 2)

                cycles.append({
                    "cycle_id": cycle_id,
                    "farm_id": farm["farm_id"],
                    "crop_id": crop["crop_id"],
                    "season_id": s["season_id"],
                    "sowing_date": sowing.isoformat(),
                    "expected_harvest_date": expected_harvest.isoformat(),
                    "actual_harvest_date": actual_harvest.isoformat() if actual_harvest else None,
                    "cultivated_area_hectares": cultivated_area,
                    "status": status,
                    "created_at": datetime.combine(sowing, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
                })
                cycle_id += 1

    return cycles[:target_count]


def generate_yield_records(cycles: List[Dict[str, Any]], crops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generates realistic harvest yields for completed crop cycles."""
    yields = []
    crop_map = {c["crop_id"]: c for c in crops}
    yield_id = 1

    for cycle in cycles:
        if cycle["status"] == "Harvested" and cycle["actual_harvest_date"]:
            crop = crop_map.get(cycle["crop_id"], {})
            std_yield = crop.get("standard_yield_kg_per_ha", 3000.0)
            area = cycle["cultivated_area_hectares"]

            # Realism: Yield varies 80% to 125% of standard benchmark based on management and conditions
            actual_yield_ha = round(std_yield * random.uniform(0.80, 1.25), 2)
            total_kg = round(actual_yield_ha * area, 2)
            grade = random.choices(["Grade A", "Grade B", "Standard", "Export Quality"], weights=[0.42, 0.35, 0.15, 0.08])[0]

            harvest_dt = date.fromisoformat(cycle["actual_harvest_date"])

            yields.append({
                "yield_id": yield_id,
                "cycle_id": cycle["cycle_id"],
                "harvest_date": harvest_dt.isoformat(),
                "yield_kg": total_kg,
                "yield_per_hectare": actual_yield_ha,
                "quality_grade": grade,
                "created_at": datetime.combine(harvest_dt, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
            })
            yield_id += 1

    return yields


def generate_soil_records(farms: List[Dict[str, Any]], target_count: int = 850) -> List[Dict[str, Any]]:
    """Generates 850+ realistic periodic soil laboratory and probe records."""
    records = []
    rec_id = 1
    base_date = date(2023, 2, 1)

    while len(records) < target_count:
        for farm in farms:
            if len(records) >= target_count:
                break
            num_samples = random.randint(14, 20)
            for s_idx in range(num_samples):
                if len(records) >= target_count:
                    break
                sample_date = base_date + timedelta(days=s_idx * 48 + random.randint(-8, 8))
                if sample_date > date(2025, 5, 1):
                    continue

                st = farm["soil_type"]
                if "Black" in st:
                    ph = round(random.gauss(7.6, 0.35), 1)
                    nitrogen = round(random.uniform(220.0, 420.0), 2)
                    phosphorus = round(random.uniform(14.0, 32.0), 2)
                    potassium = round(random.uniform(220.0, 440.0), 2)
                    moisture = round(random.uniform(28.0, 58.0), 2)
                    ec = round(random.uniform(0.4, 1.1), 2)
                    oc = round(random.uniform(0.45, 0.85), 2)
                elif "Sandy" in st:
                    ph = round(random.gauss(6.6, 0.3), 1)
                    nitrogen = round(random.uniform(170.0, 310.0), 2)
                    phosphorus = round(random.uniform(10.0, 22.0), 2)
                    potassium = round(random.uniform(120.0, 260.0), 2)
                    moisture = round(random.uniform(16.0, 38.0), 2)
                    ec = round(random.uniform(0.2, 0.7), 2)
                    oc = round(random.uniform(0.30, 0.60), 2)
                else:  # Alluvial / Laterite
                    ph = round(random.gauss(7.1, 0.35), 1)
                    nitrogen = round(random.uniform(240.0, 400.0), 2)
                    phosphorus = round(random.uniform(15.0, 30.0), 2)
                    potassium = round(random.uniform(180.0, 350.0), 2)
                    moisture = round(random.uniform(22.0, 46.0), 2)
                    ec = round(random.uniform(0.3, 0.85), 2)
                    oc = round(random.uniform(0.40, 0.75), 2)

                # Clamp pH to strict realistic agronomic boundaries
                ph = min(max(ph, 5.2), 8.9)

                records.append({
                    "soil_record_id": rec_id,
                    "farm_id": farm["farm_id"],
                    "record_date": sample_date.isoformat(),
                    "ph": ph,
                    "nitrogen": nitrogen,
                    "phosphorus": phosphorus,
                    "potassium": potassium,
                    "moisture_percentage": moisture,
                    "organic_carbon": oc,
                    "electrical_conductivity": ec,
                    "created_at": datetime.combine(sample_date, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
                })
                rec_id += 1

    return records[:target_count]


def generate_irrigation_records(
    cycles: List[Dict[str, Any]],
    farms: List[Dict[str, Any]],
    crops: List[Dict[str, Any]],
    target_count: int = 1200,
) -> List[Dict[str, Any]]:
    """
    Generates 1200+ realistic irrigation records.
    Enforces domain realism:
    - Rice and Sugarcane have higher water requirements
    - Drip is much more efficient than Canal Flood
    - Irrigation decreases during monsoon months (July-Sept)
    """
    records = []
    farm_map = {f["farm_id"]: f for f in farms}
    crop_map = {c["crop_id"]: c for c in crops}
    irrig_id = 1

    while len(records) < target_count:
        for cycle in cycles:
            if len(records) >= target_count:
                break
            farm = farm_map.get(cycle["farm_id"], {})
            crop = crop_map.get(cycle["crop_id"], {})
            method = farm.get("irrigation_type", "Drip")
            area = cycle["cultivated_area_hectares"]

            sowing = date.fromisoformat(cycle["sowing_date"])
            end_date = date.fromisoformat(cycle["actual_harvest_date"]) if cycle["actual_harvest_date"] else sowing + timedelta(days=120)
            total_days = max((end_date - sowing).days, 30)

            # High water crops (Rice, Sugarcane) have more frequent irrigation events
            is_high_water = crop.get("crop_name") in ("Rice", "Sugarcane")
            num_events = random.randint(7, 12) if is_high_water else random.randint(5, 8)

            for e in range(num_events):
                if len(records) >= target_count:
                    break
                event_date = sowing + timedelta(days=int((e + 0.5) * (total_days / num_events)))
                month = event_date.month

                # Realism: lower irrigation in monsoon months (July, August) due to rain
                monsoon_factor = 0.55 if month in (7, 8) else 1.0

                if method == "Drip":
                    water_per_ha = random.uniform(18000, 32000) * monsoon_factor
                    dur_min = int(random.uniform(120, 240))
                elif method == "Sprinkler":
                    water_per_ha = random.uniform(28000, 52000) * monsoon_factor
                    dur_min = int(random.uniform(180, 360))
                elif method == "Canal Flood":
                    water_per_ha = random.uniform(90000, 190000) * monsoon_factor
                    dur_min = int(random.uniform(300, 600))
                else:  # Tube Well
                    water_per_ha = random.uniform(45000, 95000) * monsoon_factor
                    dur_min = int(random.uniform(240, 480))

                # Extra water multiplier for high water demand crops
                if crop.get("crop_name") == "Sugarcane":
                    water_per_ha *= 1.4
                elif crop.get("crop_name") == "Rice":
                    water_per_ha *= 1.35

                water_liters = round(water_per_ha * area, 2)

                records.append({
                    "irrigation_id": irrig_id,
                    "farm_id": farm["farm_id"],
                    "cycle_id": cycle["cycle_id"],
                    "date": event_date.isoformat(),
                    "water_used_liters": water_liters,
                    "irrigation_method": method,
                    "duration_minutes": dur_min,
                    "created_at": datetime.combine(event_date, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
                })
                irrig_id += 1

    return records[:target_count]


def generate_fertilizer_records(
    cycles: List[Dict[str, Any]],
    crops: List[Dict[str, Any]],
    target_count: int = 700,
) -> List[Dict[str, Any]]:
    """
    Generates 700+ fertilizer application records.
    Enforces domain realism:
    - Quantities correspond roughly to cultivated area and crop requirements
    - Basal, top-dressing, and fertigation dosages
    """
    records = []
    fert_id = 1

    doses = [
        {"offset": 0, "type": "DAP", "method": "Basal", "rate": (70, 110)},
        {"offset": 25, "type": "Urea", "method": "Broadcast", "rate": (50, 90)},
        {"offset": 55, "type": "NPK 10:26:26", "method": "Fertigation", "rate": (60, 100)},
        {"offset": 80, "type": "MOP", "method": "Foliar Spray", "rate": (25, 45)},
    ]

    while len(records) < target_count:
        for cycle in cycles:
            if len(records) >= target_count:
                break
            area = cycle["cultivated_area_hectares"]
            sowing = date.fromisoformat(cycle["sowing_date"])

            for d in doses:
                if len(records) >= target_count:
                    break
                event_date = sowing + timedelta(days=d["offset"])
                rate = random.uniform(d["rate"][0], d["rate"][1])
                qty = round(rate * area, 2)

                records.append({
                    "fertilizer_id": fert_id,
                    "farm_id": cycle["farm_id"],
                    "crop_id": cycle["crop_id"],
                    "cycle_id": cycle["cycle_id"],
                    "date": event_date.isoformat(),
                    "fertilizer_type": d["type"],
                    "quantity_kg": qty,
                    "application_method": d["method"],
                    "created_at": datetime.combine(event_date, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
                })
                fert_id += 1

    return records[:target_count]


def generate_weather_observations(farms: List[Dict[str, Any]], target_count: int = 1500) -> List[Dict[str, Any]]:
    """
    Generates 1500+ semi-structured weather telemetry documents for MongoDB.
    Structure: { farm_id, date, temperature_c, humidity_percentage, rainfall_mm, wind_speed_kmh, weather_condition }
    """
    records = []
    base_date = date(2023, 6, 1)

    for i in range(target_count):
        farm = random.choice(farms)
        obs_date = base_date + timedelta(days=(i % 650) + random.randint(0, 1))
        month = obs_date.month

        # Seasonal weather patterns in Maharashtra
        if 6 <= month <= 9:  # Monsoon
            temp = round(random.uniform(24.0, 31.5), 1)
            humidity = round(random.uniform(68.0, 95.0), 1)
            rain = round(random.choices([0.0, random.uniform(5.0, 40.0), random.uniform(40.0, 105.0)], weights=[0.35, 0.45, 0.20])[0], 1)
            cond = "Rainy" if rain > 8.0 else ("Overcast" if humidity > 78 else "Cloudy")
            wind = round(random.uniform(10.0, 28.0), 1)
        elif month in (11, 12, 1, 2):  # Winter / Rabi
            temp = round(random.uniform(13.5, 27.0), 1)
            humidity = round(random.uniform(32.0, 58.0), 1)
            rain = 0.0 if random.random() < 0.95 else round(random.uniform(1.0, 6.0), 1)
            cond = "Clear" if humidity < 50 else "Mist"
            wind = round(random.uniform(4.0, 14.0), 1)
        else:  # Summer / Zaid (March - May)
            temp = round(random.uniform(32.0, 42.0), 1)
            humidity = round(random.uniform(18.0, 42.0), 1)
            rain = 0.0 if random.random() < 0.90 else round(random.uniform(4.0, 20.0), 1)
            cond = "Sunny" if temp > 35 else "Partly Cloudy"
            wind = round(random.uniform(6.0, 20.0), 1)

        records.append({
            "farm_id": farm["farm_id"],
            "date": obs_date.isoformat(),
            "temperature_c": temp,
            "humidity_percentage": humidity,
            "rainfall_mm": rain,
            "wind_speed_kmh": wind,
            "weather_condition": cond,
            "district": farm.get("location", "").split(",")[-1].strip(),
        })

    return records


def generate_field_observations(
    farms: List[Dict[str, Any]],
    crops: List[Dict[str, Any]],
    target_count: int = 500,
) -> List[Dict[str, Any]]:
    """
    Generates 500+ qualitative field scouting observations for MongoDB.
    Structure: { farm_id, crop_id, date, observation_type, severity, description, metadata }
    Observation types:
    - Normal crop growth
    - Low soil moisture
    - Excess moisture
    - Nutrient deficiency indication
    - Pest observation
    - Weed observation
    - Crop stress
    """
    records = []
    types_pool = [
        ("Normal crop growth", "Low", "Crop canopy development is healthy and uniform across plot."),
        ("Low soil moisture", "Medium", "Upper 10cm soil dry to touch, wilting observed in late afternoon."),
        ("Excess moisture", "Medium", "Waterlogging in low-lying furrow sections following rainfall."),
        ("Nutrient deficiency indication", "Medium", "Interveinal chlorosis observed on older leaves, indicating N/Fe deficit."),
        ("Pest observation", "High", "Active pest cluster noticed on lower leaves; threshold scouting recommended."),
        ("Weed observation", "Low", "Broadleaf weeds emerging along irrigation furrows."),
        ("Crop stress", "High", "Canopy leaf curling due to elevated temperatures and moisture stress."),
    ]
    scouts = ["Dr. S. K. Mahajan (KVK)", "P. R. Shinde (Agri Officer)", "V. B. Jadhav (Field Scout)", "K. N. Patil (Agronomist)"]
    base_date = date(2023, 7, 1)

    for i in range(1, target_count + 1):
        farm = random.choice(farms)
        crop = random.choice(crops)
        obs_date = base_date + timedelta(days=(i % 600) + random.randint(0, 3))
        obs_type, sev, desc = random.choice(types_pool)

        metadata = {
            "scout_name": random.choice(scouts),
            "crop_health_rating": 5 if obs_type == "Normal crop growth" else random.choice([2, 3, 4]),
            "field_quadrant": random.choice(["North-East", "South-West", "Center Plot", "Furrow Zone"]),
            "action_taken": "No action needed" if sev == "Low" else "Recommendation dispatched to farmer",
        }

        records.append({
            "farm_id": farm["farm_id"],
            "crop_id": crop["crop_id"],
            "date": obs_date.isoformat(),
            "observation_type": obs_type,
            "severity": sev,
            "description": f"{desc} ({farm['farm_name']}, {crop['crop_name']})",
            "metadata": metadata,
        })

    return records


def generate_agricultural_alerts(farms: List[Dict[str, Any]], target_count: int = 80) -> List[Dict[str, Any]]:
    """
    Generates 80+ rule-based alerts triggered by statistical/threshold violations.
    Structure: { farm_id, alert_type, severity, message, metric, actual_value, threshold_value, created_at, status }
    """
    records = []
    alert_rules = [
        {"type": "Soil Acidity Warning", "sev": "Warning", "metric": "ph", "msg": "Soil pH fell below minimum agronomic threshold", "actual": 5.4, "thresh": 5.8},
        {"type": "Soil Alkalinity Hazard", "sev": "High", "metric": "ph", "msg": "Soil pH exceeds safe sodicity threshold", "actual": 8.8, "thresh": 8.5},
        {"type": "Moisture Deficit", "sev": "High", "metric": "moisture_percentage", "msg": "Soil moisture dropped below critical threshold", "actual": 17.5, "thresh": 20.0},
        {"type": "Extreme Water Deficit", "sev": "Critical", "metric": "water_used_liters", "msg": "Cumulative irrigation water 40% below crop requirement", "actual": 18000.0, "thresh": 30000.0},
        {"type": "High Temperature Heat Stress", "sev": "High", "metric": "temperature_c", "msg": "Ambient temperature exceeded 38C during critical growth phase", "actual": 40.5, "thresh": 38.0},
    ]

    base_time = datetime(2023, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
    for i in range(1, target_count + 1):
        rule = random.choice(alert_rules)
        farm = random.choice(farms)
        ts = base_time + timedelta(days=i * 7 + random.randint(0, 3))
        status = random.choices(["Open", "Acknowledged", "Resolved"], weights=[0.3, 0.3, 0.4])[0]

        records.append({
            "farm_id": farm["farm_id"],
            "alert_type": rule["type"],
            "severity": rule["sev"],
            "message": f"{rule['msg']} on {farm['farm_name']}",
            "metric": rule["metric"],
            "actual_value": round(rule["actual"] + random.uniform(-0.4, 0.4), 2),
            "threshold_value": rule["thresh"],
            "created_at": ts.isoformat(),
            "status": status,
        })

    return records


def generate_activity_logs(target_count: int = 100) -> List[Dict[str, Any]]:
    """
    Generates 100+ audit activity logs.
    Activities: data import, data update, alert generation, database synchronization.
    """
    records = []
    actions = [
        ("data import", "crop_cycles", "Batch imported seasonal crop cycle records from agronomist portal"),
        ("data update", "soil_records", "Updated soil chemical analysis from KVK laboratory testing"),
        ("alert generation", "agricultural_alerts", "Rule-based engine evaluated threshold conditions and dispatched alert"),
        ("database synchronization", "database", "Synchronized relational records and generated MongoDB observation documents"),
    ]

    base_time = datetime(2023, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
    for i in range(1, target_count + 1):
        action, entity, msg = random.choice(actions)
        ts = base_time + timedelta(days=i * 6 + random.randint(0, 2))
        records.append({
            "action": action,
            "entity": entity,
            "entity_id": str(random.randint(1, 55)),
            "user": random.choice(["system", "admin_agrisense", "kvk_operator"]),
            "timestamp": ts.isoformat(),
            "details": {"summary": msg, "records_affected": random.randint(1, 50)},
        })

    return records


# -----------------------------------------------------------------------------
# Seeding and Export Workflow
# -----------------------------------------------------------------------------

def export_all_datasets_to_disk(raw_dir: Path) -> Dict[str, int]:
    """Generates all datasets and exports them into CSV and JSON in data/raw/."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    counts = {}

    print("Generating farmers and farms...")
    farmers = generate_farmers(count=40)
    farms = generate_farms(farmers, count=55)
    pd.DataFrame(farmers).to_csv(raw_dir / "farmers.csv", index=False)
    pd.DataFrame(farms).to_csv(raw_dir / "farms.csv", index=False)
    counts["farmers"] = len(farmers)
    counts["farms"] = len(farms)

    print("Generating crops and seasons...")
    crops = generate_crops()
    seasons = generate_seasons()
    pd.DataFrame(crops).to_csv(raw_dir / "crops.csv", index=False)
    pd.DataFrame(seasons).to_csv(raw_dir / "seasons.csv", index=False)
    counts["crops"] = len(crops)
    counts["seasons"] = len(seasons)

    print("Generating crop cycles and yields...")
    cycles = generate_crop_cycles(farms, crops, seasons, target_count=180)
    yields = generate_yield_records(cycles, crops)
    pd.DataFrame(cycles).to_csv(raw_dir / "crop_cycles.csv", index=False)
    pd.DataFrame(yields).to_csv(raw_dir / "yield_records.csv", index=False)
    counts["crop_cycles"] = len(cycles)
    counts["yield_records"] = len(yields)

    print("Generating soil records...")
    soil_records = generate_soil_records(farms, target_count=850)
    pd.DataFrame(soil_records).to_csv(raw_dir / "soil_records.csv", index=False)
    counts["soil_records"] = len(soil_records)

    print("Generating irrigation records...")
    irrigation_records = generate_irrigation_records(cycles, farms, crops, target_count=1200)
    pd.DataFrame(irrigation_records).to_csv(raw_dir / "irrigation_records.csv", index=False)
    counts["irrigation_records"] = len(irrigation_records)

    print("Generating fertilizer records...")
    fertilizer_records = generate_fertilizer_records(cycles, crops, target_count=700)
    pd.DataFrame(fertilizer_records).to_csv(raw_dir / "fertilizer_records.csv", index=False)
    counts["fertilizer_records"] = len(fertilizer_records)

    print("Generating MongoDB observations, alerts & logs...")
    weather = generate_weather_observations(farms, target_count=1500)
    with open(raw_dir / "weather_observations.json", "w", encoding="utf-8") as f:
        json.dump(weather, f, indent=2)
    counts["weather_observations"] = len(weather)

    field_obs = generate_field_observations(farms, crops, target_count=500)
    with open(raw_dir / "field_observations.json", "w", encoding="utf-8") as f:
        json.dump(field_obs, f, indent=2)
    counts["field_observations"] = len(field_obs)

    alerts = generate_agricultural_alerts(farms, target_count=80)
    with open(raw_dir / "agricultural_alerts.json", "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
    counts["agricultural_alerts"] = len(alerts)

    activity = generate_activity_logs(target_count=100)
    with open(raw_dir / "activity_logs.json", "w", encoding="utf-8") as f:
        json.dump(activity, f, indent=2)
    counts["activity_logs"] = len(activity)

    return counts


def seed_mysql_from_files(raw_dir: Path, reset: bool = False) -> Tuple[bool, str]:
    """Inserts raw CSV records into live MySQL database if connected."""
    from database.mysql_connection import get_db_session, init_mysql_tables, check_mysql_connection
    from models import (
        Base, Farmer, Farm, Crop, Season, CropCycle,
        SoilRecord, IrrigationRecord, FertilizerRecord, YieldRecord
    )

    ok, conn_msg = check_mysql_connection()
    if not ok:
        return False, f"MySQL is not connected: {conn_msg}"

    try:
        init_mysql_tables()

        with get_db_session() as session:
            if reset:
                # Clear in reverse foreign key order
                session.query(YieldRecord).delete()
                session.query(FertilizerRecord).delete()
                session.query(IrrigationRecord).delete()
                session.query(SoilRecord).delete()
                session.query(CropCycle).delete()
                session.query(Season).delete()
                session.query(Crop).delete()
                session.query(Farm).delete()
                session.query(Farmer).delete()
                session.flush()

            # Check if tables already seeded
            if not reset and session.query(Farmer).first() is not None:
                return True, "MySQL database already contains seeded data; skipping duplicate insertion."

            # Farmers
            df_farmers = pd.read_csv(raw_dir / "farmers.csv")
            for _, r in df_farmers.iterrows():
                session.add(Farmer(
                    farmer_id=int(r["farmer_id"]),
                    name=str(r["name"]),
                    phone=str(r["phone"]),
                    village=str(r["village"]),
                    district=str(r["district"]),
                    state=str(r["state"]),
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Farms
            df_farms = pd.read_csv(raw_dir / "farms.csv")
            for _, r in df_farms.iterrows():
                session.add(Farm(
                    farm_id=int(r["farm_id"]),
                    farmer_id=int(r["farmer_id"]),
                    farm_name=str(r["farm_name"]),
                    area_hectares=float(r["area_hectares"]),
                    soil_type=str(r["soil_type"]),
                    irrigation_type=str(r["irrigation_type"]),
                    location=str(r["location"]) if pd.notna(r.get("location")) else None,
                    latitude=float(r["latitude"]) if pd.notna(r.get("latitude")) else None,
                    longitude=float(r["longitude"]) if pd.notna(r.get("longitude")) else None,
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Crops
            df_crops = pd.read_csv(raw_dir / "crops.csv")
            for _, r in df_crops.iterrows():
                session.add(Crop(
                    crop_id=int(r["crop_id"]),
                    crop_name=str(r["crop_name"]),
                    crop_category=str(r["crop_category"]),
                    ideal_season=str(r["ideal_season"]),
                    ideal_soil_type=str(r["ideal_soil_type"]),
                    typical_growth_days=int(r["typical_growth_days"]) if "typical_growth_days" in r and pd.notna(r["typical_growth_days"]) else 120,
                    water_requirement_mm=float(r["water_requirement_mm"]) if pd.notna(r.get("water_requirement_mm")) else None,
                    standard_yield_kg_per_ha=float(r["standard_yield_kg_per_ha"]) if pd.notna(r.get("standard_yield_kg_per_ha")) else None,
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Seasons
            df_seasons = pd.read_csv(raw_dir / "seasons.csv")
            for _, r in df_seasons.iterrows():
                session.add(Season(
                    season_id=int(r["season_id"]),
                    season_name=str(r["season_name"]),
                    year=int(r["year"]),
                    start_date=date.fromisoformat(str(r["start_date"])),
                    end_date=date.fromisoformat(str(r["end_date"])),
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Crop Cycles
            df_cycles = pd.read_csv(raw_dir / "crop_cycles.csv")
            for _, r in df_cycles.iterrows():
                session.add(CropCycle(
                    cycle_id=int(r["cycle_id"]),
                    farm_id=int(r["farm_id"]),
                    crop_id=int(r["crop_id"]),
                    season_id=int(r["season_id"]),
                    sowing_date=date.fromisoformat(str(r["sowing_date"])),
                    expected_harvest_date=date.fromisoformat(str(r["expected_harvest_date"])) if pd.notna(r.get("expected_harvest_date")) else None,
                    actual_harvest_date=date.fromisoformat(str(r["actual_harvest_date"])) if pd.notna(r.get("actual_harvest_date")) else None,
                    cultivated_area_hectares=float(r["cultivated_area_hectares"]),
                    status=str(r["status"]),
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Soil Records
            df_soil = pd.read_csv(raw_dir / "soil_records.csv")
            for _, r in df_soil.iterrows():
                session.add(SoilRecord(
                    soil_record_id=int(r["soil_record_id"]),
                    farm_id=int(r["farm_id"]),
                    record_date=date.fromisoformat(str(r["record_date"])),
                    ph=float(r["ph"]),
                    nitrogen=float(r["nitrogen"]),
                    phosphorus=float(r["phosphorus"]),
                    potassium=float(r["potassium"]),
                    moisture_percentage=float(r["moisture_percentage"]),
                    organic_carbon=float(r["organic_carbon"]) if pd.notna(r.get("organic_carbon")) else None,
                    electrical_conductivity=float(r["electrical_conductivity"]) if pd.notna(r.get("electrical_conductivity")) else None,
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Irrigation Records
            df_irrig = pd.read_csv(raw_dir / "irrigation_records.csv")
            for _, r in df_irrig.iterrows():
                session.add(IrrigationRecord(
                    irrigation_id=int(r["irrigation_id"]),
                    farm_id=int(r["farm_id"]),
                    cycle_id=int(r["cycle_id"]) if pd.notna(r.get("cycle_id")) else None,
                    date=date.fromisoformat(str(r["date"])),
                    water_used_liters=float(r["water_used_liters"]),
                    irrigation_method=str(r["irrigation_method"]),
                    duration_minutes=int(r["duration_minutes"]) if pd.notna(r.get("duration_minutes")) else None,
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Fertilizer Records
            df_fert = pd.read_csv(raw_dir / "fertilizer_records.csv")
            for _, r in df_fert.iterrows():
                session.add(FertilizerRecord(
                    fertilizer_id=int(r["fertilizer_id"]),
                    farm_id=int(r["farm_id"]),
                    crop_id=int(r["crop_id"]),
                    cycle_id=int(r["cycle_id"]) if pd.notna(r.get("cycle_id")) else None,
                    date=date.fromisoformat(str(r["date"])),
                    fertilizer_type=str(r["fertilizer_type"]),
                    quantity_kg=float(r["quantity_kg"]),
                    application_method=str(r["application_method"]) if pd.notna(r.get("application_method")) else None,
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

            # Yield Records
            df_yield = pd.read_csv(raw_dir / "yield_records.csv")
            for _, r in df_yield.iterrows():
                session.add(YieldRecord(
                    yield_id=int(r["yield_id"]),
                    cycle_id=int(r["cycle_id"]),
                    harvest_date=date.fromisoformat(str(r["harvest_date"])),
                    yield_kg=float(r["yield_kg"]),
                    yield_per_hectare=float(r["yield_per_hectare"]),
                    quality_grade=str(r["quality_grade"]) if pd.notna(r.get("quality_grade")) else None,
                    created_at=datetime.fromisoformat(str(r["created_at"])),
                ))
            session.flush()

        return True, "Successfully seeded MySQL relational tables!"
    except Exception as e:
        return False, f"Failed seeding MySQL: {str(e)}"


def seed_mongo_from_files(raw_dir: Path, reset: bool = False) -> Tuple[bool, str]:
    """Inserts raw JSON collections into live MongoDB database if connected."""
    from database.mongo_connection import get_mongo_db, init_mongo_indexes, check_mongo_connection

    ok, conn_msg = check_mongo_connection()
    if not ok:
        return False, f"MongoDB is not connected: {conn_msg}"

    db = get_mongo_db()
    if db is None:
        return False, "MongoDB handle is unavailable."

    try:
        init_mongo_indexes()

        collections = [
            ("weather_observations", "weather_observations.json"),
            ("field_observations", "field_observations.json"),
            ("agricultural_alerts", "agricultural_alerts.json"),
            ("activity_logs", "activity_logs.json"),
        ]

        for col_name, file_name in collections:
            col = db[col_name]
            if reset:
                col.delete_many({})
            if col.count_documents({}) == 0:
                with open(raw_dir / file_name, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                if docs:
                    col.insert_many(docs)

        return True, "Successfully seeded MongoDB semi-structured collections!"
    except Exception as e:
        return False, f"Failed seeding MongoDB: {str(e)}"


def main():
    """Main CLI entrypoint for seed_data.py."""
    raw_dir = settings.paths.raw_data_dir
    reset = "--reset" in sys.argv

    print("\nAgriSense Database Seeding")
    print("--------------------------")
    counts = export_all_datasets_to_disk(raw_dir)

    print(f"Farmers inserted: {counts.get('farmers', 0)}")
    print(f"Farms inserted: {counts.get('farms', 0)}")
    print(f"Crops inserted: {counts.get('crops', 0)}")
    print(f"Seasons inserted: {counts.get('seasons', 0)}")
    print(f"Crop cycles inserted: {counts.get('crop_cycles', 0)}")
    print(f"Soil records inserted: {counts.get('soil_records', 0)}")
    print(f"Irrigation records inserted: {counts.get('irrigation_records', 0)}")
    print(f"Fertilizer records inserted: {counts.get('fertilizer_records', 0)}")
    print(f"Yield records inserted: {counts.get('yield_records', 0)}")
    print("\nMongoDB")
    print(f"Weather observations: {counts.get('weather_observations', 0)}")
    print(f"Field observations: {counts.get('field_observations', 0)}")
    print(f"Alerts inserted: {counts.get('agricultural_alerts', 0)}")
    print(f"Activity logs inserted: {counts.get('activity_logs', 0)}")

    # Attempt to seed live MySQL if reachable
    from database.mysql_connection import check_mysql_connection
    my_ok, _ = check_mysql_connection()
    if my_ok:
        print("\nConnecting to live MySQL...")
        s_ok, s_msg = seed_mysql_from_files(raw_dir, reset=reset)
        print(f"MySQL Status: {s_msg}")

    # Attempt to seed live MongoDB if reachable
    from database.mongo_connection import check_mongo_connection
    mo_ok, _ = check_mongo_connection()
    if mo_ok:
        print("\nConnecting to live MongoDB...")
        m_ok, m_msg = seed_mongo_from_files(raw_dir, reset=reset)
        print(f"MongoDB Status: {m_msg}")

    print("\nDatabase setup completed successfully.")


if __name__ == "__main__":
    main()
