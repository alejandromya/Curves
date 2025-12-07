# ---------------------------
# Helpers para extraer campos
# ---------------------------
def _try_get(d: dict, keys, default=None):
    """Intentar obtener el primer key existente en d de la lista keys."""
    for k in keys:
        if k in d:
            return d[k]
    return default

def _format_num(v):
    if v is None:
        return "—"
    try:
        # Si es entero muy grande, mostrar sin decimales; si float, 2 decimales
        if isinstance(v, int):
            return f"{v}"
        return f"{float(v):.2f}"
    except Exception:
        return str(v)

# ---------------------------
# Generar una fila por sample
# ---------------------------
def generar_fila_sample(bloque):
    """
    Devuelve una lista con los valores en el orden de columnas:
    [Sample, 1,10,50,100,250,500, Cyclic Stiffness (N/mm),
     Yield Stiffness (N/mm), FMax ATM (N), Max Disp ATM (mm), Force at 2mm (N), Force at 3mm (N)]
    """
    df = bloque.get("df")
    detalles = bloque.get("ciclos", bloque.get("detalles", {})) or {}
    fuerza_max = bloque.get("fuerza_max")
    deformacion_max = bloque.get("deformacion_max")

    # ciclos objetivo (deformación HIGH)
    ciclos_obj = [1, 10, 50, 100, 250, 500]
    valores_ciclos = []

    for cnum in ciclos_obj:
        cd = detalles.get(cnum)
        if cd:
            # intento obtener deform_high_end o deform_high_start o deform_high
            deform_high = _try_get(cd, ["deform_high_end", "deform_high_start", "deform_high"])
            if deform_high is not None:
                valores_ciclos.append(_format_num(deform_high))
                continue
        valores_ciclos.append("—")

    # F2mm y F3mm: basados en LOW del último ciclo (intento obtener último ciclo)
    try:
        ciclos_ordenados = sorted(int(k) for k in detalles.keys())
    except Exception:
        # si keys no son enteras (improbable), fallback simple
        try:
            ciclos_ordenados = sorted([int(k) for k in detalles.keys() if str(k).isdigit()])
        except Exception:
            ciclos_ordenados = []

    if ciclos_ordenados:
        ultimo_ciclo = detalles[ciclos_ordenados[-1]]
        deform_low_last = _try_get(ultimo_ciclo, ["deform_low", "deform_low_start", "low_deform"])
    else:
        ultimo_ciclo = None
        deform_low_last = None

    f2mm_y = None
    f3mm_y = None
    if deform_low_last is not None and df is not None:
        try:
            f2mm_idx = (df["Deformacion"] - deform_low_last - 2.0).abs().idxmin()
            f3mm_idx = (df["Deformacion"] - deform_low_last - 3.0).abs().idxmin()
            f2mm_y = float(df.loc[f2mm_idx, "Fuerza"])
            f3mm_y = float(df.loc[f3mm_idx, "Fuerza"])
        except Exception:
            f2mm_y = None
            f3mm_y = None
    # --------------------------------------------
    # Leer yield_stiffness ya calculado en backend
    # --------------------------------------------
    yield_stiffness = bloque.get("yield_stiffness", None)
    # Cyclic stiffness: usar ciclo 250 si existe
    cyclic_stiffness = None
    cd250 = detalles.get(250)
    if cd250:
        # intentamos extraer forces y displacements desde cd250
        force_high = _try_get(cd250, ["force_high", "f_high", "fuerza_high", "force_peak", "peak_force"])
        force_low = _try_get(cd250, ["force_low", "f_low", "fuerza_low"])
        disp_high = _try_get(cd250, ["deform_high_end", "deform_high_start", "deform_high", "high_deform"])
        disp_low = _try_get(cd250, ["deform_low", "low_deform", "deform_low_start"])
        # si alguno falta, intentamos aproximar buscando en el DF: si dispones de índices guardados en cd250 (p. ej. high_idx, low_idx)
        if None in (force_high, force_low, disp_high, disp_low):
            # intentar leer campos alternativos que podrían guardar índices y buscar en df
            try:
                # intentos de índices
                high_idx = _try_get(cd250, ["high_idx", "deform_high_idx", "high_index"])
                low_idx = _try_get(cd250, ["low_idx", "deform_low_idx", "low_index"])
                if (high_idx is not None) and (low_idx is not None) and (df is not None):
                    # extraer desde df
                    try:
                        force_high = force_high or float(df.loc[int(high_idx), "Fuerza"])
                        force_low = force_low or float(df.loc[int(low_idx), "Fuerza"])
                        disp_high = disp_high or float(df.loc[int(high_idx), "Deformacion"])
                        disp_low = disp_low or float(df.loc[int(low_idx), "Deformacion"])
                    except Exception:
                        pass
            except Exception:
                pass

        # Si ya tenemos los cuatro valores, calcular
        if None not in (force_high, force_low, disp_high, disp_low):
            try:
                assert force_high is not None
                assert force_low is not None
                assert disp_high is not None
                assert disp_low is not None
                denom = float(disp_high) - float(disp_low)
                if denom != 0:
                    cyclic_stiffness = (float(force_high) - float(force_low)) / denom
            except Exception:
                cyclic_stiffness = None

    # Fmax ATM y Max Disp ATM
    fmax_atm = fuerza_max
    max_disp_atm = deformacion_max

    fila = []
    # Sample name
    fila.append(bloque.get("titulo", "Sample"))
    # columnas 1,10,50,100,250,500 (deform high)
    fila.extend(valores_ciclos)
    # Cyclic Stiffness
    fila.append(_format_num(cyclic_stiffness) if cyclic_stiffness is not None else "—")
    # Yield Stiffness (stf)
    fila.append(_format_num(yield_stiffness) if yield_stiffness is not None else "—")
    # FMax ATM
    fila.append(_format_num(fmax_atm) if fmax_atm is not None else "—")
    # Max Disp ATM
    fila.append(_format_num(max_disp_atm) if max_disp_atm is not None else "—")
    # Force at 2mm y 3mm
    fila.append(_format_num(f2mm_y) if f2mm_y is not None else "—")
    fila.append(_format_num(f3mm_y) if f3mm_y is not None else "—")
  # Guardar yield_stiffness en el bloque (por si el bloque se reusa en otras partes)
    try:
        # guardamos None si no existe para que otros consumidores lo lean
        bloque["yield_stiffness"] = yield_stiffness
    except Exception:
        pass

    return fila


