"""
AgriSense - MongoDB Document Schemas (Pydantic Models)
Flexible, semi-structured data models for MongoDB collections in Prompt 2:
- weather_observations: farm_id, date, temperature_c, humidity_percentage, rainfall_mm, wind_speed_kmh, weather_condition
- field_observations: farm_id, crop_id, date, observation_type, severity, description, metadata
- agricultural_alerts: farm_id, alert_type, severity, message, metric, actual_value, threshold_value, created_at, status
- activity_logs: action, entity, entity_id, user, timestamp, details
"""
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class WeatherObservation(BaseModel):
    """Semi-structured meteorological telemetry from weather stations/sensors for farms."""
    farm_id: int = Field(..., description="Target farm identifier")
    date: str = Field(..., description="Observation date (YYYY-MM-DD)")
    temperature_c: float = Field(..., description="Air temperature in Celsius")
    humidity_percentage: float = Field(..., ge=0.0, le=100.0, description="Relative humidity %")
    rainfall_mm: float = Field(default=0.0, ge=0.0, description="Precipitation in mm")
    wind_speed_kmh: float = Field(default=0.0, ge=0.0, description="Wind speed in km/h")
    weather_condition: str = Field(default="Clear", description="Clear, Sunny, Rainy, Overcast, Partly Cloudy, Mist")
    
    # Supporting fields for rich telemetry
    station_id: Optional[str] = Field(None, description="Source weather station code")
    district: Optional[str] = Field(None, description="District name")
    solar_radiation: Optional[float] = Field(None, description="Solar irradiance in W/m²")

    # Backward compatibility properties
    @property
    def temperature(self) -> float:
        return self.temperature_c

    @property
    def humidity(self) -> float:
        return self.humidity_percentage

    @property
    def timestamp(self) -> str:
        return f"{self.date}T12:00:00Z"

    def to_mongo(self) -> Dict[str, Any]:
        return self.model_dump()


class FieldObservation(BaseModel):
    """Qualitative scouting observations, crop conditions, pest/weed records."""
    farm_id: int = Field(..., description="Associated farm ID")
    crop_id: int = Field(..., description="Associated crop ID")
    date: str = Field(..., description="Observation date (YYYY-MM-DD)")
    observation_type: str = Field(..., description="Normal crop growth, Low soil moisture, Excess moisture, Nutrient deficiency indication, Pest observation, Weed observation, Crop stress")
    severity: str = Field(default="Low", description="Low, Medium, High, Critical")
    description: str = Field(..., description="Scouting notes and detailed description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata per observation type")

    # Backward compatibility properties
    @property
    def observation_id(self) -> str:
        return self.metadata.get("observation_id", f"OBS-{self.farm_id}")

    @property
    def observation_date(self) -> str:
        return self.date

    @property
    def crop_health_rating(self) -> int:
        return self.metadata.get("crop_health_rating", 3)

    def to_mongo(self) -> Dict[str, Any]:
        return self.model_dump()


class AgriculturalAlert(BaseModel):
    """Rule-based alerts triggered by statistical/threshold violations."""
    farm_id: int = Field(..., description="Associated farm ID")
    alert_type: str = Field(..., description="Soil Acidity Warning, Moisture Deficit, Heat Stress, etc.")
    severity: str = Field(..., description="Info, Warning, High, Critical")
    message: str = Field(..., description="Human-readable notification message")
    metric: str = Field(..., description="Evaluated metric name (e.g. ph, moisture, temp)")
    actual_value: float = Field(..., description="Calculated metric value that triggered the alert")
    threshold_value: float = Field(..., description="Expected rule threshold")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="Open", description="Open, Acknowledged, Resolved")

    # Backward compatibility properties
    @property
    def alert_id(self) -> str:
        return f"ALT-{self.farm_id}-{self.metric}"

    @property
    def trigger_rule(self) -> str:
        return self.message

    @property
    def metric_value(self) -> float:
        return self.actual_value

    @property
    def timestamp(self) -> str:
        return self.created_at

    def to_mongo(self) -> Dict[str, Any]:
        return self.model_dump()


class SensorObservation(BaseModel):
    """IoT sensor telemetry payload (soil sensors, weather micro-stations, etc.)."""
    farm_id: int = Field(..., description="Associated farm ID")
    sensor_id: str = Field(..., description="Unique sensor device identifier")
    sensor_type: str = Field(..., description="soil_moisture, soil_temp, air_temp, humidity, pH_sensor, NPK_sensor")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    value: float = Field(..., description="Primary sensor reading value")
    unit: str = Field(..., description="Unit of measurement (%, °C, dS/m, mg/kg, etc.)")
    battery_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Sensor battery level %")
    signal_strength: Optional[int] = Field(None, description="Wireless signal strength (RSSI dBm)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional sensor payload fields")

    def to_mongo(self) -> Dict[str, Any]:
        return self.model_dump()


class ActivityLog(BaseModel):
    """Platform audit trail for database synchronization, imports, and updates."""
    action: str = Field(..., description="data import, data update, alert generation, database synchronization")
    entity: str = Field(..., description="Target entity type")
    entity_id: Optional[str] = Field(None, description="Target record key")
    user: str = Field(default="system", description="User or automated agent responsible")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary event payload")

    # Backward compatibility property
    @property
    def log_id(self) -> str:
        return self.details.get("log_id", "LOG")

    def to_mongo(self) -> Dict[str, Any]:
        return self.model_dump()
