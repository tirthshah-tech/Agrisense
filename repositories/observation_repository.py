"""
Observation and Semi-Structured Repository (MongoDB + JSON Fallback).
Handles Weather, Field Scouting, Agricultural Alerts, IoT Sensors, and Audit Logs.
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

from repositories.base_repository import BaseRepository
from database.mongo_connection import (
    get_weather_collection,
    get_field_observations_collection,
    get_alerts_collection,
    get_sensor_collection,
    get_activity_logs_collection,
)

logger = logging.getLogger(__name__)


class ObservationRepository(BaseRepository):
    """Repository for semi-structured observations and telemetry."""

    def get_weather_observations(self, limit: int = 1000) -> pd.DataFrame:
        """Retrieves weather telemetry."""
        if self.is_mongo_available():
            try:
                col = get_weather_collection()
                if col is not None:
                    docs = list(col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
                    if docs:
                        return pd.DataFrame(docs)
            except Exception as e:
                logger.warning("Error fetching weather from MongoDB: %s", e)

        data = self.load_json_fallback("weather_observations.json")
        return pd.DataFrame(data[:limit]) if data else pd.DataFrame()

    def get_field_observations(self, limit: int = 500) -> pd.DataFrame:
        """Retrieves agronomist field scouting observations."""
        if self.is_mongo_available():
            try:
                col = get_field_observations_collection()
                if col is not None:
                    docs = list(col.find({}, {"_id": 0}).sort("observation_date", -1).limit(limit))
                    if docs:
                        return pd.DataFrame(docs)
            except Exception as e:
                logger.warning("Error fetching field observations from MongoDB: %s", e)

        data = self.load_json_fallback("field_observations.json")
        return pd.DataFrame(data[:limit]) if data else pd.DataFrame()

    def get_agricultural_alerts(self, status: Optional[str] = None) -> pd.DataFrame:
        """Retrieves rule-based agricultural alerts."""
        if self.is_mongo_available():
            try:
                col = get_alerts_collection()
                if col is not None:
                    query = {"status": status} if status else {}
                    docs = list(col.find(query, {"_id": 0}).sort("timestamp", -1))
                    if docs:
                        return pd.DataFrame(docs)
            except Exception as e:
                logger.warning("Error fetching alerts from MongoDB: %s", e)

        data = self.load_json_fallback("agricultural_alerts.json")
        df = pd.DataFrame(data) if data else pd.DataFrame()
        if not df.empty and status:
            df = df[df["status"] == status]
        return df

    def save_agricultural_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Upserts alerts with deduplication based on alert_id or deduplication_key.
        Returns the count of newly inserted alerts.
        """
        if not alerts:
            return 0

        inserted_count = 0
        if self.is_mongo_available():
            try:
                col = get_alerts_collection()
                if col is not None:
                    for alert in alerts:
                        dedup_key = alert.get("dedup_key") or f"{alert.get('farm_id')}_{alert.get('alert_type')}_{alert.get('timestamp')}"
                        result = col.update_one(
                            {"dedup_key": dedup_key},
                            {"$setOnInsert": alert},
                            upsert=True
                        )
                        if result.upserted_id:
                            inserted_count += 1
                    return inserted_count
            except Exception as e:
                logger.warning("Error saving alerts to MongoDB: %s", e)

        # Fallback to in-memory / JSON archive update
        raw_path = self.raw_data_dir / "agricultural_alerts.json"
        existing = self.load_json_fallback("agricultural_alerts.json") or []
        existing_keys = {a.get("dedup_key") or f"{a.get('farm_id')}_{a.get('alert_type')}_{a.get('timestamp')}" for a in existing}
        for alert in alerts:
            k = alert.get("dedup_key") or f"{alert.get('farm_id')}_{alert.get('alert_type')}_{alert.get('timestamp')}"
            if k not in existing_keys:
                existing.append(alert)
                existing_keys.add(k)
                inserted_count += 1
        try:
            import json
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, default=str)
        except Exception as e:
            logger.warning("Could not persist alerts to JSON: %s", e)

        return inserted_count


    def get_sensor_observations(self, limit: int = 500) -> pd.DataFrame:
        """Retrieves IoT sensor observation payloads."""
        if self.is_mongo_available():
            try:
                col = get_sensor_collection()
                if col is not None:
                    docs = list(col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
                    if docs:
                        return pd.DataFrame(docs)
            except Exception as e:
                logger.warning("Error fetching sensors from MongoDB: %s", e)

        data = self.load_json_fallback("sensor_observations.json")
        return pd.DataFrame(data[:limit]) if data else pd.DataFrame()

    def get_activity_logs(self, limit: int = 200) -> pd.DataFrame:
        """Retrieves system activity audit logs."""
        if self.is_mongo_available():
            try:
                col = get_activity_logs_collection()
                if col is not None:
                    docs = list(col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
                    if docs:
                        return pd.DataFrame(docs)
            except Exception as e:
                logger.warning("Error fetching logs from MongoDB: %s", e)

        data = self.load_json_fallback("activity_logs.json")
        return pd.DataFrame(data[:limit]) if data else pd.DataFrame()
