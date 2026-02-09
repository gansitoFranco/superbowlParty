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
    
    # Normalización para evitar errores de texto
    first_scorer_real = (real.get('first_scorer') or "").lower().strip()
    sh_scorer_real = (real.get('second_half_first_scorer') or "").lower().strip()
    toss_win_real = (real.get('coin_toss_winner') or "").lower().strip()
    toss_res_real = (real.get('coin_toss_result') or "").lower().strip()

    # Ganador Real
    if pats_puntos > hawks_puntos: ganador_actual = "patriots"
    elif hawks_puntos > pats_puntos: ganador_actual = "seahawks"
    else: ganador_actual = "tie"

    # --- LÓGICA DE CERCANÍA ---
    # Calculamos todas las diferencias primero
    diffs = [abs((p.get('puntos_totales') or 0) - real_total) for p in predictions]
    min_diff = min(diffs) if diffs else None

    leaderboard = []
    for p in predictions:
        puntos = 0
        p_total_pred = p.get('puntos_totales') or 0
        
        # 1. Ganador (7 pts) - Buscamos palabra clave para ser flexibles
        pred_ganador = (p.get('equipo_ganador') or "").lower()
        if ganador_actual != "tie" and ganador_actual in pred_ganador:
            puntos += 7
        
        # 2. First Scorer 1H (2 pts)
        pred_fs = (p.get('primer_anotador') or "").lower()
        if first_scorer_real and "nadie" not in first_scorer_real:
            if "patriots" in first_scorer_real and "patriots" in pred_fs: puntos += 2
            elif "seahawks" in first_scorer_real and "seahawks" in pred_fs: puntos += 2

        # 3. First Scorer 2H (2 pts)
        pred_sh = (p.get('second_half_first_scorer') or "").lower()
        if sh_scorer_real and "nadie" not in sh_scorer_real:
            if "patriots" in sh_scorer_real and "patriots" in pred_sh: puntos += 2
            elif "seahawks" in sh_scorer_real and "seahawks" in pred_sh: puntos += 2

        # 4. Volado (Result 1pt / Winner 2pts)
        pred_toss_res = (p.get('resultado_bolado') or "").lower()
        if toss_res_real and ("heads" in toss_res_real or "tails" in toss_res_real):
            # Mapeo simple: Heads=Cara, Tails=Cruz
            if ("heads" in toss_res_real and "cara" in pred_toss_res) or \
               ("tails" in toss_res_real and "cruz" in pred_toss_res):
                puntos += 1

        pred_toss_win = (p.get('ganador_bolado') or "").lower()
        if toss_win_real and "nadie" not in toss_win_real:
            if "patriots" in toss_win_real and "patriots" in pred_toss_win: puntos += 2
            elif "seahawks" in toss_win_real and "seahawks" in pred_toss_win: puntos += 2

        # 5. PUNTOS TOTALES (Exacto 5 / Cercano 3)
        if real_total > 0:
            if p_total_pred == real_total:
                puntos += 5
            elif abs(p_total_pred - real_total) == min_diff:
                # Solo damos puntos de cercanía si NO acertó el exacto 
                # (para no duplicar puntos en la misma categoría)
                puntos += 3

        leaderboard.append({
            "nombre": p.get('nombre', 'Anonimo'),
            "Puntos": puntos,
            "Pick Ganador": p.get('equipo_ganador', 'N/A'),
            "Predicción Total": p_total_pred
        })

    conn.close()
    # Ordenamos por Puntos y luego por nombre para desempates visuales
    df = pd.DataFrame(leaderboard).sort_values(by=["Puntos", "nombre"], ascending=[False, True])
    return df