def detectar_fuerza_maxima(df, detalles_ciclos=None):
    """
    Detecta el punto de fuerza máxima válido después del último ciclo completo (High→Low→High).
    Se toma el máximo global de la sección posterior al último ciclo.
    """

    if not detalles_ciclos:
        idx_max = df["Fuerza"].idxmax()
        return df.loc[idx_max, "Fuerza"], df.loc[idx_max, "Deformacion"]

    # Último ciclo
    ciclos_ordenados = [detalles_ciclos[k] for k in sorted(detalles_ciclos.keys())]
    ultimo_ciclo = ciclos_ordenados[-1]

    # Filtrar datos después del último High final del ciclo
    deform_inicio_busqueda = ultimo_ciclo['deform_high_end']
    df_filtrado = df[df["Deformacion"] > deform_inicio_busqueda]

    if df_filtrado.empty:
        idx_max = df["Fuerza"].idxmax()
        return df.loc[idx_max, "Fuerza"], df.loc[idx_max, "Deformacion"]

    # Tomar máximo global en la sección filtrada
    idx_max = df_filtrado["Fuerza"].idxmax()
    return df_filtrado.loc[idx_max, "Fuerza"], df_filtrado.loc[idx_max, "Deformacion"]
