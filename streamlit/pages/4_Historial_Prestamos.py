import streamlit as st
import requests

st.set_page_config(page_title="Historial de Préstamos", page_icon="📋")

st.markdown("# 📋 Historial de Préstamos por Usuario")
st.write("Consulta todos los préstamos activos y pasados de un usuario.")

API_URL = "http://fastapi:8000"

usuario_id = st.number_input("ID del Usuario", min_value=1, step=1)

if st.button("Consultar historial"):
    try:
        response = requests.get(f"{API_URL}/usuarios/{usuario_id}/prestamos")

        if response.status_code == 200:
            data = response.json()
            nombre = data.get("usuario_nombre", "")
            historial = data.get("historial", [])

            st.markdown(f"### Usuario: {nombre}")

            if historial:
                for p in historial:
                    if p["activo"]:
                        estado = "🟢 Activo"
                        color = "🟢"
                    else:
                        estado = "✅ Devuelto"
                        color = "✅"

                    with st.expander(f"{color} {p['libro']}"):
                        st.write(f"**Fecha de préstamo:** {p['fecha_prestamo']}")
                        if p["activo"]:
                            st.warning("Pendiente de devolución")
                        else:
                            st.write(f"**Fecha de devolución:** {p['fecha_devolucion']}")
            else:
                st.info("Este usuario no tiene historial de préstamos.")

        elif response.status_code == 404:
            st.error("Usuario no encontrado.")
        else:
            st.error(f"Error del servidor: {response.status_code}")

    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("Asegúrate de que el contenedor 'fastapi' está corriendo.")

