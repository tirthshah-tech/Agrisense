"""SoilRecord SQLAlchemy model."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class SoilRecord(Base):
    __tablename__ = "soil_records"

    soil_record_id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.farm_id", ondelete="CASCADE"), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    ph = Column(Numeric(3, 1), nullable=False)
    nitrogen = Column(Numeric(6, 2), nullable=False, comment="Available Nitrogen kg/ha")
    phosphorus = Column(Numeric(6, 2), nullable=False, comment="Available Phosphorus kg/ha")
    potassium = Column(Numeric(6, 2), nullable=False, comment="Available Potassium kg/ha")
    moisture_percentage = Column(Numeric(5, 2), nullable=False, comment="Moisture percentage 0-100")
    organic_carbon = Column(Numeric(4, 2), nullable=True, comment="Organic Carbon percentage")
    electrical_conductivity = Column(Numeric(5, 2), nullable=True, comment="EC in dS/m")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    farm = relationship("Farm", back_populates="soil_records")

    # Backward compatibility property
    @property
    def moisture(self):
        return self.moisture_percentage

    def __repr__(self) -> str:
        return f"<SoilRecord(id={self.soil_record_id}, farm_id={self.farm_id}, date={self.record_date}, pH={self.ph})>"

    def to_dict(self) -> dict:
        return {
            "soil_record_id": self.soil_record_id,
            "farm_id": self.farm_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "ph": float(self.ph) if self.ph is not None else None,
            "nitrogen": float(self.nitrogen) if self.nitrogen is not None else None,
            "phosphorus": float(self.phosphorus) if self.phosphorus is not None else None,
            "potassium": float(self.potassium) if self.potassium is not None else None,
            "moisture_percentage": float(self.moisture_percentage) if self.moisture_percentage is not None else None,
            "moisture": float(self.moisture_percentage) if self.moisture_percentage is not None else None,
            "organic_carbon": float(self.organic_carbon) if self.organic_carbon is not None else None,
            "electrical_conductivity": float(self.electrical_conductivity) if self.electrical_conductivity is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
