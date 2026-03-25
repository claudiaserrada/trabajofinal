import streamlit as st
import requests

API_URL = "http://fastapi:8000"

st.title("Registrar nuevo libro")

titulo = st.text_input("Título")
autor = st.text_input("Autor")
genero = st.text_input("Género")

if st.button("Guardar libro"):
    if not titulo or not autor or not genero:
        st.error("Todos los campos son obligatorios")
    else:
        nuevo_libro = {
            "id": 0,
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "disponible": True
        }

        try:
            response = requests.post(f"{API_URL}/libros/", json=nuevo_libro)

            if response.status_code == 200:
                st.success("Libro guardado correctamente")
            else:
                st.error("Error al guardar el libro")

        except Exception as e:
            st.error(f"Error de conexión: {e}")
