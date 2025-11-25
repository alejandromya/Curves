import os
import io
import sys
from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf_unico

# Parámetros desde servidor
pico = float(sys.argv[1])
valle = float(sys.argv[2])
toler = float(sys.argv[3])
columna = sys.argv[4]  # columna dinámica

input_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend", "uploads", f"col{columna}")
)
output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "results"))
os.makedirs(output_folder, exist_ok=True)

bloques_pdf = []

# Procesar únicamente los CSVs de la carpeta de la columna
for archivo in os.listdir(input_folder):
    if not archivo.lower().endswith(".csv"):
        continue

    archivo_path = os.path.join(input_folder, archivo)
    df = cargar_y_preparar_csv(archivo_path)
    ciclos_totales, detalles = detectar_ciclos(df, pico, valle, toler)
    if ciclos_totales == 0:
        continue

    fuerza_max, deformacion_max = detectar_fuerza_maxima(df, detalles)
    ciclos_ordenados = sorted(detalles.keys())
    ultimo_ciclo = detalles[ciclos_ordenados[-1]]

    deform_low_last = ultimo_ciclo["deform_low"]
    f2mm_idx = (df["Deformacion"] - deform_low_last - 2.0).abs().idxmin()
    f3mm_idx = (df["Deformacion"] - deform_low_last - 3.0).abs().idxmin()

    f2mm_x, f2mm_y = float(df.loc[f2mm_idx, "Deformacion"]), float(df.loc[f2mm_idx, "Fuerza"])
    f3mm_x, f3mm_y = float(df.loc[f3mm_idx, "Deformacion"]), float(df.loc[f3mm_idx, "Fuerza"])

    grafico_memoria = io.BytesIO()
    plot_ciclos(df, detalles, fuerza_max, deformacion_max,
                f2mm_x, f2mm_y, f3mm_x, f3mm_y,
                output_path=grafico_memoria)
    grafico_memoria.seek(0)

    bloques_pdf.append({
        "titulo": archivo,
        "total_ciclos": ciclos_totales,
        "ciclos": detalles,
        "grafico": grafico_memoria,
        "fuerza_max": fuerza_max,
        "deformacion_max": deformacion_max,
        "df": df,
        "f2mm_x": f2mm_x,
        "f2mm_y": f2mm_y,
        "f3mm_x": f3mm_x,
        "f3mm_y": f3mm_y
    })

pdf_path = os.path.join(output_folder, f"INFORME_COL{columna}.pdf")
generar_pdf_unico(bloques_pdf, pdf_path)
print(f"PDF generado: {pdf_path}")