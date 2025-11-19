def detectar_fuerza_maxima(df, detalles_ciclos=None, limite_desplazamiento=1.0):
    """
    Detecta el punto de fuerza máxima válido en el DataFrame.
    Si se proporcionan detalles de ciclos, busca el máximo después del último ciclo.
    
    Lógica: Si después de un máximo la fuerza cae y vuelve a subir más alto,
    ese nuevo máximo solo es válido si el desplazamiento entre ambos es < 1mm.
    Si el desplazamiento es >= 1mm, el máximo válido es el anterior.
    
    Args:
        df: DataFrame con columnas 'Fuerza' y 'Deformacion'
        detalles_ciclos: Lista de ciclos detectados (opcional)
        limite_desplazamiento: Diferencia máxima de deformación entre máximos en mm (por defecto 1.0)
        
    Returns:
        tuple: (fuerza_maxima, deformacion_en_max)
    """
    df_filtrado = df.copy()
    
    # Si hay ciclos detectados, filtrar solo datos después del último ciclo
    if detalles_ciclos and len(detalles_ciclos) > 0:
        ultimo_ciclo = detalles_ciclos[-1]
        deform_ultimo_valle = ultimo_ciclo['deform_low']
        df_filtrado = df_filtrado[df_filtrado["Deformacion"] > deform_ultimo_valle].copy()
    
    if df_filtrado.empty:
        # No hay datos después de los ciclos
        idx_max = df["Fuerza"].idxmax()
        return df.loc[idx_max, "Fuerza"], df.loc[idx_max, "Deformacion"]
    
    # Resetear índices para trabajar más fácilmente
    df_filtrado = df_filtrado.reset_index(drop=True)
    
    # Encontrar todos los máximos locales
    maximos = []
    for i in range(1, len(df_filtrado) - 1):
        f_prev = df_filtrado.loc[i-1, "Fuerza"]
        f = df_filtrado.loc[i, "Fuerza"]
        f_next = df_filtrado.loc[i+1, "Fuerza"]
        
        # Es un máximo local si es mayor que sus vecinos
        if f > f_prev and f > f_next:
            maximos.append({
                'idx': i,
                'fuerza': f,
                'deformacion': df_filtrado.loc[i, "Deformacion"]
            })
    
    # Si no hay máximos locales, usar el máximo global
    if not maximos:
        idx_max = df_filtrado["Fuerza"].idxmax()
        return df_filtrado.loc[idx_max, "Fuerza"], df_filtrado.loc[idx_max, "Deformacion"]
    
    # Ordenar máximos por orden de aparición (ya deberían estarlo)
    maximos.sort(key=lambda x: x['idx'])
    
    # Validar máximos según la regla de desplazamiento
    maximo_valido = maximos[0]  # Empezar con el primer máximo
    
    for i in range(1, len(maximos)):
        maximo_actual = maximos[i]
        
        # Si este máximo es más alto que el válido actual
        if maximo_actual['fuerza'] > maximo_valido['fuerza']:
            # Calcular diferencia de deformación
            diff_deformacion = abs(maximo_actual['deformacion'] - maximo_valido['deformacion'])
            
            # Solo actualizar si la diferencia es menor al límite
            if diff_deformacion < limite_desplazamiento:
                maximo_valido = maximo_actual
            # Si diff >= límite, mantener el máximo anterior (maximo_valido)
        # Si no es más alto, no cambiamos nada
    
    return maximo_valido['fuerza'], maximo_valido['deformacion']