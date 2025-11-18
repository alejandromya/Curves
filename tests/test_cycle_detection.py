import pandas as pd
from src.cycle_detection import detectar_ciclos

def test_ciclos_basico():
    df = pd.DataFrame({
        "Fuerza": [10, 80, 35, 80, 35, 80, 35],
        "Deformacion": [0, 1, 2, 3, 4, 5, 6]
    })
    ciclos, detalles = detectar_ciclos(df, min_force=10, smooth_window=1)
    assert ciclos == 3
    assert detalles[0]["deform_high"] == 1
    assert detalles[0]["deform_low"] == 2

def test_ciclo_incompleto():
    df = pd.DataFrame({
        "Fuerza": [10, 50, 80],  # Solo subida, sin valle
        "Deformacion": [0, 1, 2]
    })
    ciclos, detalles = detectar_ciclos(df, min_force=10, smooth_window=1)
    assert ciclos == 0
    assert detalles == []

def test_ciclos_con_ruido():
    df = pd.DataFrame({
        "Fuerza": [10, 45, 42, 48, 35, 50, 30, 55, 33],
        "Deformacion": list(range(9))
    })
    ciclos, detalles = detectar_ciclos(df, min_force=10, smooth_window=3)
    assert ciclos >= 2  # Debe detectar al menos 2 ciclos pese al ruido

def test_pullout_final():
    df = pd.DataFrame({
        "Fuerza": [10, 60, 30, 60, 30, 70, 10],  # Última caída es pullout
        "Deformacion": list(range(7))
    })
    ciclos, detalles = detectar_ciclos(df, min_force=10, smooth_window=1)
    assert ciclos == 3  # Ignora la última caída como ciclo
