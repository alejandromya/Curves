import os
import io
import sys
from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf_unico
from src.excel_generator import agregar_hoja_excel
from src.debug import debug_ciclos
    
# Parámetros desde servidor
pico = float(sys.argv[1])
valle = float(sys.argv[2])
toler = float(sys.argv[3])
columna_actual = sys.argv[4]  # columna dinámica

UPLOAD_FOLDER = "/tmp/uploads"
RESULTS_FOLDER = "/tmp/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Diccionario global para todos los bloques de todas las columnas
bloques_por_columna = {}

# Carpeta de la columna actual
input_folder = os.path.join(UPLOAD_FOLDER, f"col{columna_actual}")
csv_files = sorted(
    [f for f in os.listdir(input_folder) if f.lower().endswith(".csv")]
)
bloques_pdf = []

for archivo in csv_files:
    if not archivo.lower().endswith(".csv"):
        continue

    archivo_path = os.path.join(input_folder, archivo)
    df = cargar_y_preparar_csv(archivo_path)
    ciclos_totales, detalles = detectar_ciclos(df, pico, valle, toler)
    # Convertimos a lista de ciclos para debug
    ciclos_lista = list(detalles.values())
    debug_ciclos(ciclos_lista, debug_filename="debug_main_ciclos.txt")
    

    if ciclos_totales == 0:
        continue


    ciclos_ordenados = sorted(detalles.keys())
    ultimo_ciclo = detalles[ciclos_ordenados[-1]]

    deform_low_last = ultimo_ciclo["deform_low"]
    fuerza_max, deformacion_max, f2mm_x, f2mm_y, f3mm_x, f3mm_y, yield_stiffness = detectar_fuerza_maxima(df, detalles)


    grafico_memoria = io.BytesIO()
    plot_ciclos(df, detalles, fuerza_max, deformacion_max,
                f2mm_x, f2mm_y, f3mm_x, f3mm_y,
                output_path=grafico_memoria)
    grafico_memoria.seek(0)

    bloque = {
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
        "f3mm_y": f3mm_y,
        "yield_stiffness": yield_stiffness
    }
    bloques_pdf.append(bloque)

# Guardar PDF de esta columna
pdf_path = os.path.join(RESULTS_FOLDER, f"INFORME_COL{columna_actual}.pdf")
generar_pdf_unico(bloques_pdf, pdf_path)
print(f"PDF generado: {pdf_path}")

# Agregar bloques de esta columna al diccionario global
bloques_por_columna[columna_actual] = bloques_pdf

# Guardar Excel único con una hoja por columna (acumulando todas)
excel_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.xlsx")
agregar_hoja_excel(bloques_pdf, columna_actual, excel_path)
print(f"Excel generado: {excel_path}")

