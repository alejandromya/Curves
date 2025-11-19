import numpy as np

def detectar_ciclos(df, pico_obj, valle_obj, toler):
    """
    Detecta ciclos como High → Low → High usando un valor global de pico y valle
    con tolerancia. Cada ciclo empieza en un pico y termina en el siguiente pico.
    """

    fuerza = df["Fuerza"].values
    deform = df["Deformacion"].values

    pico_min = pico_obj - toler
    pico_max = pico_obj + toler
    valle_min = valle_obj - toler
    valle_max = valle_obj + toler

    # Índices de picos y valles
    picos_idx = np.where((fuerza >= pico_min) & (fuerza <= pico_max))[0]
    valles_idx = np.where((fuerza >= valle_min) & (fuerza <= valle_max))[0]

    if len(picos_idx) < 2 or len(valles_idx) == 0:
        return 0, {}

    ciclos = []
    v_ptr = 0  # puntero a valles

    for i in range(len(picos_idx) - 1):
        p_inicio = picos_idx[i]
        p_final = picos_idx[i + 1]

        # Buscar el primer valle que esté entre estos dos picos
        while v_ptr < len(valles_idx) and valles_idx[v_ptr] <= p_inicio:
            v_ptr += 1

        if v_ptr >= len(valles_idx):
            break  # no hay más valles

        v = valles_idx[v_ptr]

        if v >= p_final:
            continue

        ciclos.append({
            "ciclo": len(ciclos) + 1,
            "pico_inicio_idx": p_inicio,
            "valle_idx": v,
            "pico_final_idx": p_final,
            "deform_high_start": deform[p_inicio],
            "deform_low": deform[v],
            "deform_high_end": deform[p_final]
        })

        v_ptr += 1  # avanzar puntero de valle

    ciclos_dict = {c["ciclo"]: c for c in ciclos}
    return len(ciclos), ciclos_dict