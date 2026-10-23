"""
AgriSense - Input and Domain Validation Utilities
Validates agronomic values, phone numbers, geographic coordinates, and date ranges.
"""
import re
from datetime import date, datetime
from typing import Tuple, Optional


def validate_indian_phone(phone: str) -> bool:
    """Validates Indian mobile number format (+91 or standard 10 digits starting 6-9)."""
    if not phone:
        return False
    clean = re.sub(r"[\s\-\+]", "", phone)
    if clean.startswith("91") and len(clean) == 12:
        clean = clean[2:]
    return bool(re.match(r"^[6-9]\d{9}$", clean))


def validate_coordinates(lat: Optional[float], lon: Optional[float]) -> bool:
    """
    Validates geographical coordinates within the approximate bounding box of Maharashtra, India.
    Latitude: ~15.5°N to 22.2°N
    Longitude: ~72.5°E to 81.0°E
    """
    if lat is None or lon is None:
        return True  # Coordinates are optional
    return (15.5 <= lat <= 22.5) and (72.5 <= lon <= 81.2)


def validate_soil_ph(ph: float) -> Tuple[bool, str]:
    """Validates soil pH against standard agronomic scale."""
    if ph < 0 or ph > 14:
        return False, "pH must be between 0.0 and 14.0."
    if ph < 4.0:
        return True, "Extreme Acidity (Rare in Maharashtra; review sample)."
    if ph > 9.5:
        return True, "Strongly Alkaline (Sodic soil condition)."
    return True, "Normal agricultural pH range."


def validate_crop_cycle_dates(sowing: date, harvest: Optional[date]) -> Tuple[bool, str]:
    """Ensures harvest date does not precede sowing date."""
    if harvest is not None and harvest < sowing:
        return False, "Harvest date cannot be earlier than sowing date."
    return True, "Dates are logically valid."
