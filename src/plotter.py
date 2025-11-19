import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, output_path=None):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Deformacion"], df["Fuerza"], linewidth=0.8, label="Datos completos")

    for i, c in enumerate(detalles_ciclos.values()):
        # marcar pico inicial, valle y pico final
        plt.scatter(c["deform_high_start"], df.loc[c["pico_inicio_idx"], "Fuerza"],
                    color="red", s=20, label="High inicio" if i == 0 else "")
        plt.scatter(c["deform_low"], df.loc[c["valle_idx"], "Fuerza"],
                    color="blue", s=20, label="Low" if i == 0 else "")
        plt.scatter(c["deform_high_end"], df.loc[c["pico_final_idx"], "Fuerza"],
                    color="orange", s=20, label="High final" if i == 0 else "")

        # unir puntos para visualizar el ciclo
        plt.plot([c["deform_high_start"], c["deform_low"], c["deform_high_end"]],
                 [df.loc[c["pico_inicio_idx"], "Fuerza"],
                  df.loc[c["valle_idx"], "Fuerza"],
                  df.loc[c["pico_final_idx"], "Fuerza"]],
                 color="green", linewidth=0.8)

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