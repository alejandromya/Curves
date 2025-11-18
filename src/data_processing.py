import pandas as pd
from .utils import detectar_separador

def cargar_y_preparar_csv(filepath):
    """Carga el CSV, limpia encabezados y convierte valores numéricos."""
    
    sep = detectar_separador(filepath)
    df = pd.read_csv(filepath, sep=sep, encoding="latin1")

    # Normalizar encabezados
    df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)

    # Detectar columnas correctas
    posibles_fuerza = [c for c in df.columns if "fuer" in c.lower()]
    posibles_defo = [c for c in df.columns if "deform" in c.lower()]

    if not posibles_fuerza or not posibles_defo:
        raise ValueError(f"No se detectaron columnas adecuadas. Columnas = {df.columns.tolist()}")

    df.rename(columns={
        posibles_fuerza[0]: "Fuerza",
        posibles_defo[0]: "Deformacion"
    }, inplace=True)

    # Convertir a numérico
    df["Fuerza"] = pd.to_numeric(df["Fuerza"].astype(str).str.replace(",", "."), errors="coerce")
    df["Deformacion"] = pd.to_numeric(df["Deformacion"].astype(str).str.replace(",", "."), errors="coerce")

    if df["Fuerza"].dropna().empty:
        raise ValueError("La columna Fuerza está vacía o no contiene números válidos.")

    return df
