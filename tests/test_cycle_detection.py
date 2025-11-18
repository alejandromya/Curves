import pandas as pd
import pytest
from src.cycle_detection import detectar_ciclos

def test_ciclos_basico():
    df = pd.DataFrame({
        "Fuerza": [10, 80, 35, 80, 35, 80, 35],
        "Deformacion": [0,1,2,3,4,5,6]
    })
    ciclos, detalles = detectar_ciclos(df, HIGH=80, LOW=35, TOL=5)
    assert ciclos == 3
    assert detalles[0]["deform_high"] == 1
    assert detalles[0]["deform_low"] == 2
