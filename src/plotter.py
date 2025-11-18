import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, HIGH, LOW, output_path="grafico_temp.png"):
    """
    Genera y guarda un gráfico Fuerza vs Deformación con puntos HIGH y LOW.

    Parámetros:
        df: DataFrame con columnas "Deformacion" y "Fuerza".
        detalles_ciclos: lista de diccionarios con 'deform_high' y 'deform_low' por ciclo.
        HIGH: lista de valores de fuerza correspondiente a cada deform_high.
        LOW: lista de valores de fuerza correspondiente a cada deform_low.
        output_path: ruta del archivo PNG de salida.

    Retorna:
        output_path: ruta del archivo generado.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(df["Deformacion"], df["Fuerza"], linewidth=0.8, label="Datos completos")

    # Marcar puntos HIGH y LOW asegurando que x e y tengan la misma longitud
    for i, c in enumerate(detalles_ciclos):
        y_high = HIGH[i] if isinstance(HIGH, list) else HIGH
        y_low = LOW[i] if isinstance(LOW, list) else LOW
        plt.scatter(c["deform_high"], y_high, color="red", s=20, label="HIGH detectado" if i == 0 else "")
        plt.scatter(c["deform_low"], y_low, color="blue", s=20, label="LOW detectado" if i == 0 else "")

    plt.title("Gráfica Deformación vs Fuerza")
    plt.xlabel("Deformación (mm)")
    plt.ylabel("Fuerza (N)")
    plt.grid(True)

    # Mostrar leyenda sin duplicados
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path
