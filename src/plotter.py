import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, fuerza_max, deformacion_max, output_path=None):
    """
    Plotea la curva de Fuerza vs Deformación con marcadores:
    - Inicio primer ciclo (HIGH) → rojo
    - Último HIGH de todos los ciclos → azul
    - Fmax → naranja
    - F2mm → verde
    - F3mm → rojo/oscuro
    """
    plt.figure(figsize=(10, 6))
    plt.plot(df["Deformacion"], df["Fuerza"], color='black', lw=1, label="Curva")

    # -----------------------------
    # ORDENAR CICLOS
    # -----------------------------
    ciclos_ordenados = [detalles_ciclos[k] for k in sorted(detalles_ciclos.keys())]

    # -----------------------------
    # PRIMER HIGH
    # -----------------------------
    primer_ciclo = ciclos_ordenados[0]
    idx_primer_high = primer_ciclo["pico_inicio_idx"]

    plt.scatter(primer_ciclo['deform_high_start'],
                df.loc[idx_primer_high, "Fuerza"],
                color="red", s=50, label="High inicio")

    # -----------------------------
    # ÚLTIMO HIGH REAL
    # -----------------------------
    ultimo_high_val = max(c['deform_high_end'] for c in detalles_ciclos.values())
    idx_ultimo_high = df["Deformacion"].sub(ultimo_high_val).abs().idxmin()

    plt.scatter(ultimo_high_val,
                df.loc[idx_ultimo_high, "Fuerza"],
                color="blue", s=50, label="Último HIGH real")

    # -----------------------------
    # Fmax
    # -----------------------------
    idx_fmax = df["Fuerza"].sub(fuerza_max).abs().idxmin()

    plt.scatter(df.loc[idx_fmax, "Deformacion"],
                fuerza_max,
                color="orange", s=60, label="Fuerza máxima")

    # -----------------------------
    # F2mm y F3mm
    # -----------------------------
    ultimo_ciclo_key = sorted(detalles_ciclos.keys())[-1]
    ultimo_ciclo = detalles_ciclos[ultimo_ciclo_key]
    deform_low_last = ultimo_ciclo["deform_low"]

    # Cálculo igual que en PDF
    idx_f2mm = (df["Deformacion"] - deform_low_last - 2.0).abs().idxmin()
    idx_f3mm = (df["Deformacion"] - deform_low_last - 3.0).abs().idxmin()

    f2mm_x = df.loc[idx_f2mm, "Deformacion"]
    f2mm_y = df.loc[idx_f2mm, "Fuerza"]

    f3mm_x = df.loc[idx_f3mm, "Deformacion"]
    f3mm_y = df.loc[idx_f3mm, "Fuerza"]

    # Scatter visibles
    plt.scatter(f2mm_x, f2mm_y, s=70, color="green", label="F2mm")
    plt.scatter(f3mm_x, f3mm_y, s=70, color="darkred", label="F3mm")

    # -----------------------------
    # FORMATO GENERAL
    # -----------------------------
    plt.xlabel("Deformación [mm]")
    plt.ylabel("Fuerza [N]")
    plt.title("Curva Fuerza vs Deformación")
    plt.legend()
    plt.grid(True)

    # Guardar en buffer si corresponde
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.close()
