import streamlit as st
import requests

API_URL = "http://fastapi:8000"

st.title("Registrar préstamo")

try:
    libros_response = requests.get(f"{API_URL}/libros/")
    usuarios_response = requests.get(f"{API_URL}/usuarios/")

    libros = libros_response.json().get("libros", [])
    usuarios = usuarios_response.json().get("usuarios", [])

    libros_disponibles = [libro for libro in libros if libro["disponible"]]

    if not libros_disponibles:
        st.info("No hay libros disponibles para préstamo.")
    elif not usuarios:
        st.info("No hay usuarios registrados.")
    else:
        libro_opciones = {
            f'{libro["id"]} - {libro["titulo"]}': libro["id"]
            for libro in libros_disponibles
        }

        usuario_opciones = {
            f'{usuario["id"]} - {usuario["nombre"]} ({usuario["email"]})': usuario["id"]
            for usuario in usuarios
        }

        libro_seleccionado = st.selectbox("Selecciona un libro", list(libro_opciones.keys()))
        usuario_seleccionado = st.selectbox("Selecciona un usuario", list(usuario_opciones.keys()))

        if st.button("Registrar préstamo"):
            payload = {
                "libro_id": libro_opciones[libro_seleccionado],
                "usuario_id": usuario_opciones[usuario_seleccionado]
            }

            response = requests.post(f"{API_URL}/prestamos/", json=payload)
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.success("Préstamo realizado correctamente")

except Exception as e:
    st.error(f"Error de conexión: {e}")
