import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de conexión
conn = st.connection("mysql", type="sql")

# 2. Función para obtener datos (con caché para no saturar la BD)
@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def obtener_datos():
    query = "SELECT * FROM user_predictions;"
    return conn.query(query, ttl="10m")

st.title("resultados superbowlParty")

# 3. Carga y visualización
df = obtener_datos()

st.dataframe(df, use_container_width=True)

