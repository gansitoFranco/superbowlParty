import streamlit as st
from picks_service import save_pick

PH_EQUIPO = "-- Selecciona equipo ganador --"
PH_BOLADO = "-- Selecciona resultado del volado --"
PH_GANADOR_BOLADO = "-- Selecciona ganador del volado --"
PH_PRIMER_ANOTADOR = "-- Selecciona primer anotador --"

with st.form("user_form"):
    name = st.text_input("Nombre")

    equipo_ganador = st.selectbox(
        "Selecciona equipo ganador",
        [PH_EQUIPO, "Seahawks", "Patriots"]
    )

    puntos_totales = st.number_input(
        "Puntos Totales",
        min_value=0,
        step=1
    )

    resultado_bolado = st.selectbox(
        "Selecciona el resultado del volado",
        [PH_BOLADO, "Cara", "Cruz"]
    )

    ganador_bolado = st.selectbox(
        "Selecciona equipo ganador del volado",
        [PH_GANADOR_BOLADO, "Seahawks", "Patriots"]
    )

    primer_anotador = st.selectbox(
        "Selecciona al primer anotador",
        [PH_PRIMER_ANOTADOR, "Seahawks", "Patriots"]
    )

    submitted = st.form_submit_button("Guardar")

    if submitted:
        errores = False

        if not name:
            st.error("Debes ingresar tu nombre")
            errores = True

        if equipo_ganador == PH_EQUIPO:
            st.error("Debes seleccionar un equipo ganador")
            errores = True

        if resultado_bolado == PH_BOLADO:
            st.error("Debes seleccionar el resultado del bolado")
            errores = True

        if ganador_bolado == PH_GANADOR_BOLADO:
            st.error("Debes seleccionar al ganador del bolado")
            errores = True

        if primer_anotador == PH_PRIMER_ANOTADOR:
            st.error("Debes seleccionar el primer anotador")
            errores = True

        if errores:
            st.stop()

        save_pick(
            nombre=name,
            equipo_ganador=equipo_ganador,
            puntos_totales=puntos_totales,
            resultado_bolado=resultado_bolado,
            ganador_bolado=ganador_bolado,
            primer_anotador=primer_anotador
        )

        st.success("Formulario guardado correctamente ✅")
