from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.pdf_generator import generar_pdf

# -------------------------------
# Archivo CSV
# -------------------------------
archivo_csv = "datasets/500Ciclos+Pullout_7.csv"
df = cargar_y_preparar_csv(archivo_csv)

# -------------------------------
# Input del usuario
# -------------------------------
print("\n--- Configuración del ciclo ---")
HIGH = float(input("Introduce el valor alto del ciclo (HIGH, N): "))
LOW = float(input("Introduce el valor bajo del ciclo (LOW, N): "))
TOL = float(input("Introduce tolerancia (ej. 5 o 10): "))

# -------------------------------
# Detectar ciclos
# -------------------------------
ciclos_totales, detalles = detectar_ciclos(df, HIGH, LOW, TOL)

print(f"\nNúmero total de ciclos detectados: {ciclos_totales}")

# Seleccionar ciclos específicos
targets = [100, 250, 500]
ciclos_seleccionados = {}

for t in targets:
    ciclo_data = next((x for x in detalles if x["ciclo"] == t), None)
    if ciclo_data:
        ciclos_seleccionados[t] = ciclo_data
        print(f"\nCiclo {t}: HIGH={ciclo_data['deform_high']:.6f}, LOW={ciclo_data['deform_low']:.6f}")
    else:
        print(f"\n⚠ Ciclo {t} no existe.")

# -------------------------------
# Gráfico
# -------------------------------
grafico_file = plot_ciclos(df, detalles, HIGH, LOW)

# -------------------------------
# Generar PDF
# -------------------------------
pdf_file = generar_pdf(ciclos_totales, ciclos_seleccionados, grafico_file)

print(f"\nPDF generado correctamente: {pdf_file}")
