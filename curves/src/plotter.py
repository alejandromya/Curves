import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def plot_ciclos(df, detalles_ciclos, fuerza_max, deformacion_max,
                f2mm_x, f2mm_y, f3mm_x, f3mm_y, output_path=None):
    """
    Generates a Force–Displacement plot with:
    - Truncation up to Fmax displacement + 3 mm
    - Cyclic start high point (red)
    - Last actual cyclic high point (blue)
    - Maximum force Fmax (orange)
    - Force at 2 mm displacement (green)
    - Force at 3 mm displacement (brown)
    """

    plt.figure(figsize=(10, 6))

    # ================================
    # 1) Plot limit: Fmax displacement + 3 mm
    # ================================
    plot_limit = deformacion_max + 3.0
    df_plot = df[df["Deformacion"] <= plot_limit]

    # ================================
    # 2) Truncated curve
    # ================================
    plt.plot(
        df_plot["Deformacion"],
        df_plot["Fuerza"],
        color="black",
        lw=1,
        label="Truncated Force–Displacement Curve"
    )

    # ================================
    # 3) Cyclic start high point
    # ================================
    first_key = min(detalles_ciclos.keys())
    first_cycle = detalles_ciclos[first_key]
    idx_first = first_cycle["pico_inicio_idx"]

    plt.scatter(
        first_cycle["deform_high_start"],
        df.loc[idx_first, "Fuerza"],
        color="red",
        s=40,
        label="Cyclic Start (High Point)"
    )

    # ================================
    # 4) Last actual cyclic high point
    # ================================
    last_high_real = max(
        c["deform_high_end"] for c in detalles_ciclos.values()
    )
    idx_last = df["Deformacion"].sub(last_high_real).abs().idxmin()

    plt.scatter(
        last_high_real,
        df.loc[idx_last, "Fuerza"],
        color="blue",
        s=40,
        label="Cyclic End (High Point)"
    )

    # ================================
    # 5) Absolute maximum force (Fmax)
    # ================================
    idx_fmax = df["Fuerza"].sub(fuerza_max).abs().idxmin()

    plt.scatter(
        df.loc[idx_fmax, "Deformacion"],
        fuerza_max,
        color="orange",
        s=50,
        label="Maximum Force (Fmax)"
    )

    # ================================
    # 6) Force at 2 mm displacement
    # ================================
    plt.scatter(
        f2mm_x,
        f2mm_y,
        s=50,
        color="green",
        label="Force at 2 mm (F₂mm)"
    )

    # ================================
    # 7) Force at 3 mm displacement
    # ================================
    plt.scatter(
        f3mm_x,
        f3mm_y,
        s=50,
        color="brown",
        label="Force at 3 mm (F₃mm)"
    )

    # ================================
    # 8) Plot styling
    # ================================
    plt.xlabel("Displacement [mm]")
    plt.ylabel("Force [N]")
    plt.title("Force–Displacement Curve (Truncated at Fmax + 3 mm)")
    plt.grid(True)
    plt.legend()

    # ================================
    # 9) Save figure
    # ================================
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.close()