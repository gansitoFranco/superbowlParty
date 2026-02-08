import streamlit as st
from leaderboard_service import obtener_leaderboard_data
from admin_service import obtener_marcador_previo
from datetime import datetime

st.set_page_config(page_title="Super Bowl Leaderboard", layout="wide")

# 1. Encabezado con Título, Reglas y botón de refresco
col_title, col_rules, col_refresh = st.columns([3, 1, 1])

with col_title:
    st.title("🏆 Leaderboard Super Bowl Party")

with col_rules:
    with st.popover("📋 Ver Reglas"):
        st.markdown("""
        ### 🏈 Sistema de Puntos
        | Categoría | Puntos |
        | :--- | :---: |
        | **Ganador del Partido** | 7 pts |
        | **Puntos Totales Exactos** | 5 pts |
        | **Puntos Totales (Más cercano)** | 3 pts |
        | **Primer Anotador 2da Mitad** | 2 pts |
        | **Ganador del Volado (Equipo)** | 2 pts |
        | **Primer Equipo en Anotar** | 2 pts |
        | **Cara o Cruz** | 1 pt |
        
        *Nota: Los puntos se calculan dinámicamente según los datos ingresados por el Admin.*
        """)

with col_refresh:
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()

# 2. Mostrar Marcador Real Actual
real = obtener_marcador_previo()
if real:
    # Mostramos también quién anotó en la 2da mitad si ya existe el dato
    sh_text = f" | 2da Mitad: {real['second_half_first_scorer']}" if real.get('second_half_first_scorer') and real['second_half_first_scorer'] != "Nadie aún" else ""
    st.info(f"🏈 Marcador Actual: Patriots {real['patriots_points']} - {real['seahawks_points']} Seahawks | Total: {real['total_points']}{sh_text}")
else:
    st.info("🏈 Esperando el inicio del partido...")

st.divider()

# 3. Cargar Datos del Leaderboard
df = obtener_leaderboard_data()

if not df.empty:
    st.subheader("📍 Posiciones Actuales")
    
    num_jugadores = len(df)
    cols_count = min(num_jugadores, 3)
    top_3 = df.head(cols_count)
    
    cols = st.columns(cols_count)
    
    for i, (index, row) in enumerate(top_3.iterrows()):
        nombre_usuario = row.get('nombre', 'Anónimo')
        puntos_usuario = row.get('Puntos', 0)
        
        cols[i].metric(
            label=f"Posición {i+1}", 
            value=nombre_usuario, 
            delta=f"{puntos_usuario} pts"
        )

    st.write("---")
    st.write("### 📊 Tabla General")
    
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
    st.warning("📢 Aún no hay predicciones registradas.")