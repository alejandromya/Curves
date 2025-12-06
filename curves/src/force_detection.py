def detectar_fuerza_maxima(df, detalles_ciclos, limite_desplazamiento=1.0):
    """
    Detecta la fuerza máxima real después del ciclado y calcula F a 2mm y 3mm
    desde el valle final del último ciclo.
    Devuelve: fuerza_max, deformacion_max, f2mm_x, f2mm_y, f3mm_x, f3mm_y
    """
    # Si no hay ciclos, usamos máximo global
    if not detalles_ciclos:
        idx = df["Fuerza"].idxmax()
        f_max = df.loc[idx, "Fuerza"]
        d_max = df.loc[idx, "Deformacion"]
        deform_low = df["Deformacion"].min()
        f2mm_idx = (df["Deformacion"] - deform_low - 2.0).abs().idxmin()
        f3mm_idx = (df["Deformacion"] - deform_low - 3.0).abs().idxmin()
        f2mm_x = df.loc[f2mm_idx, "Deformacion"]
        f2mm_y = df.loc[f2mm_idx, "Fuerza"]
        f3mm_x = df.loc[f3mm_idx, "Deformacion"]
        f3mm_y = df.loc[f3mm_idx, "Fuerza"]
        return f_max, d_max, f2mm_x, f2mm_y, f3mm_x, f3mm_y

    # Ordenar ciclos y tomar último
    ciclos_ordenados = [detalles_ciclos[k] for k in sorted(detalles_ciclos)]
    ultimo = ciclos_ordenados[-1]

    deform_low_last = ultimo["deform_low"]

    # ===========================================
    # Punto desde el que empieza el pullout
    deform_inicio_busqueda = ultimo['deform_low']

    # Filtrar datos posteriores al valle
    df2 = df[df["Deformacion"] > deform_inicio_busqueda].copy()
    df2 = df2.reset_index(drop=True)

    if df2.empty:
        idx = df["Fuerza"].idxmax()
        f_max = df.loc[idx, "Fuerza"]
        d_max = df.loc[idx, "Deformacion"]
    else:
        f_max = df2.loc[0, "Fuerza"]
        d_max = df2.loc[0, "Deformacion"]
        for i in range(1, len(df2)):
            f = df2.loc[i, "Fuerza"]
            d = df2.loc[i, "Deformacion"]
            if f > f_max:
                if abs(d - d_max) > limite_desplazamiento:
                    break  # máximo real alcanzado
                f_max = f
                d_max = d

    # F2mm y F3mm desde deform_low del último ciclo
    f2mm_idx = (df["Deformacion"] - deform_inicio_busqueda - 2.0).abs().idxmin()
    f3mm_idx = (df["Deformacion"] - deform_inicio_busqueda - 3.0).abs().idxmin()
    f2mm_x = df.loc[f2mm_idx, "Deformacion"]
    f2mm_y = df.loc[f2mm_idx, "Fuerza"]
    f3mm_x = df.loc[f3mm_idx, "Deformacion"]
    f3mm_y = df.loc[f3mm_idx, "Fuerza"]

        # ===========================================
    # CÁLCULO CORRECTO DEL YIELD STIFFNESS
    # ===========================================
    yield_stiffness = None
    try:
        delta_disp = d_max - deform_low_last
        if delta_disp != 0:
            yield_stiffness = f_max / delta_disp
    except:
        yield_stiffness = None

    return f_max, d_max, f2mm_x, f2mm_y, f3mm_x, f3mm_y, yield_stiffness
