"""
AgriSense - Application Configuration Module
Centralized configuration management with environment variable loading and validation.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Base Directory Resolution
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()  # Fallback to default environment lookup


@dataclass(frozen=True)
class DatabaseSettings:
    """Relational Database (MySQL) configuration settings."""
    host: str = os.getenv("MYSQL_HOST", "localhost")
    port: int = int(os.getenv("MYSQL_PORT", "3306"))
    user: str = os.getenv("MYSQL_USER", "root")
    password: str = os.getenv("MYSQL_PASSWORD", "")
    database: str = os.getenv("MYSQL_DATABASE", "agrisense_db")

    @property
    def is_configured(self) -> bool:
        """Returns True if MySQL credentials appear minimally configured."""
        return bool(self.host and self.user and self.database and self.password)

    @property
    def connection_url(self) -> str:
        """Constructs a standard SQLAlchemy connection URL for MySQL."""
        # Using PyMySQL driver with utf8mb4 encoding
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"


@dataclass(frozen=True)
class MongoSettings:
    """NoSQL Database (MongoDB) configuration settings."""
    uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    database: str = os.getenv("MONGO_DATABASE", "agrisense_nosql")

    @property
    def is_configured(self) -> bool:
        """Returns True if MongoDB URI and Database name are provided."""
        return bool(self.uri and self.database)


@dataclass(frozen=True)
class PathSettings:
    """Filesystem path configuration for data and assets."""
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    raw_data_dir: Path = BASE_DIR / "data" / "raw"
    processed_data_dir: Path = BASE_DIR / "data" / "processed"
    assets_dir: Path = BASE_DIR / "assets"
    css_path: Path = BASE_DIR / "assets" / "style.css"


@dataclass(frozen=True)
class AppSettings:
    """Global Application configuration."""
    app_name: str = "AgriSense"
    app_tagline: str = "Data-Driven Crop Monitoring & Agricultural Analytics Platform"
    app_env: str = os.getenv("APP_ENV", "development")
    app_debug: bool = os.getenv("APP_DEBUG", "true").lower() in ("true", "1", "yes")
    allow_local_fallback: bool = os.getenv("ALLOW_LOCAL_FALLBACK", "true").lower() in ("true", "1", "yes")

    mysql: DatabaseSettings = DatabaseSettings()
    mongo: MongoSettings = MongoSettings()
    paths: PathSettings = PathSettings()

    def ensure_directories(self) -> None:
        """Ensure all runtime directories exist."""
        self.paths.data_dir.mkdir(parents=True, exist_ok=True)
        self.paths.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.paths.processed_data_dir.mkdir(parents=True, exist_ok=True)
        self.paths.assets_dir.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = AppSettings()
settings.ensure_directories()
