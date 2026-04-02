from fastapi import FastAPI, Depends, HTTPException
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


class Devolucion(PydanticBaseModel):
    libro_id: int
    usuario_id: int


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def inicio():
    return {"mensaje": "API biblioteca funcionando"}


@app.get("/libros", response_model=ListadoLibros)
def listar_libros(db: Session = Depends(get_db)):
    libros_db = db.query(LibroDB).all()

    return ListadoLibros(
        libros=[
            Libro(
                id=libro.id,
                titulo=libro.titulo,
                autor=libro.autor,
                genero=libro.genero,
                disponible=libro.disponible
            )
            for libro in libros_db
        ]
    )


@app.post("/libros")
def crear_libro(libro: Libro, db: Session = Depends(get_db)):
    if not libro.titulo.strip() or not libro.autor.strip() or not libro.genero.strip():
        raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")

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


@app.get("/usuarios", response_model=ListadoUsuarios)
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios_db = db.query(UsuarioDB).all()

    return ListadoUsuarios(
        usuarios=[
            Usuario(
                id=usuario.id,
                nombre=usuario.nombre,
                email=usuario.email
            )
            for usuario in usuarios_db
        ]
    )


@app.post("/usuarios")
def crear_usuario(usuario: Usuario, db: Session = Depends(get_db)):
    if not usuario.nombre.strip() or not usuario.email.strip():
        raise HTTPException(status_code=400, detail="Nombre y email son obligatorios")

    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

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


@app.post("/prestamos")
def realizar_prestamo(prestamo: Prestamo, db: Session = Depends(get_db)):
    libro = db.query(LibroDB).filter(LibroDB.id == prestamo.libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="El libro no existe")

    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == prestamo.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario no existe")

    if not libro.disponible:
        raise HTTPException(status_code=400, detail="El libro ya está prestado")

    nuevo_prestamo = PrestamoDB(
        libro_id=prestamo.libro_id,
        usuario_id=prestamo.usuario_id,
        devuelto=False
    )

    libro.disponible = False

    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)

    return {
        "mensaje": "Préstamo realizado correctamente",
        "id": nuevo_prestamo.id
    }


@app.put("/devoluciones")
def devolver_libro(devolucion: Devolucion, db: Session = Depends(get_db)):
def devolver_libro(devolucion: Devolucion, db: Session = Depends(get_db)):
    prestamo_activo = db.query(PrestamoDB).filter(
        PrestamoDB.libro_id == devolucion.libro_id,
        PrestamoDB.usuario_id == devolucion.usuario_id,
        PrestamoDB.devuelto == False
    ).first()

    if not prestamo_activo:
        raise HTTPException(status_code=404, detail="No hay préstamo activo")

    libro = db.query(LibroDB).filter(LibroDB.id == devolucion.libro_id).first()

    prestamo_activo.devuelto = True
    libro.disponible = True

    # Fuerza la sesión
    db.add(prestamo_activo)
    db.add(libro)

    try:
        db.commit()
        db.refresh(libro)  # Esto obliga a SQLAlchemy a volver a leer de la DB
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    return {"mensaje": "Devolución registrada", "libro_estado": libro.disponible}
