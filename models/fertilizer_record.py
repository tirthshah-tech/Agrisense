"""FertilizerRecord SQLAlchemy model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class FertilizerRecord(Base):
    __tablename__ = "fertilizer_records"

    fertilizer_id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.farm_id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("crops.crop_id", ondelete="RESTRICT"), nullable=False, index=True)
    cycle_id = Column(Integer, ForeignKey("crop_cycles.cycle_id", ondelete="SET NULL"), nullable=True, index=True)
    date = Column(Date, nullable=False, index=True)
    fertilizer_type = Column(String(60), nullable=False)  # Urea, DAP, NPK 10:26:26, MOP, etc.
    quantity_kg = Column(Numeric(8, 2), nullable=False)
    application_method = Column(String(50), nullable=True)  # Broadcast, Fertigation, Basal, Foliar
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farm = relationship("Farm", back_populates="fertilizer_records")
    crop = relationship("Crop", back_populates="fertilizer_records")
    crop_cycle = relationship("CropCycle", back_populates="fertilizer_records")

    def __repr__(self) -> str:
        return f"<FertilizerRecord(id={self.fertilizer_id}, farm_id={self.farm_id}, type='{self.fertilizer_type}', qty={self.quantity_kg}kg)>"

    def to_dict(self) -> dict:
        return {
            "fertilizer_id": self.fertilizer_id,
            "farm_id": self.farm_id,
            "crop_id": self.crop_id,
            "cycle_id": self.cycle_id,
            "date": self.date.isoformat() if self.date else None,
            "fertilizer_type": self.fertilizer_type,
            "quantity_kg": float(self.quantity_kg) if self.quantity_kg is not None else None,
            "application_method": self.application_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
