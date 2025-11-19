import os
import io
import pandas as pd
from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf_unico
from src.word_generator import generar_word_unico

# Carpetas
input_folder = "datasets"
output_folder = "results"
os.makedirs(output_folder, exist_ok=True)

# Preguntar PICO/VALLE solo una vez
print("\n=== CONFIGURACIÓN GLOBAL DE CICLOS ===")
pico_obj = float(input("Ingrese valor objetivo del PICO: "))
valle_obj = float(input("Ingrese valor objetivo del VALLE: "))
toler = float(input("Ingrese tolerancia (ej. 0.5): "))

# Ciclos a seleccionar (targets)
targets = [100, 200, 300, 400, 500]

# Lista de bloques para PDF único
bloques_pdf = []

# Iterar sobre todos los CSV
for archivo in os.listdir(input_folder):
    if archivo.lower().endswith(".csv"):
        archivo_path = os.path.join(input_folder, archivo)
        print(f"\nProcesando: {archivo_path}")

        # Cargar y preparar CSV
        df = cargar_y_preparar_csv(archivo_path)

        # Detectar ciclos
        ciclos_totales, detalles = detectar_ciclos(df, pico_obj, valle_obj, toler)
        print(f"Número de ciclos detectados: {ciclos_totales}")

        if ciclos_totales == 0:
            print("❌ No se detectaron ciclos. Se omite este archivo.")
            continue

        # Detectar fuerza máxima después del último ciclo
        fuerza_max, deformacion_max = detectar_fuerza_maxima(df, detalles)
        print(f"Fuerza máxima: {fuerza_max:.6f}, Desplazamiento: {deformacion_max:.6e}")

        # Selección de ciclos concretos usando diccionario seguro
        ciclos_seleccionados = {}
        for t in targets:
            ciclo_data = detalles.get(t, None)
            if ciclo_data:
                ciclos_seleccionados[t] = ciclo_data
                print(f"Ciclo {t}: HIGH inicio={ciclo_data['deform_high_start']:.6f}, "
                      f"LOW={ciclo_data['deform_low']:.6f}, "
                      f"HIGH final={ciclo_data['deform_high_end']:.6f}")
            else:
                print(f"Ciclo {t} no existe (solo hay {ciclos_totales})")

        # Guardar gráfico en memoria
        grafico_memoria = io.BytesIO()
        plot_ciclos(df, detalles,fuerza_max, deformacion_max, output_path=grafico_memoria)
        grafico_memoria.seek(0)

        # Guardar todos los datos en un bloque para PDF
        bloques_pdf.append({
        "titulo": archivo,
        "total_ciclos": ciclos_totales,
        "ciclos": detalles,
        "grafico": grafico_memoria,
        "fuerza_max": fuerza_max,
        "deformacion_max": deformacion_max,
        "df": df  # <-- añadido para calcular F2mm, F3mm y desplazamientos relativos
    })

# Generar PDF único
pdf_final = os.path.join(output_folder, "INFORME_FINAL.pdf")
generar_pdf_unico(bloques_pdf, pdf_final)
print("\n📄 PDF único generado en:", pdf_final)

# Generar Word único

# word_final = os.path.join(output_folder, "INFORME_FINAL.docx")
# generar_word_unico(bloques_pdf, word_final)
# print("📄 Word único generado en:", word_final)