def test_grafico_generado(tmp_path):
    import pandas as pd
    from src.plotter import plot_ciclos

    df = pd.DataFrame({
        "Fuerza": [10, 80, 35, 80, 35],
        "Deformacion": [0, 1, 2, 3, 4]
    })

    # Archivo de salida temporal
    archivo = tmp_path / "grafico_test.png"

    # Datos de ejemplo para HIGH y LOW
    HIGH = [80, 80]
    LOW = [10, 35]

    # Detalles de ciclos de ejemplo
    detalles_ciclos = [
        {"deform_high": 1, "deform_low": 2},
        {"deform_high": 3, "deform_low": 4}
    ]

    # Llamada correcta a la función
    resultado = plot_ciclos(df, detalles_ciclos, HIGH, LOW, output_path=str(archivo))

    # Verificar que el archivo se creó
    assert archivo.exists()
    assert resultado == str(archivo)
