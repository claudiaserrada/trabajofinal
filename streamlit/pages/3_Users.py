import streamlit as st
import requests
import pandas as pd

API_URL = "http://fastapi:8000"

st.title("Gestión de usuarios")

st.subheader("Registrar usuario")

nombre = st.text_input("Nombre")
email = st.text_input("Email")

if st.button("Guardar usuario"):
    if not nombre or not email:
        st.error("Todos los campos son obligatorios")
    else:
        nuevo_usuario = {
            "nombre": nombre,
            "email": email
        }

        try:
            response = requests.post(f"{API_URL}/usuarios/", json=nuevo_usuario)
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.success("Usuario guardado correctamente")

        except Exception as e:
            st.error(f"Error de conexión: {e}")

st.subheader("Listado de usuarios")

try:
    response = requests.get(f"{API_URL}/usuarios/")
    data = response.json()
    usuarios = data.get("usuarios", [])

    if usuarios:
        df = pd.DataFrame(usuarios)
        st.dataframe(df)
    else:
        st.info("No hay usuarios registrados.")

except Exception as e:
    st.error(f"Error al cargar usuarios: {e}")
