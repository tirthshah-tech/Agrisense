"""Crop SQLAlchemy model."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from models.base import Base


class Crop(Base):
    __tablename__ = "crops"

    crop_id = Column(Integer, primary_key=True, autoincrement=True)
    crop_name = Column(String(80), nullable=False, unique=True, index=True)
    crop_category = Column(String(50), nullable=False, index=True)
    ideal_season = Column(String(50), nullable=False, index=True)
    ideal_soil_type = Column(String(60), nullable=False)
    typical_growth_days = Column(Integer, nullable=False, default=120)
    water_requirement_mm = Column(Numeric(7, 2), nullable=True)
    standard_yield_kg_per_ha = Column(Numeric(8, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    crop_cycles = relationship("CropCycle", back_populates="crop")
    fertilizer_records = relationship("FertilizerRecord", back_populates="crop")

    def __repr__(self) -> str:
        return f"<Crop(id={self.crop_id}, name='{self.crop_name}', category='{self.crop_category}')>"

    def to_dict(self) -> dict:
        return {
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "crop_category": self.crop_category,
            "ideal_season": self.ideal_season,
            "ideal_soil_type": self.ideal_soil_type,
            "typical_growth_days": self.typical_growth_days,
            "water_requirement_mm": float(self.water_requirement_mm) if self.water_requirement_mm is not None else None,
            "standard_yield_kg_per_ha": float(self.standard_yield_kg_per_ha) if self.standard_yield_kg_per_ha is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
