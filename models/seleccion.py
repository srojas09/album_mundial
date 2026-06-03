from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Seleccion(Base):
    __tablename__ = "selecciones"

    id = Column(Integer, primary_key=True, index=True)
    id_api = Column(Integer, unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    pais = Column(String(100), nullable=False)
    grupo = Column(String(10), nullable=True)
    logo_url = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True)

    jugadores = relationship("Jugador", back_populates="seleccion")