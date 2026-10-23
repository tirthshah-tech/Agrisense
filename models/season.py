"""Season SQLAlchemy model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base


class Season(Base):
    __tablename__ = "seasons"

    season_id = Column(Integer, primary_key=True, autoincrement=True)
    season_name = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("season_name", "year", name="uq_season_year"),
    )

    # Relationships
    crop_cycles = relationship("CropCycle", back_populates="season")

    def __repr__(self) -> str:
        return f"<Season(id={self.season_id}, name='{self.season_name} {self.year}')>"

    def to_dict(self) -> dict:
        return {
            "season_id": self.season_id,
            "season_name": self.season_name,
            "year": self.year,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
