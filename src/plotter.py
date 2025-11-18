import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, HIGH, LOW, output_path=None):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Deformacion"], df["Fuerza"], linewidth=0.8, label="Datos completos")

    for i, c in enumerate(detalles_ciclos):
        y_high = HIGH[i] if isinstance(HIGH, list) else HIGH
        y_low = LOW[i] if isinstance(LOW, list) else LOW
        plt.scatter(c["deform_high"], y_high, color="red", s=20, label="HIGH detectado" if i == 0 else "")
        plt.scatter(c["deform_low"], y_low, color="blue", s=20, label="LOW detectado" if i == 0 else "")

    plt.title("Gráfica Deformación vs Fuerza")
    plt.xlabel("Deformación (mm)")
    plt.ylabel("Fuerza (N)")
    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150)
    plt.close()
    
    return output_path
