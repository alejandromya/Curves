def detectar_fuerza_maxima(df, detalles_ciclos=None, limite_desplazamiento=1.0):
    """
    Detecta el punto de fuerza máxima válido después del último ciclo.
    """

    if not detalles_ciclos:
        idx_max = df["Fuerza"].idxmax()
        return df.loc[idx_max, "Fuerza"], df.loc[idx_max, "Deformacion"]

    # Convertir dict a lista ordenada
    ciclos_ordenados = [detalles_ciclos[k] for k in sorted(detalles_ciclos.keys())]
    ultimo_ciclo = ciclos_ordenados[-1]
    deform_ultimo_valle = ultimo_ciclo['deform_low']

    df_filtrado = df[df["Deformacion"] > deform_ultimo_valle].copy()
    if df_filtrado.empty:
        idx_max = df["Fuerza"].idxmax()
        return df.loc[idx_max, "Fuerza"], df.loc[idx_max, "Deformacion"]

    df_filtrado = df_filtrado.reset_index(drop=True)

    # Buscar máximos locales
    maximos = []
    for i in range(1, len(df_filtrado) - 1):
        f_prev = df_filtrado.loc[i-1, "Fuerza"]
        f = df_filtrado.loc[i, "Fuerza"]
        f_next = df_filtrado.loc[i+1, "Fuerza"]

        if f > f_prev and f > f_next:
            maximos.append({
                'idx': i,
                'fuerza': f,
                'deformacion': df_filtrado.loc[i, "Deformacion"]
            })

    if not maximos:
        idx_max = df_filtrado["Fuerza"].idxmax()
        return df_filtrado.loc[idx_max, "Fuerza"], df_filtrado.loc[idx_max, "Deformacion"]

    maximos.sort(key=lambda x: x['idx'])
    maximo_valido = maximos[0]

    for i in range(1, len(maximos)):
        max_actual = maximos[i]
        if max_actual['fuerza'] > maximo_valido['fuerza']:
            diff_def = abs(max_actual['deformacion'] - maximo_valido['deformacion'])
            if diff_def < limite_desplazamiento:
                maximo_valido = max_actual

    return maximo_valido['fuerza'], maximo_valido['deformacion']
