from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Jugador(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, index=True)
    id_api = Column(Integer, unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    seleccion_id = Column(Integer, ForeignKey("selecciones.id"), nullable=False)
    posicion = Column(String(50), nullable=True)
    numero_camiseta = Column(Integer, nullable=True)
    edad = Column(Integer, nullable=True)
    foto_url = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True)

    seleccion = relationship("Seleccion", back_populates="jugadores")
    laminas = relationship("LaminaAlbum", back_populates="jugador")
    publicaciones = relationship("Publicacion", back_populates="jugador")