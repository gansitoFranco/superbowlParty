import streamlit as st
from admin_service import obtener_marcador_previo, actualizar_marcador_db

# 1. Configuración estética
st.set_page_config(page_title="Super Bowl LX Admin", layout="centered")

st.markdown("""
    <style>
    .team-label { font-size: 20px; font-weight: bold; margin-top: 10px; }
    .record-label { color: #888; font-size: 14px; margin-bottom: 10px; }
    .vs-text { 
        font-size: 18px; color: #888; display: flex; 
        justify-content: center; align-items: center; height: 150px; 
    }
    .total-box {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Carga de datos inicial
datos = obtener_marcador_previo()
pats_score_db = datos['patriots_points']
hawks_score_db = datos['seahawks_points']
total_puntos_db = datos['total_points']

# 3. Encabezado
st.title("Super Bowl LX Admin")
st.write("NFL · Panel de Control en Vivo")

# 4. Resumen de Puntos Totales
st.markdown(f"""
    <div class="total-box">
        <small style="color: #888;">PUNTOS TOTALES ACTUALES (BD)</small>
        <h1 style="margin:0; color: #00ff00;">{total_puntos_db}</h1>
    </div>
    """, unsafe_allow_html=True)

# Listas de opciones para los Dropdowns
equipos = ["Nadie aún", "New England Patriots", "Seattle Seahawks"]
opciones_volado = ["Heads", "Tails"]

# 5. Formulario de Actualización
with st.form("marcador_form"):
    # --- SECCIÓN DE MARCADOR ---
    col1, col_vs, col2 = st.columns([2, 0.5, 2])
    
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/en/b/b9/New_England_Patriots_logo.svg", width=120)
        st.markdown('<p class="team-label">New England Patriots</p>', unsafe_allow_html=True)
        st.markdown('<p class="record-label">(17 - 3)</p>', unsafe_allow_html=True)
        nuevo_pats = st.number_input("Puntos Patriots", value=pats_score_db, step=1, label_visibility="collapsed")

    with col_vs:
        st.markdown('<div class="vs-text">vs.</div>', unsafe_allow_html=True)

    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/en/8/8e/Seattle_Seahawks_logo.svg", width=120)
        st.markdown('<p class="team-label">Seattle Seahawks</p>', unsafe_allow_html=True)
        st.markdown('<p class="record-label">(16 - 3)</p>', unsafe_allow_html=True)
        nuevo_hawks = st.number_input("Puntos Seahawks", value=hawks_score_db, step=1, label_visibility="collapsed")

    st.divider()
    
    # --- SECCIÓN DE EVENTOS ESPECIALES ---
    st.subheader("Eventos Especiales")
    
    # Primera Fila: First Scorer y Coin Toss Result
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        def_scorer = equipos.index(datos['first_scorer']) if datos['first_scorer'] in equipos else 0
        nuevo_scorer = st.selectbox("1st Half First Scorer", equipos, index=def_scorer)
    with row1_c2:
        def_toss_res = opciones_volado.index(datos['coin_toss_result']) if datos['coin_toss_result'] in opciones_volado else 0
        nuevo_toss_res = st.selectbox("Coin Toss Result", opciones_volado, index=def_toss_res)

    # Segunda Fila: Coin Toss Winner y Second Half Scorer
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        def_toss_win = equipos.index(datos['coin_toss_winner']) if datos['coin_toss_winner'] in equipos else 0
        nuevo_toss_win = st.selectbox("Coin Toss Winner", equipos, index=def_toss_win)
    with row2_c2:
        # --- NUEVO CAMPO: 2nd Half First Scorer ---
        def_sh_scorer = equipos.index(datos['second_half_first_scorer']) if datos.get('second_half_first_scorer') in equipos else 0
        nuevo_sh_scorer = st.selectbox("2nd Half First Scorer", equipos, index=def_sh_scorer)

    submit = st.form_submit_button("ACTUALIZAR TODO EL REGISTRO", use_container_width=True)

# 6. Lógica de guardado
if submit:
    try:
        # Ahora enviamos 6 parámetros a la función del servicio
        actualizar_marcador_db(
            nuevo_pats, 
            nuevo_hawks, 
            nuevo_scorer, 
            nuevo_toss_res, 
            nuevo_toss_win,
            nuevo_sh_scorer  # Sexto parámetro enviado
        )
        
        st.success("✅ Registro completo actualizado exitosamente.")
        st.rerun() 
            
    except Exception as e:
        st.error(f"Error al guardar: {e}")

st.divider()
st.caption("Administrador oficial de Super Bowl Party 2026.")