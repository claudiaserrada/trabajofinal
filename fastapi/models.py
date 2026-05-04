from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from database import Base


class LibroDB(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    genero = Column(String, nullable=False)
    disponible = Column(Boolean, default=True)


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


class PrestamoDB(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    
    activo = Column(Boolean, default=True)

    fecha_prestamo = Column(Date, nullable=False)
    fecha_devolucion = Column(Date, nullable=True)
