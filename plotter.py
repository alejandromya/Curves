import matplotlib.pyplot as plt

def generar_grafico(df, detalles_ciclos, HIGH, LOW, output_path="grafico_temp.png"):
    """
    Genera y guarda un gráfico Fuerza vs Deformación.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(df["Deformacion"], df["Fuerza"], linewidth=0.8, label="Datos completos")

    # Marcar puntos HIGH y LOW
    for c in detalles_ciclos:
        plt.scatter(c["deform_high"], HIGH, color="red", s=5)
        plt.scatter(c["deform_low"], LOW, color="blue", s=5)

    plt.title("Gráfica Deformación vs Fuerza")
    plt.xlabel("Deformación (mm)")
    plt.ylabel("Fuerza (N)")
    plt.grid(True)
    plt.legend(["Datos completos", "HIGH detectado", "LOW detectado"])
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path
