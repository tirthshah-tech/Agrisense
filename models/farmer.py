"""Farmer SQLAlchemy model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from models.base import Base


class Farmer(Base):
    __tablename__ = "farmers"

    farmer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False, unique=True, index=True)
    village = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, default="Maharashtra")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Farmer(id={self.farmer_id}, name='{self.name}', district='{self.district}')>"

    def to_dict(self) -> dict:
        return {
            "farmer_id": self.farmer_id,
            "name": self.name,
            "phone": self.phone,
            "village": self.village,
            "district": self.district,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
