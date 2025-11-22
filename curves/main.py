import os
import io
import pandas as pd
import sys
from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf_unico

# Carpetas
input_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "uploads"))
output_folder = "results"
os.makedirs(output_folder, exist_ok=True)

pico_obj = float(sys.argv[1])
valle_obj = float(sys.argv[2])
toler = float(sys.argv[3])

targets = [100, 200, 300, 400, 500]
bloques_pdf = []

for archivo in os.listdir(input_folder):
    if archivo.lower().endswith(".csv"):
        archivo_path = os.path.join(input_folder, archivo)
        print(f"\nProcesando: {archivo_path}")

        df = cargar_y_preparar_csv(archivo_path)

        ciclos_totales, detalles = detectar_ciclos(df, pico_obj, valle_obj, toler)
        print(f"Número de ciclos detectados: {ciclos_totales}")

        if ciclos_totales == 0:
            print("❌ No se detectaron ciclos. Se omite este archivo.")
            continue

        fuerza_max, deformacion_max = detectar_fuerza_maxima(df, detalles)
        print(f"Fuerza máxima: {fuerza_max:.6f}, Desplazamiento: {deformacion_max:.6f}")

        # Primer y último ciclo:
        ciclos_ordenados = sorted(detalles.keys())
        primer_ciclo = detalles[ciclos_ordenados[0]]
        ultimo_ciclo = detalles[ciclos_ordenados[-1]]

        # === Calcular F2mm y F3mm desde low del último ciclo ===
        deform_low_last = ultimo_ciclo["deform_low"]

        f2mm_idx = (df["Deformacion"] - deform_low_last - 2.0).abs().idxmin()
        f3mm_idx = (df["Deformacion"] - deform_low_last - 3.0).abs().idxmin()

        f2mm_x = float(df.loc[f2mm_idx, "Deformacion"])
        f2mm_y = float(df.loc[f2mm_idx, "Fuerza"])
        f3mm_x = float(df.loc[f3mm_idx, "Deformacion"])
        f3mm_y = float(df.loc[f3mm_idx, "Fuerza"])

        # === Gráfico en memoria ===
        grafico_memoria = io.BytesIO()
        plot_ciclos(
            df,
            detalles,
            fuerza_max,
            deformacion_max,
            f2mm_x,
            f2mm_y,
            f3mm_x,
            f3mm_y,
            output_path=grafico_memoria
        )
        grafico_memoria.seek(0)

        # === BLOQUE COMPLETO ===
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

# === Generar PDF ===
pdf_final = os.path.join(output_folder, "INFORME_FINAL.pdf")
generar_pdf_unico(bloques_pdf, pdf_final)
print("\n📄 PDF único generado en:", pdf_final)
