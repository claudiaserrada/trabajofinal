from fastapi import FastAPI, Depends
from pydantic import BaseModel as PydanticBaseModel
from typing import List
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import LibroDB

Base.metadata.create_all(bind=engine)

class Libro(PydanticBaseModel):
    id: int | None = None
    titulo: str
    autor: str
    genero: str
    disponible: bool = True

class ListadoLibros(PydanticBaseModel):
    libros: List[Libro] = []

app = FastAPI(
    title="Gestor de Bibliotecas API",
    description="Servidor de datos para la gestión de bibliotecas.",
    version="1.0.0",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/libros/")
def retrieve_data(db: Session = Depends(get_db)):
    libros_db = db.query(LibroDB).all()
    libros = [
        {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "genero": libro.genero,
            "disponible": libro.disponible,
        }
        for libro in libros_db
    ]
    return {"libros": libros}

@app.post("/libros/")
def create_book(libro: Libro, db: Session = Depends(get_db)):
    nuevo_libro = LibroDB(
        titulo=libro.titulo,
        autor=libro.autor,
        genero=libro.genero,
        disponible=True
    )
    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)

    return {
        "mensaje": "Libro añadido correctamente",
        "id": nuevo_libro.id
    }

@app.post("/prestamos/")
async def create_loan(libro_id: int):
    return {"message": "Préstamo creado (no realmente)", "libro_id": libro_id}
