import numpy as np

def detectar_ciclos(df, pico_obj, valle_obj, toler):
    """
    Detecta ciclos High → Low → High usando máximos y mínimos locales dentro
    de la tolerancia definida por pico_obj y valle_obj.

    Devuelve:
        num_ciclos: int
        ciclos_dict: dict con información de cada ciclo
    """
    fuerza = df["Fuerza"].values
    deform = df["Deformacion"].values

    # Derivada discreta
    dF = np.gradient(fuerza)

    # Detectar máximos y mínimos locales
    max_local_idx = np.where((np.hstack([dF[0] > 0, dF[:-1] > 0]) & np.hstack([dF[1:] < 0, dF[-1] < 0])))[0]
    min_local_idx = np.where((np.hstack([dF[0] < 0, dF[:-1] < 0]) & np.hstack([dF[1:] > 0, dF[-1] > 0])))[0]

    # Filtrar según tolerancia
    picos_idx = [i for i in max_local_idx if pico_obj - toler <= fuerza[i] <= pico_obj + toler]
    valles_idx = [i for i in min_local_idx if valle_obj - toler <= fuerza[i] <= valle_obj + toler]

    if len(picos_idx) < 2 or len(valles_idx) == 0:
        return 0, {}

    ciclos = []
    v_ptr = 0

    for i in range(len(picos_idx) - 1):
        p_inicio = picos_idx[i]
        p_final = picos_idx[i + 1]

        # Buscar primer valle entre los dos picos
        while v_ptr < len(valles_idx) and valles_idx[v_ptr] <= p_inicio:
            v_ptr += 1
        if v_ptr >= len(valles_idx):
            break

        v = valles_idx[v_ptr]
        if v >= p_final:
            continue

        ciclos.append({
            "ciclo": len(ciclos) + 1,
            "pico_inicio_idx": p_inicio,
            "pico_inicio_f": float(fuerza[p_inicio]),
            "valle_idx": v,
            "valle_f": float(fuerza[v]),
            "pico_final_idx": p_final,
            "pico_final_f": float(fuerza[p_final]),
            "deform_high_start": float(deform[p_inicio]),
            "deform_low": float(deform[v]),
            "deform_high_end": float(deform[p_final])
        })
        v_ptr += 1

    ciclos_dict = {c["ciclo"]: c for c in ciclos}
    return len(ciclos), ciclos_dict