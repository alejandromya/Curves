import os
import io
import sys
import shutil
import atexit
import pathlib


# ============================================
# Carpeta real del exe / script
# ============================================
def exe_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


# ============================================
# Paths base
# ============================================
BASE_DIR = pathlib.Path(__file__).resolve().parent  # curves/
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


# ============================================
# Imports internos
# ============================================
from curves.src.data_processing import cargar_y_preparar_csv
from curves.src.cycle_detection import detectar_ciclos
from curves.src.plotter import plot_ciclos
from curves.src.force_detection import detectar_fuerza_maxima
from curves.src.pdf_generator import generar_pdf_unico
from curves.src.excel_generator import agregar_hoja_excel
from curves.src.word_generator import generar_word_unico
from curves.src.debug import debug_ciclos


# ============================================
# Carpetas al nivel del exe
# ============================================
BASE_OUTPUT = exe_dir()

UPLOAD_FOLDER = os.path.join(BASE_OUTPUT, "uploads")
RESULTS_FOLDER = BASE_OUTPUT   # Todo junto al exe

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================
# Limpieza automática
# ============================================
def limpiar_uploads():
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)


atexit.register(limpiar_uploads)


# ============================================
# Lógica principal
# ============================================
def procesar_columna(pico, valle, toler, columna_actual, csv_files):

    if not csv_files:
        raise ValueError("No se recibieron CSVs")

    bloques_pdf = []

    # Carpeta temporal por columna
    col_folder = os.path.join(UPLOAD_FOLDER, f"col{columna_actual}")
    os.makedirs(col_folder, exist_ok=True)

    # Copiar CSVs
    csv_locales = []

    for f in csv_files:
        dest = os.path.join(col_folder, os.path.basename(f))
        shutil.copy2(f, dest)
        csv_locales.append(dest)


    # Procesar CSVs
    for archivo_path in csv_locales:

        archivo = os.path.basename(archivo_path)

        df = cargar_y_preparar_csv(archivo_path)

        ciclos_totales, detalles = detectar_ciclos(
            df, pico, valle, toler
        )

        debug_ciclos(
            list(detalles.values()),
            os.path.join(BASE_OUTPUT, "debug_main_ciclos.txt")
        )


        if ciclos_totales == 0:
            continue


        (
            fuerza_max,
            deformacion_max,
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
    # Resultados finales (junto al exe)
    # ============================================
    pdf_path = os.path.join(
        RESULTS_FOLDER,
        f"INFORME_COL{columna_actual}.pdf"
    )

    excel_path = os.path.join(
        RESULTS_FOLDER,
        "INFORME_TOTAL.xlsx"
    )

    word_path = os.path.join(
        RESULTS_FOLDER,
        "INFORME_TOTAL.docx"
    )


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
