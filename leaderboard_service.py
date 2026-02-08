from connection import get_connection
import pandas as pd

def obtener_leaderboard_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Obtener resultado real
    cursor.execute("SELECT * FROM match_results WHERE id = 1")
    real = cursor.fetchone()
    
    # 2. Obtener predicciones
    cursor.execute("SELECT * FROM user_predictions")
    predictions = cursor.fetchall()
    
    # --- VALIDACIÓN INICIAL: Si no hay datos, salir elegantemente ---
    if not real or not predictions:
        conn.close()
        # Retornamos un DataFrame con las columnas necesarias pero vacío
        return pd.DataFrame(columns=["nombre", "Puntos", "Predicción Ganador", "Puntos Predichos"])

    # --- NORMALIZACIÓN ADMIN (con seguros para None) ---
    pats_puntos = real.get('patriots_points', 0) or 0
    hawks_puntos = real.get('seahawks_points', 0) or 0
    toss_res_real = (real.get('coin_toss_result') or "").lower().strip()
    toss_win_real = (real.get('coin_toss_winner') or "").lower().strip()
    first_scorer_real = (real.get('first_scorer') or "").lower().strip()
    
    # Ganador Real
    if pats_puntos > hawks_puntos:
        ganador_actual_key = "patriots"
    elif hawks_puntos > pats_puntos:
        ganador_actual_key = "seahawks"
    else:
        ganador_actual_key = "tie"

    # Mapeo de Volado
    mapeo_volado = {
        "heads": ["cara", "heads", "head"],
        "tails": ["cruz", "tails", "tail"]
    }

    # --- CÁLCULO DE DIFERENCIA MÍNIMA (Seguro) ---
    diffs = [abs((p.get('puntos_totales') or 0) - (real.get('total_points') or 0)) for p in predictions]
    min_diff = min(diffs) if diffs else 0

    leaderboard = []
    for p in predictions:
        puntos = 0
        
        # 1. Ganador (5 pts)
        pred_ganador = (p.get('equipo_ganador') or "").lower()
        if ganador_actual_key != "tie" and ganador_actual_key in pred_ganador:
            puntos += 5
        
        # 2. Resultado Volado (1 pt)
        pred_toss_res = (p.get('resultado_bolado') or "").lower().strip()
        if toss_res_real in mapeo_volado and pred_toss_res in mapeo_volado[toss_res_real]:
            puntos += 1
            
        # 3. Ganador Volado Equipo (2 pts)
        pred_toss_win = (p.get('ganador_bolado') or "").lower()
        if toss_win_real != "" and (("patriots" in pred_toss_win and "patriots" in toss_win_real) or 
                                    ("seahawks" in pred_toss_win and "seahawks" in toss_win_real)):
            puntos += 2
            
        # 4. First Scorer (2 pts)
        pred_scorer = (p.get('primer_anotador') or "").lower()
        if first_scorer_real != "" and (("patriots" in pred_scorer and "patriots" in first_scorer_real) or 
                                        ("seahawks" in pred_scorer and "seahawks" in first_scorer_real)):
            puntos += 2

        # 5. Puntos Totales (Exacto 5 / Prox 3)
        p_total_pred = p.get('puntos_totales') or 0
        real_total = real.get('total_points') or 0
        
        if real_total > 0: # Solo contar si el partido ya empezó/tiene puntos
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
    
    # Creamos el DF y ordenamos. El nombre de la columna es "Puntos" con P mayúscula.
    df = pd.DataFrame(leaderboard)
    if not df.empty:
        df = df.sort_values(by="Puntos", ascending=False)
    
    return df