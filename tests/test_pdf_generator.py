import os
import pandas as pd
from src.pdf_generator import generar_pdf

def test_pdf_generado(tmp_path):
    df = pd.DataFrame({
        "Fuerza": [10, 80, 35],
        "Deformacion": [0,1,2]
    })
    ciclos_seleccionados = {1: {"deform_high":1, "deform_low":2}}
    archivo_pdf = tmp_path / "reporte_test.pdf"
    generar_pdf(df, ciclos_seleccionados, "reporte_test", str(archivo_pdf))
    assert archivo_pdf.exists()
    assert archivo_pdf.stat().st_size > 0
