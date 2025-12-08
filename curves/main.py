import os
import io
import sys

# ============================================
# Ajustar sys.path para poder importar /curves/src
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_DIR)

from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf_unico
from src.excel_generator import agregar_hoja_excel
from src.debug import debug_ciclos

# ============================================
# Carpetas temporales compatibles con Render
# ============================================
UPLOAD_FOLDER = "/tmp/uploads"
RESULTS_FOLDER = "/tmp/results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


def procesar_columna(pico, valle, toler, columna_actual):
    """
    Procesa todos los CSV pertenecientes a una columna y genera:
    - PDF con resultados
    - Hoja correspondiente en el Excel total

    Devuelve:
        {
            "pdf": ruta_pdf,
            "excel": ruta_excel,
            "bloques": bloques_pdf
        }
    """

    bloques_pdf = []

    # Carpeta donde están los csv de esa columna (creada en server.py)
    input_folder = os.path.join(UPLOAD_FOLDER, f"col{columna_actual}")

    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"No existe la carpeta: {input_folder}")

    # Buscar archivos CSV
    csv_files = sorted(
        f for f in os.listdir(input_folder)
        if f.lower().endswith(".csv")
    )

    for archivo in csv_files:
        archivo_path = os.path.join(input_folder, archivo)

        # ==============================
        # 1. Cargar datos
        # ==============================
        df = cargar_y_preparar_csv(archivo_path)

        # ==============================
        # 2. Detectar ciclos
        # ==============================
        ciclos_totales, detalles = detectar_ciclos(df, pico, valle, toler)

        # Guardar debug
        debug_ciclos(list(detalles.values()), "debug_main_ciclos.txt")

        if ciclos_totales == 0:
            continue

        # último ciclo
        ultimo_id = sorted(detalles.keys())[-1]
        ultimo_ciclo = detalles[ultimo_id]

        # ==============================
        # 3. Detectar fuerza máxima
        # ==============================
        (
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            yield_stiffness
        ) = detectar_fuerza_maxima(df, detalles)

        # ==============================
        # 4. Generar gráfico en memoria
        # ==============================
        grafico = io.BytesIO()
        plot_ciclos(
            df, detalles,
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            output_path=grafico
        )
        grafico.seek(0)

        # ==============================
        # 5. Construir bloque PDF
        # ==============================
        bloque = {
            "titulo": archivo,
            "total_ciclos": ciclos_totales,
            "ciclos": detalles,
            "grafico": grafico,
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

    # ==============================
    # 6. Generar PDF y Excel
    # ==============================
    pdf_path = os.path.join(RESULTS_FOLDER, f"INFORME_COL{columna_actual}.pdf")
    excel_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.xlsx")

    generar_pdf_unico(bloques_pdf, pdf_path)
    agregar_hoja_excel(bloques_pdf, columna_actual, excel_path)

    return {
        "pdf": pdf_path,
        "excel": excel_path,
        "bloques": bloques_pdf
    }


if __name__ == "__main__":
    print("Este script es importable. Usa procesar_columna(pico, valle, toler, columna).")
