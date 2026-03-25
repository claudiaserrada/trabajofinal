from fastapi import FastAPI, Depends
from pydantic import BaseModel as PydanticBaseModel
from typing import List
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import LibroDB, UsuarioDB, PrestamoDB

Base.metadata.create_all(bind=engine)


class Libro(PydanticBaseModel):
    id: int | None = None
    titulo: str
    autor: str
    genero: str
    disponible: bool = True


class ListadoLibros(PydanticBaseModel):
    libros: List[Libro] = []


class Usuario(PydanticBaseModel):
    id: int | None = None
    nombre: str
    email: str


class ListadoUsuarios(PydanticBaseModel):
    usuarios: List[Usuario] = []


class Prestamo(PydanticBaseModel):
    libro_id: int
    usuario_id: int


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


@app.get("/usuarios/")
def get_users(db: Session = Depends(get_db)):
    usuarios_db = db.query(UsuarioDB).all()
    usuarios = [
        {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
        }
        for usuario in usuarios_db
    ]
    return {"usuarios": usuarios}


@app.post("/usuarios/")
def create_user(usuario: Usuario, db: Session = Depends(get_db)):
    existe = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()

    if existe:
        return {"error": "Ese email ya está registrado"}

    nuevo_usuario = UsuarioDB(
        nombre=usuario.nombre,
        email=usuario.email
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario creado correctamente",
        "id": nuevo_usuario.id
    }


@app.post("/prestamos/")
def create_loan(prestamo: Prestamo, db: Session = Depends(get_db)):
    libro = db.query(LibroDB).filter(LibroDB.id == prestamo.libro_id).first()
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == prestamo.usuario_id).first()

    if not libro:
        return {"error": "Libro no encontrado"}

    if not usuario:
        return {"error": "Usuario no encontrado"}

    if not libro.disponible:
        return {"error": "El libro ya está prestado"}

    nuevo_prestamo = PrestamoDB(
        libro_id=prestamo.libro_id,
        usuario_id=prestamo.usuario_id,
        activo=True
    )
    db.add(nuevo_prestamo)

    libro.disponible = False

    db.commit()
    db.refresh(nuevo_prestamo)

    return {
        "mensaje": "Préstamo realizado correctamente",
        "prestamo_id": nuevo_prestamo.id
    }


@app.put("/devoluciones/{libro_id}")
def return_book(libro_id: int, db: Session = Depends(get_db)):
    libro = db.query(LibroDB).filter(LibroDB.id == libro_id).first()

    if not libro:
        return {"error": "Libro no encontrado"}

    if libro.disponible:
        return {"error": "El libro ya está disponible"}

    prestamo_activo = (
        db.query(PrestamoDB)
        .filter(PrestamoDB.libro_id == libro_id, PrestamoDB.activo == True)
        .first()
    )

    if not prestamo_activo:
        return {"error": "No existe un préstamo activo para este libro"}

    prestamo_activo.activo = False
    libro.disponible = True

    db.commit()

    return {"mensaje": "Libro devuelto correctamente"}
