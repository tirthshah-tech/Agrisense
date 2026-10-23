"""IrrigationRecord SQLAlchemy model."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class IrrigationRecord(Base):
    __tablename__ = "irrigation_records"

    irrigation_id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.farm_id", ondelete="CASCADE"), nullable=False, index=True)
    cycle_id = Column(Integer, ForeignKey("crop_cycles.cycle_id", ondelete="SET NULL"), nullable=True, index=True)
    date = Column(Date, nullable=False, index=True)
    water_used_liters = Column(Numeric(10, 2), nullable=False)
    irrigation_method = Column(String(50), nullable=False)  # Drip, Sprinkler, Canal Flood, Tube Well
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    farm = relationship("Farm", back_populates="irrigation_records")
    crop_cycle = relationship("CropCycle", back_populates="irrigation_records")

    # Backward compatibility property
    @property
    def duration_hours(self):
        return round(self.duration_minutes / 60.0, 2) if self.duration_minutes is not None else None

    def __repr__(self) -> str:
        return f"<IrrigationRecord(id={self.irrigation_id}, farm_id={self.farm_id}, liters={self.water_used_liters})>"

    def to_dict(self) -> dict:
        return {
            "irrigation_id": self.irrigation_id,
            "farm_id": self.farm_id,
            "cycle_id": self.cycle_id,
            "date": self.date.isoformat() if self.date else None,
            "water_used_liters": float(self.water_used_liters) if self.water_used_liters is not None else None,
            "irrigation_method": self.irrigation_method,
            "duration_minutes": self.duration_minutes,
            "duration_hours": self.duration_hours,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
