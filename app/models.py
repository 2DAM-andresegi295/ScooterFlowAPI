from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ScooterStatus(enum.Enum):
    disponible = "disponible"
    en_uso = "en_uso"
    mantenimiento = "mantenimiento"
    sin_bateria = "sin_bateria"

class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    codigo_postal = Column(String, nullable=False)
    limite_velocidad = Column(Integer, nullable=False)
    scooters = relationship("Scooter", back_populates="zona")

class Scooter(Base):
    __tablename__ = "scooters"
    id = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(String, unique=True, nullable=False)
    modelo = Column(String, nullable=False)
    bateria = Column(Integer, nullable=False)
    estado = Column(Enum(ScooterStatus), nullable=False)
    zona_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    zona = relationship("Zone", back_populates="scooters")
    puntuacion_usuario = Column(Float, nullable=True)

