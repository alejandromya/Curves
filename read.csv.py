import pandas as pd
import matplotlib.pyplot as plt
import csv
import re

# ---------------------------------------------------------
# Detectar separador automáticamente
# ---------------------------------------------------------
def detectar_separador(filename, n=5):
    with open(filename, "r", encoding="latin1") as f:
        snippet = "".join([f.readline() for _ in range(n)])
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(snippet)
        return dialect.delimiter
    except:
        return ";"


archivo_csv = "500Ciclos+Pullout_7.csv"
sep = detectar_separador(archivo_csv)

# ---------------------------------------------------------
# Cargar CSV
# ---------------------------------------------------------
df = pd.read_csv(archivo_csv, sep=sep, encoding="latin1")

# ---------------------------------------------------------
# Limpieza de encabezados
# ---------------------------------------------------------
df.columns = (
    df.columns
    .str.strip()
    .str.replace("\ufeff", "", regex=False)
    .str.replace("ó", "o")
    .str.replace("Ó", "O")
    .str.replace(" ", "")
    .str.replace(";", "")
)

print("\nEncabezados detectados:", df.columns.tolist())

# ---------------------------------------------------------
# Buscar nombres reales de columnas automáticamente
# ---------------------------------------------------------
col_fuerza = None
col_deform = None

for col in df.columns:
    if re.search("fuer", col.lower()):
        col_fuerza = col
    if re.search("deform", col.lower()):
        col_deform = col

print("→ Columna fuerza detectada:", col_fuerza)
print("→ Columna deformación detectada:", col_deform)

if col_fuerza is None or col_deform is None:
    print("\n❌ ERROR: No se encontraron columnas válidas de Fuerza o Deformación")
    exit()

# Renombrar oficialmente
df = df.rename(columns={
    col_fuerza: "Fuerza",
    col_deform: "Deformacion"
})

# ---------------------------------------------------------
# Convertir a numérico
# ---------------------------------------------------------
df["Fuerza"] = pd.to_numeric(df["Fuerza"].astype(str).str.replace(",", "."), errors="coerce")
df["Deformacion"] = pd.to_numeric(df["Deformacion"].astype(str).str.replace(",", "."), errors="coerce")

# Validación
if df["Fuerza"].dropna().empty:
    print("\n❌ ERROR: La columna Fuerza no contiene datos numéricos válidos.")
    print(df.head())
    exit()

# ---------------------------------------------------------
# Máximo absoluto
# ---------------------------------------------------------
idx = df["Fuerza"].idxmax()
maximo_total = df.loc[idx]
print("\nMáximo Absoluto:", maximo_total["Fuerza"])

# ---------------------------------------------------------
# Máximo válido (+1 mm)
# ---------------------------------------------------------
umbral_mm = 1.0
df["es_max_local"] = (df["Fuerza"] > df["Fuerza"].shift(1)) & (df["Fuerza"] > df["Fuerza"].shift(-1))
maximos = df[df["es_max_local"]].copy()

if len(maximos) == 0:
    maximo_total_valido = df.loc[df["Fuerza"].idxmax()]
else:
    maximos = maximos.sort_values("Deformacion").reset_index(drop=True)
    grupos = []
    grupo = [maximos.iloc[0]]
    deform_ref = maximos.iloc[0]["Deformacion"]

    for i in range(1, len(maximos)):
        fila = maximos.iloc[i]
        if abs(fila["Deformacion"] - deform_ref) < umbral_mm:
            grupo.append(fila)
        else:
            grupo_df = pd.DataFrame(grupo)
            grupos.append(grupo_df.loc[grupo_df["Fuerza"].idxmax()])
            grupo = [fila]
            deform_ref = fila["Deformacion"]

    grupo_df = pd.DataFrame(grupo)
    grupos.append(grupo_df.loc[grupo_df["Fuerza"].idxmax()])
    maximo_total_valido = pd.DataFrame(grupos).loc[pd.DataFrame(grupos)["Fuerza"].idxmax()]

print("\nMáximo válido +1 mm:", maximo_total_valido.to_dict())

# ---------------------------------------------------------
# DETECCIÓN AUTOMÁTICA DE HIGH Y LOW EN CICLOS
# ---------------------------------------------------------

def pedir_rango(nombre):
    r = input(f"\nIntroduce rango aproximado para {nombre} (formato: min,max): ")
    try:
        rmin, rmax = [float(x) for x in r.split(",")]
        return rmin, rmax
    except:
        print("Entrada inválida. Usando valores por defecto.")
        return None

# Pedir rangos aproximados al usuario
rango_low = pedir_rango("LOW (bajo)")
rango_high = pedir_rango("HIGH (alto)")

if rango_low is None:
    rango_low = (30, 45)
if rango_high is None:
    rango_high = (60, 80)

low_min, low_max = rango_low
high_min, high_max = rango_high

# Filtrar valores dentro del rango
data_low = df[df["Fuerza"].between(low_min, low_max)]["Fuerza"]
data_high = df[df["Fuerza"].between(high_min, high_max)]["Fuerza"]

if data_low.empty or data_high.empty:
    print("\n❌ No pude detectar low/high dentro del rango proporcionado.")
    exit()

# HIGH y LOW reales como promedio de los valores más frecuentes
LOW_real = data_low.mean()
HIGH_real = data_high.mean()

print(f"\nLOW real detectado:  {LOW_real:.2f} N")
print(f"HIGH real detectado: {HIGH_real:.2f} N")

# ---------------------------------------------------------
# CONTAR CICLOS
# ---------------------------------------------------------
tol = 5    # tolerancia automática

arriba = False
ciclos = 0

for f in df["Fuerza"]:
    # detectar subida al nivel alto
    if not arriba and (HIGH_real - tol <= f <= HIGH_real + tol):
        arriba = True

    # detectar bajada al nivel bajo
    if arriba and (LOW_real - tol <= f <= LOW_real + tol):
        ciclos += 1
        arriba = False

print(f"\nCICLOS DETECTADOS: {ciclos}")


# ---------------------------------------------------------
# Gráfica
# ---------------------------------------------------------
plt.figure(figsize=(10,5))
plt.plot(df["Deformacion"], df["Fuerza"])
plt.title("Gráfica Deformación vs Fuerza")
plt.xlabel("Deformación (mm)")
plt.ylabel("Fuerza (N)")
plt.grid(True)
plt.show()
