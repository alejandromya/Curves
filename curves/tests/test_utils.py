from src.utils import detectar_separador

def test_detectar_separador(tmp_path):
    archivo = tmp_path / "prueba.csv"
    archivo.write_text("Col1;Col2\n1;2\n3;4", encoding="latin1")
    sep = detectar_separador(str(archivo))
    assert sep == ";"
