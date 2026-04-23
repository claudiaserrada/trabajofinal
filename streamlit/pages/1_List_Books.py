import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Catálogo de Libros", page_icon="📖")

st.markdown("# Catálogo de Libros")
st.write("Listado de libros disponibles en la biblioteca.")

API_URL = "http://fastapi:8000"

busqueda = st.text_input("🔍 Buscar por título o autor", "")

try:
    response = requests.get(f"{API_URL}/libros")
    if response.status_code == 200:
        data = response.json()
        libros = data.get("libros", [])

        if libros:
            df = pd.DataFrame(libros)

            if busqueda.strip():
                filtro = busqueda.strip().lower()
                df = df[
                    df["titulo"].str.lower().str.contains(filtro) |
                    df["autor"].str.lower().str.contains(filtro)
                ]

            if not df.empty:
                st.dataframe(df)
            else:
                st.warning("No se encontraron libros con esa búsqueda.")
        else:
            st.warning("No hay libros disponibles.")
    else:
        st.error(f"Error al obtener libros: {response.status_code}")
except Exception as e:
    st.error(f"Error de conexión con el servidor: {e}")
    st.info("Asegúrate de que el contenedor 'fastapi' está corriendo.")
