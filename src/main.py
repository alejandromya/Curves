from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.pdf_generator import generar_pdf

# -------------------------------
# Archivo CSV
# -------------------------------
archivo_csv = "datasets/500Ciclos+Pullout_7.csv"
df = cargar_y_preparar_csv(archivo_csv)

# ==============================
# 2) Detectar ciclos automáticamente
# ==============================
print("\nDetectando ciclos...")

ciclos_totales, detalles = detectar_ciclos(df, min_force=10, smooth_window=5)

print(f"\nNúmero total de ciclos detectados: {ciclos_totales}")

# ==============================
# 3) Selección de ciclos concretos
# ==============================
targets = [100, 200, 300, 400, 500]
ciclos_seleccionados = {}

for t in targets:
        ciclo_data = next((x for x in detalles if x["ciclo"] == t), None)
        if ciclo_data:
            ciclos_seleccionados[t] = ciclo_data
            print(f"\nCiclo {t}:")
            print(f"  HIGH deform: {ciclo_data['deform_high']:.6f}")
            print(f"  LOW deform:  {ciclo_data['deform_low']:.6f}")
        else:
            print(f"\n⚠ Ciclo {t} no existe (solo hay {ciclos_totales})")


# -------------------------------
# Gráfico
# -------------------------------
HIGH = max(d['deform_high'] for d in detalles)
LOW = min(d['deform_low'] for d in detalles)
grafico_file = plot_ciclos(df, detalles, HIGH, LOW)

# -------------------------------
# Generar PDF
# -------------------------------
pdf_file = generar_pdf(ciclos_totales, ciclos_seleccionados, grafico_file)

print(f"\nPDF generado correctamente: {pdf_file}")
