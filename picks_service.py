from connection import get_connection

def save_pick(
    nombre,
    equipo_ganador,
    puntos_totales,
    resultado_bolado,
    ganador_bolado,
    primer_anotador,
    second_half_first_scorer 
):
    conn = get_connection()
    cursor = conn.cursor()

    # Aquí en el string (query) sí puedes usar comentarios de SQL si quieres, 
    # pero los quitaremos para que sea más legible.
    query = """
        INSERT INTO user_predictions (
            nombre,
            equipo_ganador,
            puntos_totales,
            resultado_bolado,
            ganador_bolado,
            primer_anotador,
            second_half_first_scorer
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # En la tupla 'values' NO deben ir comentarios.
    values = (
        nombre,
        equipo_ganador,
        puntos_totales,
        resultado_bolado,
        ganador_bolado,
        primer_anotador,
        second_half_first_scorer
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()