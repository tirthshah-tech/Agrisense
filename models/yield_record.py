"""YieldRecord SQLAlchemy model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class YieldRecord(Base):
    __tablename__ = "yield_records"

    yield_id = Column(Integer, primary_key=True, autoincrement=True)
    cycle_id = Column(Integer, ForeignKey("crop_cycles.cycle_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    harvest_date = Column(Date, nullable=False, index=True)
    yield_kg = Column(Numeric(10, 2), nullable=False)
    yield_per_hectare = Column(Numeric(8, 2), nullable=False)
    quality_grade = Column(String(20), nullable=True)  # Grade A, Grade B, Standard, Export
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    crop_cycle = relationship("CropCycle", back_populates="yield_record")

    def __repr__(self) -> str:
        return f"<YieldRecord(id={self.yield_id}, cycle_id={self.cycle_id}, yield_kg={self.yield_kg})>"

    def to_dict(self) -> dict:
        return {
            "yield_id": self.yield_id,
            "cycle_id": self.cycle_id,
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "yield_kg": float(self.yield_kg) if self.yield_kg is not None else None,
            "yield_per_hectare": float(self.yield_per_hectare) if self.yield_per_hectare is not None else None,
            "quality_grade": self.quality_grade,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
