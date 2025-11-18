def detectar_ciclos(df, HIGH, LOW, TOL):
    """
    Detecta ciclos HIGH→LOW y devuelve:
        - total de ciclos
        - lista de dicts: {ciclo, deform_high, deform_low}
    """

    arriba = False
    ciclos = 0
    detalles = []
    deform_high = None

    for i in range(len(df)):
        f = df.loc[i, "Fuerza"]
        d = df.loc[i, "Deformacion"]

        # Detecta HIGH
        if not arriba and (HIGH - TOL <= f <= HIGH + TOL):
            arriba = True
            deform_high = d

        # Detecta LOW (fin de ciclo)
        if arriba and (LOW - TOL <= f <= LOW + TOL):
            ciclos += 1
            detalles.append({
                "ciclo": ciclos,
                "deform_high": deform_high,
                "deform_low": d
            })
            arriba = False

    return ciclos, detalles
