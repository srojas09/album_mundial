from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Publicacion(Base):
    __tablename__ = "publicaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    jugador_id = Column(Integer, ForeignKey("jugadores.id"), nullable=False)
    precio = Column(Float, nullable=False)
    descripcion = Column(String(300), nullable=True)
    estado = Column(String(20), default="disponible")  # disponible, vendida, cancelada
    fecha_publicacion = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="publicaciones")
    jugador = relationship("Jugador", back_populates="publicaciones")