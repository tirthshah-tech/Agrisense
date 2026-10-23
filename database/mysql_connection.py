"""
AgriSense - MySQL Database Connection Module
Provides SQLAlchemy engine, connection pooling, session lifecycle management, and health checks.
"""
import logging
from typing import Generator, Tuple, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from config.settings import settings

logger = logging.getLogger(__name__)

# Global engine and session factory caches
_engine = None
_SessionFactory = None


def get_mysql_engine():
    """Initializes and returns a cached SQLAlchemy engine with connection pooling."""
    global _engine
    if _engine is None:
        try:
            connection_url = settings.mysql.connection_url
            _engine = create_engine(
                connection_url,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
                pool_pre_ping=True,
                echo=False,
            )
            logger.info("SQLAlchemy MySQL engine initialized.")
        except Exception as e:
            logger.error("Failed to initialize MySQL engine: %s", e)
            _engine = None
    return _engine


def get_session_factory():
    """Returns the cached SQLAlchemy sessionmaker."""
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_mysql_engine()
        if engine:
            _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionFactory


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager providing a transactional SQLAlchemy session.
    Automatically commits on success or rolls back on exception.
    """
    factory = get_session_factory()
    if factory is None:
        raise ConnectionError(
            "MySQL database session could not be established. "
            "Please verify that MySQL service is running and credentials in .env are correct."
        )

    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("Database transaction rolled back due to error: %s", e)
        raise
    finally:
        session.close()


def check_mysql_connection() -> Tuple[bool, str]:
    """
    Performs a lightweight probe to test MySQL connectivity.
    Returns (status: bool, message: str).
    """
    if not settings.mysql.is_configured:
        return False, "MySQL credentials are not configured in .env (host, user, password, or database missing)."

    try:
        engine = get_mysql_engine()
        if engine is None:
            return False, "Failed to initialize SQLAlchemy MySQL engine."

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS probe"))
            val = result.scalar()
            if val == 1:
                return True, f"Connected to MySQL successfully at {settings.mysql.host}:{settings.mysql.port}/{settings.mysql.database}"
            return False, "Unexpected response from MySQL probe query."
    except OperationalError as oe:
        logger.warning("MySQL connection operational error: %s", oe)
        return False, f"MySQL connection failed: Unable to connect to {settings.mysql.host}:{settings.mysql.port}. ({oe.orig if hasattr(oe, 'orig') else oe})"
    except SQLAlchemyError as se:
        logger.warning("MySQL connection SQLAlchemy error: %s", se)
        return False, f"MySQL database error: {str(se)}"
    except Exception as exc:
        logger.warning("MySQL unexpected connection error: %s", exc)
        return False, f"MySQL connection error: {str(exc)}"


def init_mysql_tables() -> Tuple[bool, str]:
    """
    Creates all MySQL tables defined in models if connected.
    """
    from models.base import Base

    engine = get_mysql_engine()
    if engine is None:
        return False, "Cannot initialize tables: MySQL engine is unavailable."

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("All MySQL relational tables verified/created.")
        return True, "Relational tables created/verified successfully."
    except Exception as e:
        logger.error("Failed to initialize MySQL tables: %s", e)
        return False, f"Error creating tables: {str(e)}"
