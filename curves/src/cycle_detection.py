import numpy as np

def detectar_ciclos(df, pico_obj, valle_obj, toler):
    fuerza = df["Fuerza"].values
    deform = df["Deformacion"].values

    dF = np.gradient(fuerza)

    max_local_idx = np.where(
        (np.hstack([dF[0] > 0, dF[:-1] > 0]) &
         np.hstack([dF[1:] < 0, dF[-1] < 0]))
    )[0]

    min_local_idx = np.where(
        (np.hstack([dF[0] < 0, dF[:-1] < 0]) &
         np.hstack([dF[1:] > 0, dF[-1] > 0]))
    )[0]

    picos_idx = [i for i in max_local_idx if pico_obj - toler <= fuerza[i] <= pico_obj + toler]
    valles_idx = [i for i in min_local_idx if valle_obj - toler <= fuerza[i] <= valle_obj + toler]

    if len(picos_idx) < 2 or len(valles_idx) == 0:
        return 0, {}

    ciclos = []
    v_ptr = 0

    for i in range(len(picos_idx) - 1):
        p_inicio = picos_idx[i]
        p_final = picos_idx[i + 1]

        while v_ptr < len(valles_idx) and valles_idx[v_ptr] <= p_inicio:
            v_ptr += 1
        if v_ptr >= len(valles_idx):
            break

        v = valles_idx[v_ptr]
        if v >= p_final:
            continue

        # --- cyclic stiffness ---
        f_high = fuerza[p_final]
        f_low = fuerza[v]
        d_high = deform[p_final]
        d_low = deform[v]

        cyclic_stiffness = None
        denom = d_high - d_low
        if denom != 0:
            cyclic_stiffness = (f_high - f_low) / denom

        ciclos.append({
            "ciclo": len(ciclos) + 1,

            "pico_inicio_idx": int(p_inicio),
            "pico_inicio_f": float(fuerza[p_inicio]),

            "valle_idx": int(v),
            "valle_f": float(fuerza[v]),

            "pico_final_idx": int(p_final),
            "pico_final_f": float(fuerza[p_final]),

            "deform_high_start": float(deform[p_inicio]),
            "deform_low": float(deform[v]),
            "deform_high_end": float(deform[p_final]),

            # ⭐ AQUÍ
            "cyclic_stiffness": float(cyclic_stiffness) if cyclic_stiffness is not None else None
        })

        v_ptr += 1

    ciclos_dict = {c["ciclo"]: c for c in ciclos}
    return len(ciclos), ciclos_dict
