import numpy as np
import pandas as pd

def detectar_ciclos(df, min_force=10, smooth_window=5):
    """
    Detecta ciclos HIGH→LOW de forma automática usando picos y valles.
    
    Retorna:
        - n_ciclos: cantidad de ciclos detectados
        - detalles: lista de dicts con:
            { "ciclo": n, "deform_high": xh, "deform_low": xl }
    """

    fuerza = df["Fuerza"].values
    deform = df["Deformacion"].values

    # ==============================
    # 1) Suavizar para reducir ruido
    # ==============================
    if smooth_window > 1:
        fuerza_smooth = np.convolve(
            fuerza, np.ones(smooth_window)/smooth_window, mode='same'
        )
    else:
        fuerza_smooth = fuerza

    # ==============================
    # 2) Detectar picos y valles
    # ==============================
    picos = []
    valles = []

    for i in range(1, len(fuerza_smooth) - 1):
        f_prev = fuerza_smooth[i - 1]
        f = fuerza_smooth[i]
        f_next = fuerza_smooth[i + 1]

        # Pico local
        if f > f_prev and f > f_next and f > min_force:
            picos.append(i)

        # Valle local
        if f < f_prev and f < f_next and f > min_force:
            valles.append(i)

    # ==============================
    # 3) Emparejar picos → valles para formar ciclos
    # ==============================
    ciclos = []
    v_index = 0

    for p in picos:
        # Buscar el valle que venga DESPUÉS del pico
        while v_index < len(valles) and valles[v_index] < p:
            v_index += 1

        if v_index >= len(valles):
            break  # no hay más valles → empieza el pullout

        v = valles[v_index]

        # Ignorar caídas falsas pequeñas
        if fuerza_smooth[v] > fuerza_smooth[p] * 0.8:
            continue

        ciclos.append({
            "ciclo": len(ciclos) + 1,
            "deform_high": deform[p],
            "deform_low": deform[v]
        })

        v_index += 1

    return len(ciclos), ciclos
