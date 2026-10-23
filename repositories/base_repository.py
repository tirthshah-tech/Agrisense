"""
AgriSense - Base Repository Module
Provides unified data access with intelligent fallback:
Queries live MySQL/MongoDB when available, and gracefully falls back to sanitized
local data archives (data/raw/*.csv, *.json) if database connections are not configured.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from config.settings import settings
from database.mysql_connection import get_db_session, check_mysql_connection
from database.mongo_connection import get_mongo_db, check_mongo_connection

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base class for data access across AgriSense services."""

    def __init__(self):
        self.raw_dir = settings.paths.raw_data_dir

    def is_mysql_available(self) -> bool:
        """Returns True if MySQL is reachable."""
        ok, _ = check_mysql_connection()
        return ok

    def is_mongo_available(self) -> bool:
        """Returns True if MongoDB is reachable."""
        ok, _ = check_mongo_connection()
        return ok

    def load_csv_fallback(self, filename: str) -> pd.DataFrame:
        """Loads a dataset from the local CSV archive."""
        file_path = self.raw_dir / filename
        if not file_path.exists():
            logger.warning("Local fallback CSV %s not found.", file_path)
            return pd.DataFrame()
        return pd.read_csv(file_path)

    def load_json_fallback(self, filename: str) -> List[Dict[str, Any]]:
        """Loads a dataset from the local JSON archive."""
        file_path = self.raw_dir / filename
        if not file_path.exists():
            logger.warning("Local fallback JSON %s not found.", file_path)
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
