import pandas as pd
from src.data_processing import cargar_y_preparar_csv

def test_cargar_csv_valido(tmp_path):
    archivo = tmp_path / "datos_prueba.csv"
    archivo.write_text("Fuerza;Deformacion\n10;0\n80;1\n35;2", encoding="latin1")
    df = cargar_y_preparar_csv(str(archivo))

    # df = cargar_y_preparar_csv("tests/datos_prueba.csv")
    assert not df.empty
    assert "Fuerza" in df.columns
    assert "Deformacion" in df.columns

def test_cargar_csv_columnas_numericas(tmp_path):
    archivo = tmp_path / "datos_prueba.csv"
    archivo.write_text("Fuerza;Deformacion\n10;0\n80;1\n35;2", encoding="latin1")
    df = cargar_y_preparar_csv(str(archivo))
    # df = cargar_y_preparar_csv("tests/datos_prueba.csv")
    assert pd.api.types.is_numeric_dtype(df["Fuerza"])
    assert pd.api.types.is_numeric_dtype(df["Deformacion"])
