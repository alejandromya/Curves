import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, fuerza_max, deform_max, output_path=None):
    """
    Grafica la curva Fuerza vs Deformacion y marca:
    - High inicio del primer ciclo (rojo)
    - Low del último ciclo (azul)
    - Fuerza máxima fuera del ciclo (naranja)
    """

    plt.figure(figsize=(10,5))
    # Curva completa
    plt.plot(df["Deformacion"], df["Fuerza"], linewidth=0.8, label="Datos completos", color="gray")

    # Primer ciclo: High inicio
    primer_ciclo = detalles_ciclos[min(detalles_ciclos.keys())]
    deform_high_start = primer_ciclo['deform_high_start']
    fuerza_high_start = df.loc[(df["Deformacion"] - deform_high_start).abs().idxmin(), "Fuerza"]
    plt.scatter(deform_high_start, fuerza_high_start, color="red", s=50, label="High inicio primer ciclo")

    # Último ciclo: Low final
    ultimo_ciclo = detalles_ciclos[max(detalles_ciclos.keys())]
    deform_low_end = ultimo_ciclo['deform_low']
    fuerza_low_end = df.loc[(df["Deformacion"] - deform_low_end).abs().idxmin(), "Fuerza"]
    plt.scatter(deform_low_end, fuerza_low_end, color="blue", s=50, label="Low último ciclo")

    # Fuerza máxima fuera del ciclo
    plt.scatter(deform_max, fuerza_max, color="orange", s=50, label="Fuerza máxima")

    # Configuración del gráfico
    plt.title("Gráfica Deformación vs Fuerza")
    plt.xlabel("Deformación (mm)")
    plt.ylabel("Fuerza (N)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Guardar si se indica
    if output_path:
        plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path