def generar_tablas_combinadas(bloques):
    """
    Genera dos tablas combinadas: Cyclic y 3rd Phase.
    Cada tabla tiene una fila por sample (bloque).
    """
    # Columnas Cyclic
    ciclos_col = [0, 10, 50, 100, 250, 500]
    headers_cyclic = [str(c) for c in ciclos_col] + ["Cyclic Stiffness (N/mm)"]

    # Columnas 3rd Phase
    headers_3rd = ["Yield Stiffness (N/mm)", "FMax ATM (N)", "Max Disp ATM (mm)", "Force at 2mm (N)", "Force at 3mm (N)"]

    filas_cyclic = []
    filas_3rd = []

    for bloque in bloques:
        df = bloque["df"]
        detalles_ciclos = bloque["ciclos"]
        fuerza_max = bloque["fuerza_max"]
        deformacion_max = bloque["deformacion_max"]
        yield_stiffness = bloque.get("yield_stiffness", "—")

        primer_ciclo = detalles_ciclos[min(detalles_ciclos.keys())]
        ultimo_ciclo = detalles_ciclos[max(detalles_ciclos.keys())]

        # --- Cyclic ---
        fila_cyclic = []
        for c in ciclos_col:
            if c in detalles_ciclos:
                fila_cyclic.append(f"{detalles_ciclos[c]['deform_high_end']:.2f}")
            elif c == 0:
                fila_cyclic.append(f"{primer_ciclo['deform_high_start']:.2f}")
            else:
                fila_cyclic.append("—")
        df_max_rel = deformacion_max - ultimo_ciclo["deform_low"]
        cyclic_stiffness = fuerza_max / df_max_rel if df_max_rel != 0 else "—"
        fila_cyclic.append(f"{cyclic_stiffness:.2f}")
        filas_cyclic.append(fila_cyclic)

        # --- 3rd Phase ---
        f2mm_idx = (df["Deformacion"] - ultimo_ciclo["deform_low"] - 2.0).abs().idxmin()
        f3mm_idx = (df["Deformacion"] - ultimo_ciclo["deform_low"] - 3.0).abs().idxmin()
        f2mm_y = float(df.loc[f2mm_idx, "Fuerza"])
        f3mm_y = float(df.loc[f3mm_idx, "Fuerza"])
       
        max_disp_atm = deformacion_max

        fila_3rd = [
            f"{yield_stiffness:.2f}" if yield_stiffness != "—" else "—",
            f"{fuerza_max:.2f}",
            f"{max_disp_atm:.2f}",
            f"{f2mm_y:.2f}",
            f"{f3mm_y:.2f}"
        ]
        filas_3rd.append(fila_3rd)

    return (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd)

