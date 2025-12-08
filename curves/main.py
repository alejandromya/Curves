import os
import io

from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf_unico
from src.excel_generator import agregar_hoja_excel
from src.debug import debug_ciclos


UPLOAD_FOLDER = "/tmp/uploads"
RESULTS_FOLDER = "/tmp/results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


def procesar_columna(pico, valle, toler, columna_actual):
    """
    Procesa todos los CSV de la columna indicada y genera:
    - PDF por columna
    - Hoja en el Excel total
    Devuelve:
    - path al PDF generado
    - path al Excel generado
    - lista de bloques generados
    """

    # Diccionario de bloques para esta columna
    bloques_pdf = []

    # Carpeta donde están los CSV de esa columna
    input_folder = os.path.join(UPLOAD_FOLDER, f"col{columna_actual}")

    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"No existe la carpeta: {input_folder}")

    csv_files = sorted(
        [f for f in os.listdir(input_folder) if f.lower().endswith(".csv")]
    )

    for archivo in csv_files:
        archivo_path = os.path.join(input_folder, archivo)

        # Cargar datos
        df = cargar_y_preparar_csv(archivo_path)

        # Detectar ciclos
        ciclos_totales, detalles = detectar_ciclos(df, pico, valle, toler)

        # Debug opcional
        ciclos_lista = list(detalles.values())
        debug_ciclos(ciclos_lista, debug_filename="debug_main_ciclos.txt")

        if ciclos_totales == 0:
            continue

        # Ordenar ciclos y tomar el último
        ciclos_ordenados = sorted(detalles.keys())
        ultimo_ciclo = detalles[ciclos_ordenados[-1]]

        # Detectar fuerzas
        (
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            yield_stiffness
        ) = detectar_fuerza_maxima(df, detalles)

        # Plot en memoria
        grafico_memoria = io.BytesIO()
        plot_ciclos(
            df, detalles,
            fuerza_max, deformacion_max,
            f2mm_x, f2mm_y,
            f3mm_x, f3mm_y,
            output_path=grafico_memoria
        )
        grafico_memoria.seek(0)

        # Crear bloque
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

    # Rutas de salida
    pdf_path = os.path.join(RESULTS_FOLDER, f"INFORME_COL{columna_actual}.pdf")
    excel_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.xlsx")

    # Generar PDF de la columna
    generar_pdf_unico(bloques_pdf, pdf_path)

    # Agregar hoja al Excel total
    agregar_hoja_excel(bloques_pdf, columna_actual, excel_path)

    return {
        "pdf": pdf_path,
        "excel": excel_path,
        "bloques": bloques_pdf
    }


# Si alguien ejecuta main.py directamente, puedes dejar un test mínimo opcional:
if __name__ == "__main__":
    print("Este script ahora es importable. Usa procesar_columna().")
