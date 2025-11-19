def detectar_fuerza_maxima(df, detalles_ciclos, limite_desplazamiento=1.0):
    """
    Detecta la fuerza máxima real después del ciclado.
    Reglas:
      - La deformación después del valle final del último ciclo siempre es creciente.
      - Mientras F sube, el máximo se actualiza.
      - Si F cae → el máximo sigue siendo el anterior.
      - Si luego aparece una F mayor, se compara su deformación con la del máximo previo:
            * si Δdeform > 1 mm → el máximo cierto es el anterior (se acabó).
            * si Δdeform <= 1 mm → nuevo máximo válido.
    """

    # Si no hay ciclos, max global
    if not detalles_ciclos:
        idx = df["Fuerza"].idxmax()
        return df.loc[idx, "Fuerza"], df.loc[idx, "Deformacion"]

    # Ordenar y tomar último ciclo
    ciclos_ordenados = [detalles_ciclos[k] for k in sorted(detalles_ciclos)]
    ultimo = ciclos_ordenados[-1]

    # Punto desde el que empieza realmente el pullout (el valle final)
    deform_inicio_busqueda = ultimo['deform_low']

    # Filtrar datos posteriores al valle
    df2 = df[df["Deformacion"] > deform_inicio_busqueda].copy()
    df2 = df2.reset_index(drop=True)

    if df2.empty:
        idx = df["Fuerza"].idxmax()
        return df.loc[idx, "Fuerza"], df.loc[idx, "Deformacion"]

    # Primer punto como candidato inicial
    fuerza_max = df2.loc[0, "Fuerza"]
    deform_max = df2.loc[0, "Deformacion"]

    # Recorremos toda la región post-ciclado
    for i in range(1, len(df2)):
        f = df2.loc[i, "Fuerza"]
        d = df2.loc[i, "Deformacion"]

        if f > fuerza_max:
            # Si es mayor, verificar la distancia en deformación
            if abs(d - deform_max) > limite_desplazamiento:
                # Demasiado lejos → el máximo verdadero es el anterior
                return fuerza_max, deform_max

            # Si está dentro de 1 mm, actualizar
            fuerza_max = f
            deform_max = d

        elif f < fuerza_max:
            # Si cae y nunca vuelve a subir más allá del umbral, se quedará ahí
            # pero seguimos por si aparece un nuevo máximo dentro del rango
            pass

    return fuerza_max, deform_max
