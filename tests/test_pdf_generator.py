import pandas as pd
from PIL import Image
from src.pdf_generator import generar_pdf

def test_pdf_generado(tmp_path):
    # Crear DataFrame de ejemplo
    df = pd.DataFrame({
        "Fuerza": [10, 80, 35],
        "Deformacion": [0, 1, 2]
    })

    # Ciclos seleccionados de ejemplo
    ciclos_seleccionados = {1: {"deform_high": 1, "deform_low": 2}}

    # Crear archivo de imagen válido para el test
    grafico_file = tmp_path / "grafico_test.png"
    img = Image.new("RGB", (10, 10), color="white")  # imagen PNG válida
    img.save(grafico_file)

    # Ruta de salida PDF
    archivo_pdf = tmp_path / "reporte_test.pdf"

    # Llamar a la función
    generar_pdf(df, ciclos_seleccionados, str(grafico_file), str(archivo_pdf))

    # Comprobar que el PDF fue creado
    assert archivo_pdf.exists()
    assert archivo_pdf.stat().st_size > 0
