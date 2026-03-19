from fastapi import FastAPI
import pandas as pd
from typing import List
from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True

class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    genero: str
    disponible: bool

class ListadoLibros(BaseModel):
    libros: List[Libro] = []

app = FastAPI(
    title="Gestor de Bibliotecas API",
    description="Servidor de datos para la gestión de bibliotecas.",
    version="1.0.0",
)

@app.get("/libros/")
def retrieve_data():
    # EDUCATIONAL INEFFICIENCY: Reading CSV on every request
    # Students should optimize this by using a database or caching
    try:
        todosmisdatos = pd.read_csv('./books.csv', sep=';')
        todosmisdatos = todosmisdatos.fillna(0)
        todosmisdatosdict = todosmisdatos.to_dict(orient='records')
        listado = ListadoLibros()
        listado.libros = todosmisdatosdict
        return listado
    except Exception as e:
        return {"error": str(e)}
@app.post("/libros/")
def create_book(libro: Libro):
    try:
        df = pd.read_csv('./books.csv', sep=';')

        if not df.empty:
            new_id = int(df["id"].max()) + 1
        else:
            new_id = 1

        nuevo_libro = {
            "id": new_id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "genero": libro.genero,
            "disponible": True
        }

        df = pd.concat([df, pd.DataFrame([nuevo_libro])], ignore_index=True)
        df.to_csv('./books.csv', sep=';', index=False)

        return {"mensaje": "Libro añadido correctamente"}

    except Exception as e:
        return {"error": str(e)}
@app.post("/prestamos/")
async def create_loan(libro_id: int):
    # This is a stub for students to implement
    return {"message": "Préstamo creado (no realmente)", "libro_id": libro_id}
