from connection import get_connection
import pandas as pd

def obtener_leaderboard_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Obtener resultado real del Admin
    cursor.execute("SELECT * FROM match_results WHERE id = 1")
    real = cursor.fetchone()
    
    # 2. Obtener predicciones de los usuarios
    cursor.execute("SELECT * FROM user_predictions")
    predictions = cursor.fetchall()
    
    if not real or not predictions:
        conn.close()
        return pd.DataFrame(columns=["nombre", "Puntos", "Predicción Ganador", "Puntos Predichos"])

    # --- NORMALIZACIÓN DE DATOS REALES (ADMIN) ---
    pats_puntos = real.get('patriots_points', 0) or 0
    hawks_puntos = real.get('seahawks_points', 0) or 0
    
    # Limpieza de textos para comparación
    toss_res_real = (real.get('coin_toss_result') or "").lower().strip()
    toss_win_real = (real.get('coin_toss_winner') or "").lower().strip()
    first_scorer_real = (real.get('first_scorer') or "").lower().strip()
    sh_scorer_real = (real.get('second_half_first_scorer') or "").lower().strip()
    
    # Determinación del Ganador Real
    if pats_puntos > hawks_puntos: ganador_actual = "patriots"
    elif hawks_puntos > pats_puntos: ganador_actual = "seahawks"
    else: ganador_actual = "tie"

    # Mapeo flexible para el volado
    mapeo_volado = {"heads": ["cara", "heads", "head"], "tails": ["cruz", "tails", "tail"]}

    # --- CÁLCULO DE CERCANÍA (Para los 3 pts) ---
    real_total = real.get('total_points') or 0
    diffs = [abs((p.get('puntos_totales') or 0) - real_total) for p in predictions]
    min_diff = min(diffs) if diffs else 0

    leaderboard = []
    for p in predictions:
        puntos = 0
        
        # 1. Ganador del Partido (7 pts)
        pred_ganador = (p.get('equipo_ganador') or "").lower()
        if ganador_actual != "tie" and ganador_actual in pred_ganador:
            puntos += 7
        
        # 2. Resultado del Volado (1 pt)
        pred_toss_res = (p.get('resultado_bolado') or "").lower().strip()
        if toss_res_real in mapeo_volado and pred_toss_res in mapeo_volado[toss_res_real]:
            puntos += 1
            
        # 3. Equipo Ganador del Volado (2 pts)
        pred_toss_win = (p.get('ganador_bolado') or "").lower()
        if "nadie" not in toss_win_real and toss_win_real != "":
            if ("patriots" in toss_win_real and "patriots" in pred_toss_win) or \
               ("seahawks" in toss_win_real and "seahawks" in pred_toss_win):
                puntos += 2
            
        # 4. Primer Anotador 1ra Mitad (2 pts)
        pred_scorer = (p.get('primer_anotador') or "").lower()
        if "nadie" not in first_scorer_real and first_scorer_real != "":
            if ("patriots" in first_scorer_real and "patriots" in pred_scorer) or \
               ("seahawks" in first_scorer_real and "seahawks" in pred_scorer):
                puntos += 2

        # 5. Primer Anotador 2da Mitad (2 pts)
        pred_sh_scorer = (p.get('second_half_first_scorer') or "").lower()
        if "nadie" not in sh_scorer_real and sh_scorer_real != "":
            if ("patriots" in sh_scorer_real and "patriots" in pred_sh_scorer) or \
               ("seahawks" in sh_scorer_real and "seahawks" in pred_sh_scorer):
                puntos += 2

        # 6. Puntos Totales (Exacto 5 / Cercano 3)
        p_total_pred = p.get('puntos_totales') or 0
        if real_total > 0: 
            if p_total_pred == real_total:
                puntos += 5
            elif abs(p_total_pred - real_total) == min_diff:
                puntos += 3

        leaderboard.append({
            "nombre": p.get('nombre', 'Anonimo'),
            "Puntos": puntos,
            "Predicción Ganador": p.get('equipo_ganador', 'N/A'),
            "Puntos Predichos": p_total_pred
        })

    conn.close()
    df = pd.DataFrame(leaderboard)
    if not df.empty:
        df = df.sort_values(by="Puntos", ascending=False)
    
    return df