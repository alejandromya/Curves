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


def _rel(v, base):
    """
    Devuelve v relativo a base.
    Si alguno es None → None
    """
    if v is None or base is None:
        return None
    try:
        return v - base
    except Exception:
        return None


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
    headers_cyclic = [
        "Sample",
        "0",
        "10",
        "50",
        "100",
        "250",
        "500",
        "Cyclic Stiffness (N/mm)",
    ]

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

        # Base (ciclo 0)
        base_0 = primer.get("deform_high_start")

        # Celdas 250 y 500
        cd250 = detalles.get(250) or detalles.get(249)
        cd500 = detalles.get(500) or detalles.get(499) or detalles.get(498)

        cyclic_stiffness = cd250.get("cyclic_stiffness") if cd250 else None

        # ===============================
        # TABLA CYCLIC (RELATIVA A 0)
        # ===============================

        filas_cyclic.append([

            b.get("titulo", "Sample"),

            # Ciclo 0 → siempre 0
            _format_num(0),

            # Resto → relativo al ciclo 0
            _format_num(
                _rel(detalles.get(10, {}).get("deform_high_end"), base_0)
            ),

            _format_num(
                _rel(detalles.get(50, {}).get("deform_high_end"), base_0)
            ),

            _format_num(
                _rel(detalles.get(100, {}).get("deform_high_end"), base_0)
            ),

            _format_num(
                _rel(cd250.get("deform_high_end") if cd250 else None, base_0)
            ),

            _format_num(
                _rel(cd500.get("deform_high_end") if cd500 else None, base_0)
            ),

            _format_num(cyclic_stiffness),
        ])

        # ===============================
        # TABLA 3RD
        # ===============================

        # Calcular fuerzas a 2mm y 3mm
        deform_low = ultimo.get("deform_low")

        f2mm_y = None
        f3mm_y = None

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
