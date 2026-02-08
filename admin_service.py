from connection import get_connection

def asegurar_registro_inicial():
    """Verifica si existe el registro del partido; si no, lo crea con valores por defecto."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM match_results WHERE id = 1")
    existe = cursor.fetchone()[0]
    
    if existe == 0:
        # Insertamos la fila inicial incluyendo los nuevos campos como NULL o vacíos
        sql = """
            INSERT INTO match_results 
            (id, patriots_points, seahawks_points, total_points, first_scorer, coin_toss_result, coin_toss_winner) 
            VALUES (1, 0, 0, 0, NULL, NULL, NULL)
        """
        cursor.execute(sql)
        conn.commit()
    
    cursor.close()
    conn.close()

def obtener_marcador_previo():
    """Recupera todos los datos de la fila única para cargar el formulario."""
    asegurar_registro_inicial()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Seleccionamos todos los campos para que Streamlit los pueda usar
    sql = """
        SELECT patriots_points, seahawks_points, total_points, 
               first_scorer, coin_toss_result, coin_toss_winner 
        FROM match_results WHERE id = 1
    """
    cursor.execute(sql)
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado

def actualizar_marcador_db(pats, hawks, scorer, toss_res, toss_win):
    """Actualiza los puntos, el total calculado y los eventos especiales en la BD."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Calculamos el total de puntos
    total = pats + hawks
    
    # SQL con 6 marcadores (%s) para los 6 valores que queremos guardar
    sql = """
        UPDATE match_results 
        SET patriots_points = %s, 
            seahawks_points = %s, 
            total_points = %s,
            first_scorer = %s,
            coin_toss_result = %s,
            coin_toss_winner = %s
        WHERE id = 1
    """
    
    # La tupla debe contener los 6 elementos en el orden exacto del SQL anterior
    valores = (pats, hawks, total, scorer, toss_res, toss_win)
    
    cursor.execute(sql, valores)
    conn.commit()
    cursor.close()
    conn.close()