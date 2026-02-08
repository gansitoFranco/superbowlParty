import streamlit as st
from leaderboard_service import obtener_leaderboard_data
from admin_service import obtener_marcador_previo
from datetime import datetime

st.set_page_config(page_title="Super Bowl Leaderboard", layout="wide")

# 1. Encabezado con botón de refresco
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("🏆 Leaderboard Super Bowl Party")
with col_refresh:
    if st.button("🔄 Actualizar"):
        st.rerun()

# 2. Mostrar Marcador Real Actual (con validación por si no hay datos de admin)
real = obtener_marcador_previo()
if real:
    st.info(f"🏈 Marcador Actual: Patriots {real['patriots_points']} - {real['seahawks_points']} Seahawks | Total: {real['total_points']}")
else:
    st.info("🏈 Esperando el inicio del partido...")

st.divider()

# 3. Cargar Datos del Leaderboard
df = obtener_leaderboard_data()

# Solo entramos aquí si el DataFrame tiene filas
if not df.empty:
    # Mostrar el podio (Top 3)
    st.subheader("📍 Posiciones Actuales")
    
    # Determinamos cuántas métricas mostrar (si hay 1 persona, solo sale 1 columna)
    num_jugadores = len(df)
    cols_count = min(num_jugadores, 3)
    top_3 = df.head(cols_count)
    
    cols = st.columns(cols_count)
    
    for i, (index, row) in enumerate(top_3.iterrows()):
        # Usamos row.get para evitar KeyErrors si la columna cambia de nombre
        nombre_usuario = row.get('nombre', 'Anónimo')
        puntos_usuario = row.get('Puntos', 0)
        
        cols[i].metric(
            label=f"Posición {i+1}", 
            value=nombre_usuario, 
            delta=f"{puntos_usuario} pts"
        )

    st.write("---")
    st.write("### 📊 Tabla General")
    
    # Configuración de la tabla para que se vea impecable
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "nombre": "Participante",
            "Puntos": st.column_config.NumberColumn("Puntos 🏈", format="%d"),
            "Predicción Ganador": "Pick Ganador",
            "Puntos Predichos": "Total O/U"
        }
    )
    
    st.caption(f"⏱️ Última actualización: {datetime.now().strftime('%H:%M:%S')}")

else:
    # Mensaje amigable cuando truncas las tablas para el escenario real
    st.warning("📢 Aún no hay predicciones registradas. ¡Invita a los participantes a llenar sus picks!")
    
