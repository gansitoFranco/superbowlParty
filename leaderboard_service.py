from connection import get_connection
import pandas as pd

def obtener_leaderboard_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM match_results WHERE id = 1")
    real = cursor.fetchone()
    cursor.execute("SELECT * FROM user_predictions")
    predictions = cursor.fetchall()
    
    if not real or not predictions:
        conn.close()
        return pd.DataFrame(columns=["nombre", "Puntos", "Predicción Ganador", "Puntos Predichos"])

    # --- DATOS REALES ---
    real_total = real.get('total_points', 0)
    pats_puntos = real.get('patriots_points', 0)
    hawks_puntos = real.get('seahawks_points', 0)
    first_scorer_real = (real.get('first_scorer') or "").lower()
    sh_scorer_real = (real.get('second_half_first_scorer') or "").lower()

    if pats_puntos > hawks_puntos: ganador_actual = "patriots"
    elif hawks_puntos > pats_puntos: ganador_actual = "seahawks"
    else: ganador_actual = "tie"

    # --- LÓGICA DE CERCANÍA MEJORADA ---
    # Calculamos la diferencia absoluta de cada uno contra el total real
    # Solo si el total es > 0 para evitar dar puntos antes de que empiece el juego
    diffs = []
    for p in predictions:
        pred_val = p.get('puntos_totales') or 0
        diffs.append(abs(pred_val - real_total))
    
    # La diferencia mínima entre todos los participantes
    min_diff = min(diffs) if diffs else None

    leaderboard = []
    for p in predictions:
        puntos = 0
        p_total_pred = p.get('puntos_totales') or 0
        
        # 1. Ganador (7 pts)
        pred_ganador = (p.get('equipo_ganador') or "").lower()
        if ganador_actual != "tie" and ganador_actual in pred_ganador:
            puntos += 7
        
        # 2. First Scorer 1H (2 pts)
        if first_scorer_real and "nadie" not in first_scorer_real:
            if first_scorer_real in (p.get('primer_anotador') or "").lower():
                puntos += 2

        # 3. First Scorer 2H (2 pts)
        if sh_scorer_real and "nadie" not in sh_scorer_real:
            if sh_scorer_real in (p.get('second_half_first_scorer') or "").lower():
                puntos += 2

        # 4. PUNTOS TOTALES (Exacto 5 / Cercano 3)
        # Solo otorgamos puntos de cercanía si el partido ya tiene puntos (total > 0)
        if real_total > 0:
            if p_total_pred == real_total:
                puntos += 5  # Exacto
            elif abs(p_total_pred - real_total) == min_diff:
                puntos += 3  # Es el más cercano (Pablo Q entraría aquí)

        leaderboard.append({
            "nombre": p.get('nombre', 'Anonimo'),
            "Puntos": puntos,
            "Predicción Ganador": p.get('equipo_ganador', 'N/A'),
            "Puntos Predichos": p_total_pred
        })

    conn.close()
    df = pd.DataFrame(leaderboard).sort_values(by="Puntos", ascending=False)
    return df