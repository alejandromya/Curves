import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, fuerza_max, deformacion_max, output_path=None):
    """
    Plotea la curva de Fuerza vs Deformación con marcadores:
    - Inicio primer ciclo (HIGH) → rojo
    - Último HIGH de todos los ciclos → azul
    - Fmax → naranja
    """
    plt.figure(figsize=(10,6))
    plt.plot(df["Deformacion"], df["Fuerza"], color='black', lw=1, label="Curva")

    # Ordenar ciclos
    ciclos_ordenados = [detalles_ciclos[k] for k in sorted(detalles_ciclos.keys())]

    # MARCAR: inicio del primer ciclo (HIGH)
    primer_ciclo = ciclos_ordenados[0]
    idx_primer_high = primer_ciclo["pico_inicio_idx"]
    plt.scatter(primer_ciclo['deform_high_start'], df.loc[idx_primer_high, "Fuerza"],
                color="red", s=40, label="High inicio")

    # MARCAR: último HIGH de todos los ciclos
    ultimo_high_val = max(c['deform_high_end'] for c in detalles_ciclos.values())
    # Buscar índice aproximado en df
    idx_ultimo_high = df["Deformacion"].sub(ultimo_high_val).abs().idxmin()
    plt.scatter(ultimo_high_val, df.loc[idx_ultimo_high, "Fuerza"],
                color="blue", s=40, label="Último HIGH")

    # MARCAR: fuerza máxima
    # Buscar índice aproximado
    idx_fmax = df["Fuerza"].sub(fuerza_max).abs().idxmin()
    plt.scatter(df.loc[idx_fmax, "Deformacion"], fuerza_max,
                color="orange", s=40, label="Fuerza máxima")

    plt.xlabel("Deformación [mm]")
    plt.ylabel("Fuerza [N]")
    plt.title("Curva Fuerza vs Deformación")
    plt.legend()
    plt.grid(True)

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()