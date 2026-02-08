from connection import get_connection

def save_pick(
    nombre,
    equipo_ganador,
    puntos_totales,
    resultado_bolado,
    ganador_bolado,
    primer_anotador
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO user_predictions (
            nombre,
            equipo_ganador,
            puntos_totales,
            resultado_bolado,
            ganador_bolado,
            primer_anotador
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        nombre,
        equipo_ganador,
        puntos_totales,
        resultado_bolado,
        ganador_bolado,
        primer_anotador
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()
