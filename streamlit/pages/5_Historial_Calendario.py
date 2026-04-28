import streamlit as st
import requests
from streamlit_calendar import calendar

st.set_page_config(
    page_title="Historial en Calendario",
    layout="wide",
    page_icon="📅"
)

st.title("📅 Historial de Préstamos en Calendario")
st.markdown("Visualiza los préstamos de un usuario en un calendario interactivo.")

# ── Selector de usuario ──────────────────────────────────────────────────────
usuario_id = st.number_input(
    "Introduce el ID del usuario",
    min_value=1,
    max_value=9999,
    value=1,
    step=1
)

# ── Leyenda ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
col1.markdown("🟢 **Préstamo activo** (aún no devuelto)")
col2.markdown("🔘 **Préstamo devuelto**")

st.divider()

# ── Botón para cargar el historial ──────────────────────────────────────────
if st.button("🔍 Ver historial en calendario", use_container_width=True):
    try:
        response = requests.get(
            f"http://fastapi:8000/usuarios/{usuario_id}/prestamos",
            timeout=5
        )

        if response.status_code == 404:
            st.warning("Usuario no encontrado. Comprueba el ID introducido.")

        elif response.status_code != 200:
            st.error(f"Error del servidor: {response.status_code}")

        else:
            data = response.json()
            historial = data.get("historial", [])
            nombre_usuario = data.get("usuario_nombre", f"Usuario {usuario_id}")

            if not historial:
                st.info(f"El usuario **{nombre_usuario}** no tiene préstamos registrados.")

            else:
                # ── Construir eventos para el calendario ─────────────────────
                eventos = []
                for p in historial:
                    activo = p.get("activo", False)
                    fecha_inicio = p.get("fecha_prestamo", "")
                    fecha_fin = p.get("fecha_devolucion") or fecha_inicio
                    titulo_libro = p.get("libro", "Libro desconocido")

                    # Verde para activos, gris para devueltos
                    color = "#27ae60" if activo else "#7f8c8d"

                    eventos.append({
                        "title": titulo_libro,
                        "start": fecha_inicio,
                        "end": fecha_fin,
                        "backgroundColor": color,
                        "borderColor": color,
                        "textColor": "#ffffff",
                    })

                # ── Opciones del calendario ──────────────────────────────────
                opciones_calendario = {
                    "initialView": "dayGridMonth",
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,timeGridWeek,listMonth",
                    },
                    "locale": "es",
                    "height": 600,
                    "editable": False,
                    "selectable": True,
                }

                # ── Mostrar calendario ───────────────────────────────────────
                st.subheader(f"Préstamos de {nombre_usuario}")
                calendar(events=eventos, options=opciones_calendario)

                # ── Tabla resumen ────────────────────────────────────────────
                st.divider()
                st.subheader("Resumen de préstamos")

                for p in historial:
                    estado = "🔄 Activo" if p.get("activo") else "✅ Devuelto"
                    fecha_dev = p.get("fecha_devolucion") or "—"
                    st.markdown(
                        f"**{p.get('libro')}** · "
                        f"Préstamo: `{p.get('fecha_prestamo')}` · "
                        f"Devolución: `{fecha_dev}` · {estado}"
                    )

    except requests.exceptions.ConnectionError:
        st.error(
            "No se pudo conectar con el servidor FastAPI. "
            "Asegúrate de que los contenedores están en marcha con `docker compose up`."
        )
    except Exception as e:
        st.error(f"Error inesperado: {e}")
