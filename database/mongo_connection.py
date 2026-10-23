"""
AgriSense - MongoDB Database Connection Module
Provides PyMongo client management, collection handles, index configuration, and health checks.
"""
import logging
from typing import Tuple, Optional, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError

from config.settings import settings

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None


def get_mongo_client() -> Optional[MongoClient]:
    """Initializes and returns a cached MongoClient instance with timeout protection."""
    global _mongo_client
    if _mongo_client is None:
        try:
            # 2000ms timeout prevents application freeze if MongoDB is unavailable
            _mongo_client = MongoClient(
                settings.mongo.uri,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
            )
        except Exception as e:
            logger.error("Failed to initialize MongoClient: %s", e)
            _mongo_client = None
    return _mongo_client


def get_mongo_db() -> Optional[Database]:
    """Returns the AgriSense NoSQL database instance."""
    client = get_mongo_client()
    if client is not None:
        try:
            return client[settings.mongo.database]
        except Exception as e:
            logger.error("Error accessing MongoDB database %s: %s", settings.mongo.database, e)
    return None


def get_collection(collection_name: str) -> Optional[Collection]:
    """Safe accessor for a MongoDB collection."""
    db = get_mongo_db()
    if db is not None:
        return db[collection_name]
    return None


# Explicit collection accessors
def get_weather_collection() -> Optional[Collection]:
    return get_collection("weather_observations")


def get_field_observations_collection() -> Optional[Collection]:
    return get_collection("field_observations")


def get_alerts_collection() -> Optional[Collection]:
    return get_collection("agricultural_alerts")


def get_sensor_collection() -> Optional[Collection]:
    return get_collection("sensor_observations")


def get_activity_logs_collection() -> Optional[Collection]:
    return get_collection("activity_logs")


def check_mongo_connection() -> Tuple[bool, str]:
    """
    Performs an admin ping command to verify MongoDB connectivity.
    Returns (status: bool, message: str).
    """
    if not settings.mongo.is_configured:
        return False, "MongoDB settings are not configured in .env (MONGO_URI or MONGO_DATABASE missing)."

    try:
        client = get_mongo_client()
        if client is None:
            return False, "Failed to initialize MongoDB client instance."

        # The ping command is cheap and does not require auth on the admin db in standard setups
        client.admin.command("ping")
        return True, f"Connected to MongoDB successfully at {settings.mongo.uri} (Database: {settings.mongo.database})"
    except (ConnectionFailure, ServerSelectionTimeoutError) as ce:
        logger.warning("MongoDB connection timeout/failure: %s", ce)
        return False, f"MongoDB connection failed: Server unavailable at {settings.mongo.uri}. ({str(ce)})"
    except PyMongoError as pe:
        logger.warning("PyMongo operational error: %s", pe)
        return False, f"MongoDB error: {str(pe)}"
    except Exception as exc:
        logger.warning("MongoDB unexpected error: %s", exc)
        return False, f"MongoDB connection error: {str(exc)}"


def init_mongo_indexes() -> Tuple[bool, str]:
    """
    Creates necessary query optimization indexes for semi-structured collections.
    Indexes fields requested in Prompt 2: farm_id, date, alert status, alert severity.
    """
    db = get_mongo_db()
    if db is None:
        return False, "Cannot initialize indexes: MongoDB is not connected."

    try:
        # Weather observations: index on farm_id, date, district
        weather = db["weather_observations"]
        weather.create_index([("farm_id", 1), ("date", -1)])
        weather.create_index([("date", -1)])
        weather.create_index([("district", 1)])

        # Field observations: index on farm_id, crop_id, date, observation_type
        field_obs = db["field_observations"]
        field_obs.create_index([("farm_id", 1), ("date", -1)])
        field_obs.create_index([("crop_id", 1)])
        field_obs.create_index([("observation_type", 1)])

        # Agricultural alerts: index on farm_id, status, severity, created_at
        alerts = db["agricultural_alerts"]
        alerts.create_index([("farm_id", 1), ("status", 1)])
        alerts.create_index([("status", 1)])
        alerts.create_index([("severity", 1)])
        alerts.create_index([("created_at", -1)])

        # Activity logs: index on action and timestamp
        logs = db["activity_logs"]
        logs.create_index([("action", 1)])
        logs.create_index([("timestamp", -1)])

        logger.info("MongoDB indexes verified/created.")
        return True, "MongoDB collection indexes configured successfully."
    except Exception as e:
        logger.error("Failed to initialize MongoDB indexes: %s", e)
        return False, f"Error configuring MongoDB indexes: {str(e)}"
