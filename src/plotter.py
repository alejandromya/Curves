import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, fuerza_max, deformacion_max,
                f2mm_x, f2mm_y, f3mm_x, f3mm_y, output_path=None):
    """
    Genera la gráfica con:
    - Recorte hasta 1 mm más que la deformación en Fmax
    - High inicio (rojo)
    - Último HIGH real (azul)
    - Fmax (naranja)
    - F2mm (verde)
    - F3mm (marrón)
    """

    plt.figure(figsize=(10,6))

    # ================================
    # 1) Límite gráfico: Fmax + 1 mm
    # ================================
    limite_plot = deformacion_max + 3.0
    df_plot = df[df["Deformacion"] <= limite_plot]

    # ================================
    # 2) Dibujar la curva recortada
    # ================================
    plt.plot(df_plot["Deformacion"], df_plot["Fuerza"],
             color='black', lw=1, label="Curva recortada")

    # ================================
    # 3) High inicio (primer ciclo)
    # ================================
    primer_key = min(detalles_ciclos.keys())
    primer_ciclo = detalles_ciclos[primer_key]
    idx_primer = primer_ciclo["pico_inicio_idx"]

    plt.scatter(
        primer_ciclo["deform_high_start"],
        df.loc[idx_primer, "Fuerza"],
        color="red", s=40, label="High inicio"
    )

    # ================================
    # 4) Último HIGH real
    # ================================
    ultimo_high_real = max(c["deform_high_end"] for c in detalles_ciclos.values())
    idx_ultimo = df["Deformacion"].sub(ultimo_high_real).abs().idxmin()

    plt.scatter(
        ultimo_high_real,
        df.loc[idx_ultimo, "Fuerza"],
        color="blue", s=40, label="Último HIGH"
    )

    # ================================
    # 5) Fmax absoluto
    # ================================
    idx_fmax = df["Fuerza"].sub(fuerza_max).abs().idxmin()

    plt.scatter(
        df.loc[idx_fmax, "Deformacion"],
        fuerza_max,
        color="orange", s=50, label="Fmax"
    )

    # ================================
    # 6) F2mm
    # ================================
    plt.scatter(
        f2mm_x, f2mm_y,
        s=50, color="green", label="F2mm"
    )

    # ================================
    # 7) F3mm
    # ================================
    plt.scatter(
        f3mm_x, f3mm_y,
        s=50, color="brown", label="F3mm"
    )

    # ================================
    # 8) Estética
    # ================================
    plt.xlabel("Deformación [mm]")
    plt.ylabel("Fuerza [N]")
    plt.title("Curva Fuerza vs Deformación (recortada a Fmax + 1 mm)")
    plt.grid(True)
    plt.legend()

    # ================================
    # 9) Guardar
    # ================================
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.close()