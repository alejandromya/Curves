import os
import io
import pandas as pd
from src.data_processing import cargar_y_preparar_csv
from src.cycle_detection import detectar_ciclos
from src.plotter import plot_ciclos
from src.force_detection import detectar_fuerza_maxima
from src.pdf_generator import generar_pdf

# Carpetas
input_folder = "datasets"
output_folder = "results"
os.makedirs(output_folder, exist_ok=True)

# Ciclos a seleccionar
targets = [100, 200, 300, 400, 500]

# Iterar sobre todos los CSV
for archivo in os.listdir(input_folder):
    if archivo.lower().endswith(".csv"):
        archivo_path = os.path.join(input_folder, archivo)
        print(f"\nProcesando: {archivo_path}")

        # Cargar y preparar CSV
        df = cargar_y_preparar_csv(archivo_path)

        # Detectar ciclos
        ciclos_totales, detalles = detectar_ciclos(df, min_force=10, smooth_window=5)
        print(f"Número total de ciclos detectados: {ciclos_totales}")

        # Detectar fuerza máxima (después de los ciclos)
        fuerza_max, deformacion_max = detectar_fuerza_maxima(df, detalles)
        print(f"Fuerza máxima: {fuerza_max:.6f}")
        print(f"Desplazamiento: {deformacion_max:.6e}")

        # Selección de ciclos concretos
        ciclos_seleccionados = {}
        for t in targets:
            ciclo_data = next((x for x in detalles if x["ciclo"] == t), None)
            if ciclo_data:
                ciclos_seleccionados[t] = ciclo_data
                print(f"Ciclo {t}: HIGH={ciclo_data['deform_high']:.6f}, LOW={ciclo_data['deform_low']:.6f}")
            else:
                print(f"Ciclo {t} no existe (solo hay {ciclos_totales})")

        # Calcular HIGH y LOW para gráfico
        HIGH = max(d['deform_high'] for d in detalles)
        LOW = min(d['deform_low'] for d in detalles)

        # Guardar gráfico en memoria
        grafico_memoria = io.BytesIO()
        plot_ciclos(df, detalles, HIGH, LOW, output_path=grafico_memoria)
        grafico_memoria.seek(0)  # Volver al inicio

        # Generar PDF con fuerza máxima
        nombre_pdf = os.path.splitext(archivo)[0] + ".pdf"
        pdf_path = os.path.join(output_folder, nombre_pdf)
        generar_pdf(ciclos_totales, ciclos_seleccionados, grafico_memoria, fuerza_max, deformacion_max, output_pdf=pdf_path)
        print(f"PDF generado: {pdf_path}")