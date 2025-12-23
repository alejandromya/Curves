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
from src.word_generator import generar_word_unico

# ============================================
# Carpetas locales dentro del proyecto
# ============================================
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


def procesar_columna(pico, valle, toler, columna_actual, csv_files=None):
    """
    Procesa todos los CSV pertenecientes a una columna y genera:
    - PDF con resultados
    - Hoja correspondiente en el Excel total

    Args:
        pico, valle, toler: parámetros de detección de ciclos
        columna_actual: número de columna
        csv_files: lista opcional de rutas a CSV. Si no se da, buscará en uploads/colX

    Returns:
        dict con rutas de PDF, Excel, Word y bloques internos
    """

    bloques_pdf = []

    # Carpeta de la columna
    col_folder = os.path.join(UPLOAD_FOLDER, f"col{columna_actual}")
    os.makedirs(col_folder, exist_ok=True)

    # Si se pasan archivos directamente, copiarlos a col_folder
    if csv_files:
        for f in csv_files:
            dest = os.path.join(col_folder, os.path.basename(f))
            if not os.path.exists(dest):
                from shutil import copy2
                copy2(f, dest)

    # Listar CSVs en la carpeta de la columna
    csv_files_final = sorted(
        f for f in os.listdir(col_folder)
        if f.lower().endswith(".csv")
    )

    if not csv_files_final:
        raise FileNotFoundError(f"No se encontraron CSVs en {col_folder}")

    # ==============================
    # Procesamiento de cada CSV
    # ==============================
    for archivo in csv_files_final:
        archivo_path = os.path.join(col_folder, archivo)

        # 1️⃣ Cargar datos
        df = cargar_y_preparar_csv(archivo_path)

        # 2️⃣ Detectar ciclos
        ciclos_totales, detalles = detectar_ciclos(df, pico, valle, toler)

        debug_ciclos(list(detalles.values()), "debug_main_ciclos.txt")

        if ciclos_totales == 0:
            continue

        # Último ciclo
        ultimo_id = sorted(detalles.keys())[-1]
        ultimo_ciclo = detalles[ultimo_id]

        # 3️⃣ Detectar fuerza máxima
        (
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            yield_stiffness
        ) = detectar_fuerza_maxima(df, detalles)

        # 4️⃣ Generar gráfico en memoria
        grafico = io.BytesIO()
        plot_ciclos(
            df, detalles,
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            output_path=grafico
        )
        grafico.seek(0)

        # 5️⃣ Construir bloque PDF
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
    # Guardar PDF, Excel y Word
    # ==============================
    pdf_path = os.path.join(RESULTS_FOLDER, f"INFORME_COL{columna_actual}.pdf")
    excel_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.xlsx")
    word_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.docx")

    generar_pdf_unico(bloques_pdf, pdf_path)
    agregar_hoja_excel(bloques_pdf, columna_actual, excel_path)
    generar_word_unico(bloques_pdf, word_path)

    return {
        "pdf": pdf_path,
        "excel": excel_path,
        "word": word_path,
        "bloques": bloques_pdf
    }


if __name__ == "__main__":
    print("Este script es importable. Usa procesar_columna(pico, valle, toler, columna_actual, csv_files)")
