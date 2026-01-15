
# ============================================================
# HELPERS
# ============================================================

def _format_num(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):.2f}"
    except Exception:
        return str(v)


# ============================================================
# FILA POR SAMPLE
# ============================================================

def generar_fila_sample(bloque):
    df = bloque.get("df")
    detalles = bloque.get("ciclos", {})
    n_ciclos = bloque.get("n_ciclos", 0)

    fuerza_max = bloque.get("fuerza_max")
    deformacion_max = bloque.get("deformacion_max")

    ciclos_obj = [1, 10, 50, 100, 250, 500]
    valores_ciclos = []

    for c in ciclos_obj:
        cd = detalles.get(c)

        if cd is None and n_ciclos == c - 1:
            cd = detalles.get(c - 1)

        valores_ciclos.append(_format_num(cd.get("deform_high_end") if cd else None))

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

    cd250 = detalles.get(250)
    if cd250 is None and n_ciclos == 249:
        cd250 = detalles.get(249)

    cyclic_stiffness = cd250.get("cyclic_stiffness") if cd250 else None
    bloque["cyclic_stiffness"] = cyclic_stiffness

    return [
        bloque.get("titulo", "Sample"),
        *valores_ciclos,
        _format_num(cyclic_stiffness),
        _format_num(bloque.get("yield_stiffness")),
        _format_num(fuerza_max),
        _format_num(deformacion_max),
        _format_num(f2mm_y),
        _format_num(f3mm_y),
    ]


# ============================================================
# TABLAS COMBINADAS
# ============================================================

def generar_tablas_combinadas(bloques):
    """
    Genera tablas combinadas listas para Excel, incluyendo
    una columna extra con el nombre del sample.
    Devuelve:
        (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd)
    """

    # Columnas de las tablas
    headers_cyclic = ["Sample", "0", "10", "50", "100", "250", "500", "Cyclic Stiffness (N/mm)"]
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
        detalles = b.get("ciclos", {})
        df = b.get("df")

        # Primer y último ciclo
        primer = detalles.get(min(detalles.keys()), {})
        ultimo = detalles.get(max(detalles.keys()), {})

        # Celdas de 250 y 500 ciclos
        cd250 = detalles.get(250) or detalles.get(249)
        cd500 = detalles.get(500) or detalles.get(499) or detalles.get(498)

        cyclic_stiffness = cd250.get("cyclic_stiffness") if cd250 else None

        # Construir fila cyclic con columna extra del sample
        filas_cyclic.append([
            b.get("titulo", "Sample"),
            _format_num(primer.get("deform_high_start")),
            _format_num(detalles.get(10, {}).get("deform_high_end")),
            _format_num(detalles.get(50, {}).get("deform_high_end")),
            _format_num(detalles.get(100, {}).get("deform_high_end")),
            _format_num(cd250.get("deform_high_end") if cd250 else None),
            _format_num(cd500.get("deform_high_end") if cd500 else None),
            _format_num(cyclic_stiffness),
        ])

        # Calcular fuerzas a 2mm y 3mm
        deform_low = ultimo.get("deform_low")
        f2mm_y = f3mm_y = None
        if deform_low is not None and df is not None:
            try:
                f2_idx = (df["Deformacion"] - deform_low - 2).abs().idxmin()
                f3_idx = (df["Deformacion"] - deform_low - 3).abs().idxmin()
                f2mm_y = df.loc[f2_idx, "Fuerza"]
                f3mm_y = df.loc[f3_idx, "Fuerza"]
            except Exception:
                pass

        filas_3rd.append([
            _format_num(b.get("yield_stiffness")),
            _format_num(b.get("fuerza_max")),
            _format_num(b.get("deformacion_max")),
            _format_num(f2mm_y),
            _format_num(f3mm_y),
        ])

    return (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd)