import pandas as pd
import pytest
from src.data_processing import cargar_csv

def test_cargar_csv_valido():
    df = cargar_csv("tests/datos_prueba.csv")
    assert not df.empty
    assert "Fuerza" in df.columns
    assert "Deformacion" in df.columns

def test_cargar_csv_columnas_numericas():
    df = cargar_csv("tests/datos_prueba.csv")
    assert pd.api.types.is_numeric_dtype(df["Fuerza"])
    assert pd.api.types.is_numeric_dtype(df["Deformacion"])
