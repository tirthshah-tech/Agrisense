"""Farm SQLAlchemy model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Farm(Base):
    __tablename__ = "farms"

    farm_id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False, index=True)
    farm_name = Column(String(120), nullable=False)
    area_hectares = Column(Numeric(6, 2), nullable=False)
    soil_type = Column(String(60), nullable=False, index=True)
    irrigation_type = Column(String(60), nullable=False, index=True)
    location = Column(String(150), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer = relationship("Farmer", back_populates="farms")
    crop_cycles = relationship("CropCycle", back_populates="farm", cascade="all, delete-orphan")
    soil_records = relationship("SoilRecord", back_populates="farm", cascade="all, delete-orphan")
    irrigation_records = relationship("IrrigationRecord", back_populates="farm", cascade="all, delete-orphan")
    fertilizer_records = relationship("FertilizerRecord", back_populates="farm", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Farm(id={self.farm_id}, name='{self.farm_name}', area={self.area_hectares}ha)>"

    def to_dict(self) -> dict:
        return {
            "farm_id": self.farm_id,
            "farmer_id": self.farmer_id,
            "farm_name": self.farm_name,
            "area_hectares": float(self.area_hectares) if self.area_hectares is not None else None,
            "soil_type": self.soil_type,
            "irrigation_type": self.irrigation_type,
            "location": self.location,
            "latitude": float(self.latitude) if self.latitude is not None else None,
            "longitude": float(self.longitude) if self.longitude is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
