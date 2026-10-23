"""CropCycle SQLAlchemy model."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class CropCycle(Base):
    __tablename__ = "crop_cycles"

    cycle_id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.farm_id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("crops.crop_id", ondelete="RESTRICT"), nullable=False, index=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="RESTRICT"), nullable=False, index=True)
    sowing_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    actual_harvest_date = Column(Date, nullable=True)
    cultivated_area_hectares = Column(Numeric(6, 2), nullable=False)
    status = Column(String(20), nullable=False, default="Active", index=True)  # Planned, Active, Harvested, Failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    farm = relationship("Farm", back_populates="crop_cycles")
    crop = relationship("Crop", back_populates="crop_cycles")
    season = relationship("Season", back_populates="crop_cycles")
    yield_record = relationship("YieldRecord", back_populates="crop_cycle", uselist=False, cascade="all, delete-orphan")
    irrigation_records = relationship("IrrigationRecord", back_populates="crop_cycle")
    fertilizer_records = relationship("FertilizerRecord", back_populates="crop_cycle")

    # Backward compatibility properties
    @property
    def harvest_date(self):
        return self.actual_harvest_date

    @property
    def cultivated_area(self):
        return self.cultivated_area_hectares

    def __repr__(self) -> str:
        return f"<CropCycle(id={self.cycle_id}, farm_id={self.farm_id}, crop_id={self.crop_id}, status='{self.status}')>"

    def to_dict(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "farm_id": self.farm_id,
            "crop_id": self.crop_id,
            "season_id": self.season_id,
            "sowing_date": self.sowing_date.isoformat() if self.sowing_date else None,
            "expected_harvest_date": self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            "actual_harvest_date": self.actual_harvest_date.isoformat() if self.actual_harvest_date else None,
            "harvest_date": self.actual_harvest_date.isoformat() if self.actual_harvest_date else None,
            "cultivated_area_hectares": float(self.cultivated_area_hectares) if self.cultivated_area_hectares is not None else None,
            "cultivated_area": float(self.cultivated_area_hectares) if self.cultivated_area_hectares is not None else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
