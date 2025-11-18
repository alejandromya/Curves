import os
import pandas as pd
from src.plotter import plot_ciclos

def test_grafico_generado(tmp_path):
    df = pd.DataFrame({
        "Fuerza": [10, 80, 35, 80, 35],
        "Deformacion": [0,1,2,3,4]
    })
    archivo = tmp_path / "grafico_test.png"
    plot_ciclos(df, ciclos=[], archivo_salida=str(archivo))
    assert archivo.exists()
    assert archivo.stat().st_size > 0
