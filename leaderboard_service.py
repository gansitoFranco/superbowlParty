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
        return pd.DataFrame(columns=["nombre", "Puntos", "Pick Ganador", "Predicción Total"])

    # --- DATOS REALES (Asegurando que 0 sea tratado como número) ---
    pats_puntos = real.get('patriots_points') if real.get('patriots_points') is not None else 0
    hawks_puntos = real.get('seahawks_points') if real.get('seahawks_points') is not None else 0
    real_total = pats_puntos + hawks_puntos
    
    first_scorer_real = (real.get('first_scorer') or "").lower().strip()
    sh_scorer_real = (real.get('second_half_first_scorer') or "").lower().strip()

    # Determinar Ganador Real
    if pats_puntos > hawks_puntos: ganador_actual = "patriots"
    elif hawks_puntos > pats_puntos: ganador_actual = "seahawks"
    else: ganador_actual = "tie"

    # --- CÁLCULO DE DIFERENCIA MÍNIMA ---
    # Calculamos la diferencia de todos contra el total real (3 en este caso)
    diffs = [abs((p.get('puntos_totales') or 0) - real_total) for p in predictions]
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
        pred_fs = (p.get('primer_anotador') or "").lower()
        if first_scorer_real and "nadie" not in first_scorer_real:
            if "patriots" in first_scorer_real and "patriots" in pred_fs: puntos += 2
            elif "seahawks" in first_scorer_real and "seahawks" in pred_fs: puntos += 2

        # 3. First Scorer 2H (2 pts) - Si ya ocurrió
        pred_sh = (p.get('second_half_first_scorer') or "").lower()
        if sh_scorer_real and "nadie" not in sh_scorer_real:
            if "patriots" in sh_scorer_real and "patriots" in pred_sh: puntos += 2
            elif "seahawks" in sh_scorer_real and "seahawks" in pred_sh: puntos += 2

        # 4. CERCANÍA O EXACTO (3 o 5 pts)
        # Pablo Q: Predijo 31, Real es 3. Su diferencia es 28.
        # Si 28 es el min_diff, suma 3 puntos.
        if real_total > 0:
            if p_total_pred == real_total:
                puntos += 5
            elif min_diff is not None and abs(p_total_pred - real_total) == min_diff:
                puntos += 3

        # 5. Volado (Opcional, si lo tienes en tu tabla de puntos)
        # Si acertó Ganador (7) + Scorer (2) + Cercanía (3) + Volado (1) = 13 pts.

        leaderboard.append({
            "nombre": p.get('nombre', 'Anonimo'),
            "Puntos": puntos,
            "Pick Ganador": p.get('equipo_ganador', 'N/A'),
            "Predicción Total": p_total_pred
        })

    conn.close()
    df = pd.DataFrame(leaderboard).sort_values(by="Puntos", ascending=False)
    return df