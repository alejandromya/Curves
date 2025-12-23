import numpy as np

# ============================================================
# DETECCIÓN DE CICLOS + CÁLCULO DE CYCLIC STIFFNESS (ORIGEN)
# ============================================================

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

        # --- CYCLIC STIFFNESS REAL ---
        d_high = deform[p_final]
        d_low = deform[v]
        f_high = fuerza[p_final]
        f_low = fuerza[v]

        cyclic_stiffness = None
        if d_high != d_low:
            cyclic_stiffness = (f_high - f_low) / (d_high - d_low)

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

            # ⭐ AQUÍ SE CALCULA UNA SOLA VEZ
            "cyclic_stiffness": float(cyclic_stiffness) if cyclic_stiffness is not None else None
        })

        v_ptr += 1

    ciclos_dict = {c["ciclo"]: c for c in ciclos}
    return len(ciclos), ciclos_dict


# ============================================================
# HELPERS
# ============================================================

def _try_get(d: dict, keys, default=None):
    for k in keys:
        if k in d:
            return d[k]
    return default


def _format_num(v):
    if v is None:
        return "—"
    try:
        if isinstance(v, int):
            return f"{v}"
        return f"{float(v):.2f}"
    except Exception:
        return str(v)


# ============================================================
# FILA POR SAMPLE
# ============================================================

def generar_fila_sample(bloque):
    df = bloque.get("df")
    detalles = bloque.get("ciclos", {})
    fuerza_max = bloque.get("fuerza_max")
    deformacion_max = bloque.get("deformacion_max")

    # --- ciclos HIGH ---
    ciclos_obj = [1, 10, 50, 100, 250, 500]
    valores_ciclos = []

    for c in ciclos_obj:
        cd = detalles.get(c)
        valores_ciclos.append(_format_num(cd.get("deform_high_end") if cd else None))

    # --- LOW último ciclo ---
    try:
        ultimo = detalles[max(detalles.keys())]
        deform_low_last = ultimo.get("deform_low")
    except Exception:
        deform_low_last = None

    f2mm_y = f3mm_y = None
    if deform_low_last is not None and df is not None:
        try:
            f2_idx = (df["Deformacion"] - deform_low_last - 2).abs().idxmin()
            f3_idx = (df["Deformacion"] - deform_low_last - 3).abs().idxmin()
            f2mm_y = float(df.loc[f2_idx, "Fuerza"])
            f3mm_y = float(df.loc[f3_idx, "Fuerza"])
        except Exception:
            pass

    # --- stiffness ---
    yield_stiffness = bloque.get("yield_stiffness")
    cd250 = detalles.get(250)
    cyclic_stiffness = cd250.get("cyclic_stiffness") if cd250 else None

    # guardar a nivel bloque
    bloque["cyclic_stiffness"] = cyclic_stiffness

    return [
        bloque.get("titulo", "Sample"),
        *valores_ciclos,
        _format_num(cyclic_stiffness),
        _format_num(yield_stiffness),
        _format_num(fuerza_max),
        _format_num(deformacion_max),
        _format_num(f2mm_y),
        _format_num(f3mm_y),
    ]


# ============================================================
# TABLAS COMBINADAS
# ============================================================

def generar_tablas_combinadas(bloques):

    headers_cyclic = ["0", "10", "50", "100", "250", "500", "Cyclic Stiffness (N/mm)"]
    headers_3rd = [
        "Yield Stiffness (N/mm)",
        "FMax ATM (N)",
        "Max Disp ATM (mm)",
        "Force at 2mm (N)",
        "Force at 3mm (N)",
    ]

    filas_cyclic = []
    filas_3rd = []

    for b in bloques:
        detalles = b["ciclos"]
        df = b["df"]

        primer = detalles[min(detalles.keys())]
        ultimo = detalles[max(detalles.keys())]

        cd250 = detalles.get(250)
        cyclic_stiffness = cd250.get("cyclic_stiffness") if cd250 else None

        # --- Cyclic ---
        filas_cyclic.append([
            _format_num(primer.get("deform_high_start")),
            _format_num(detalles.get(10, {}).get("deform_high_end")),
            _format_num(detalles.get(50, {}).get("deform_high_end")),
            _format_num(detalles.get(100, {}).get("deform_high_end")),
            _format_num(detalles.get(250, {}).get("deform_high_end")),
            _format_num(detalles.get(500, {}).get("deform_high_end")),
            _format_num(cyclic_stiffness),
        ])

        # --- 3rd phase ---
        deform_low = ultimo.get("deform_low")
        f2mm_y = f3mm_y = None

        if deform_low is not None:
            f2_idx = (df["Deformacion"] - deform_low - 2).abs().idxmin()
            f3_idx = (df["Deformacion"] - deform_low - 3).abs().idxmin()
            f2mm_y = df.loc[f2_idx, "Fuerza"]
            f3mm_y = df.loc[f3_idx, "Fuerza"]

        filas_3rd.append([
            _format_num(b.get("yield_stiffness")),
            _format_num(b.get("fuerza_max")),
            _format_num(b.get("deformacion_max")),
            _format_num(f2mm_y),
            _format_num(f3mm_y),
        ])

    return (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd)