import os
import io
import sys
import shutil
import atexit

# ============================================
# Paths base
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

# ============================================
# Imports internos
# ============================================
from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf_unico
from src.excel_generator import agregar_hoja_excel
from src.word_generator import generar_word_unico
from src.debug import debug_ciclos
from desktop.paths import resource_path

# ============================================
# Carpetas de trabajo (locales)
# ============================================
UPLOAD_FOLDER = resource_path("uploads")
RESULTS_FOLDER = resource_path("results")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ============================================
# Limpieza automática al cerrar el programa
# ============================================
def limpiar_uploads():
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)

atexit.register(limpiar_uploads)

# ============================================
# Lógica principal
# ============================================
def procesar_columna(pico, valle, toler, columna_actual, csv_files):
    """
    Procesa una columna completa.

    csv_files: lista de rutas originales seleccionadas por el usuario
    """

    if not csv_files:
        raise ValueError("No se recibieron CSVs")

    bloques_pdf = []

    # Carpeta interna temporal por columna
    col_folder = os.path.join(UPLOAD_FOLDER, f"col{columna_actual}")
    os.makedirs(col_folder, exist_ok=True)

    # Copiar CSVs a carpeta temporal controlada
    csv_locales = []
    for f in csv_files:
        dest = os.path.join(col_folder, os.path.basename(f))
        shutil.copy2(f, dest)
        csv_locales.append(dest)

    # ============================================
    # Procesar CSVs
    # ============================================
    for archivo_path in csv_locales:
        archivo = os.path.basename(archivo_path)

        df = cargar_y_preparar_csv(archivo_path)

        ciclos_totales, detalles = detectar_ciclos(df, pico, valle, toler)
        debug_ciclos(list(detalles.values()), "debug_main_ciclos.txt")

        if ciclos_totales == 0:
            continue

        (
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            yield_stiffness
        ) = detectar_fuerza_maxima(df, detalles)

        grafico = io.BytesIO()
        plot_ciclos(
            df, detalles,
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            output_path=grafico
        )
        grafico.seek(0)

        bloques_pdf.append({
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
        })

    if not bloques_pdf:
        raise RuntimeError("No se generaron datos válidos")

    # ============================================
    # Resultados finales
    # ============================================
    pdf_path = os.path.join(RESULTS_FOLDER, f"INFORME_COL{columna_actual}.pdf")
    excel_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.xlsx")
    word_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.docx")

    generar_pdf_unico(bloques_pdf, pdf_path)
    agregar_hoja_excel(bloques_pdf, columna_actual, excel_path)
    generar_word_unico(bloques_pdf, word_path)

    return {
        "pdf": pdf_path,
        "excel": excel_path,
        "word": word_path
    }


if __name__ == "__main__":
    print("Usa procesar_columna(...) desde la UI")
