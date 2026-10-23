"""
AgriSense - General Agronomic and Formatting Helpers
Provides unit conversions, Indian agricultural season rules, and soil threshold classifications.
"""
from datetime import date
from typing import Literal


def classify_season_by_month(month: int) -> str:
    """
    Classifies agricultural season in India based on calendar month:
    - Kharif: June (6) to October (10) [Monsoon crops]
    - Rabi: November (11) to March (3) [Winter crops]
    - Zaid: April (4) to May (5) [Summer crops]
    """
    if 6 <= month <= 10:
        return "Kharif"
    elif month in (11, 12, 1, 2, 3):
        return "Rabi"
    else:
        return "Zaid"


def classify_soil_ph(ph: float) -> str:
    """Classifies soil pH into standard agronomic health bands."""
    if ph < 5.5:
        return "Strongly Acidic"
    elif ph < 6.5:
        return "Slightly Acidic"
    elif ph <= 7.5:
        return "Optimal / Neutral"
    elif ph <= 8.5:
        return "Moderately Alkaline"
    else:
        return "Strongly Alkaline"


def classify_soil_nutrient(nutrient: Literal["N", "P", "K"], value: float) -> str:
    """
    Classifies Indian soil nutrient fertility indices (kg/ha) based on ICAR guidelines:
    - Nitrogen: Low (< 280), Medium (280 - 560), High (> 560)
    - Phosphorus: Low (< 10), Medium (10 - 25), High (> 25)
    - Potassium: Low (< 110), Medium (110 - 280), High (> 280)
    """
    if nutrient == "N":
        if value < 280:
            return "Low"
        elif value <= 560:
            return "Medium"
        return "High"
    elif nutrient == "P":
        if value < 10:
            return "Low"
        elif value <= 25:
            return "Medium"
        return "High"
    elif nutrient == "K":
        if value < 110:
            return "Low"
        elif value <= 280:
            return "Medium"
        return "High"
    return "Unknown"


def format_number(val: float, decimals: int = 1) -> str:
    """Formats float numbers with comma separators."""
    if val is None:
        return "N/A"
    return f"{val:,.{decimals}f}"


def kg_to_quintals(kg: float) -> float:
    """Converts kilograms to Indian Quintals (1 Quintal = 100 kg)."""
    return kg / 100.0


def kg_to_metric_tonnes(kg: float) -> float:
    """Converts kilograms to Metric Tonnes (1 Tonne = 1,000 kg)."""
    return kg / 1000.0


def liters_to_cubic_meters(liters: float) -> float:
    """Converts water liters to cubic meters (1 m³ = 1,000 liters)."""
    return liters / 1000.0
