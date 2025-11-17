import pandas as pd
import matplotlib.pyplot as plt
import csv

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
        return ";"  # por defecto

archivo_csv = "salida.csv"
sep = detectar_separador(archivo_csv)

# ---------------------------------------------------------
# Cargar CSV
# ---------------------------------------------------------
df = pd.read_csv(archivo_csv, sep=sep, encoding="latin1")

# Limpiar encabezados
df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)

# ---------------------------------------------------------
# Convertir a numérico, corrigiendo decimales con coma
# ---------------------------------------------------------
for col in ["Deformacion", "Fuerza"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")

# Validación básica
if df["Fuerza"].dropna().empty:
    print("\n❌ ERROR: La columna Fuerza no contiene números válidos")
    print(df.head())
    exit()

# ---------------------------------------------------------
# Máximo absoluto
# ---------------------------------------------------------
idx = df["Fuerza"].idxmax()
maximo_total = df.loc[idx]
print("\nMáximo Absoluto:", maximo_total["Fuerza"])

# ---------------------------------------------------------
# Máximo total válido (+1 mm)
# ---------------------------------------------------------
umbral_mm = 1.0
df["es_max_local"] = (df["Fuerza"] > df["Fuerza"].shift(1)) & (df["Fuerza"] > df["Fuerza"].shift(-1))
maximos = df[df["es_max_local"]].copy()

if len(maximos) == 0:
    maximo_total_valido = df.loc[df["Fuerza"].idxmax()]
else:
    maximos = maximos.sort_values("Deformacion").reset_index(drop=True)
    maximos_grupos = []
    grupo = [maximos.iloc[0]]
    deformacion_grupo = maximos.iloc[0]["Deformacion"]

    for i in range(1, len(maximos)):
        fila = maximos.iloc[i]
        deformacion_actual = fila["Deformacion"]
        if abs(deformacion_actual - deformacion_grupo) < umbral_mm:
            grupo.append(fila)
        else:
            grupo_df = pd.DataFrame(grupo)
            maximos_grupos.append(grupo_df.loc[grupo_df["Fuerza"].idxmax()])
            grupo = [fila]
            deformacion_grupo = deformacion_actual

    grupo_df = pd.DataFrame(grupo)
    maximos_grupos.append(grupo_df.loc[grupo_df["Fuerza"].idxmax()])
    maximo_total_valido = pd.DataFrame(maximos_grupos).loc[pd.DataFrame(maximos_grupos)["Fuerza"].idxmax()]

print("Máximo total de Fuerza válido según regla +1 mm:")
print(maximo_total_valido.to_dict())

# ---------------------------------------------------------
# Valor objetivo pedido al usuario
# ---------------------------------------------------------
try:
    valor_objetivo = float(input("\nIntroduce el valor objetivo de fuerza (N): "))
except:
    print("Entrada inválida, usando 50 N por defecto.")
    valor_objetivo = 50.0

tolerancia = 10
cercanos = df[(df["Fuerza"] >= valor_objetivo - tolerancia) &
              (df["Fuerza"] <= valor_objetivo + tolerancia)]

if len(cercanos) == 0:
    print("\nNo se encontraron puntos cerca del valor objetivo.")
    exit()

primer_punto = cercanos.iloc[0][["Deformacion", "Fuerza"]]
ultimo_punto = cercanos.iloc[-1][["Deformacion", "Fuerza"]]

print("\nPrimer punto cerca del objetivo:", primer_punto.to_dict())
print("Último punto cerca del objetivo:", ultimo_punto.to_dict())

# ---------------------------------------------------------
# Contar ciclos (valor objetivo → bajo)
# ---------------------------------------------------------
HIGH = valor_objetivo
LOW = 30
tol = 10
arriba = False
ciclos = 0

for i in range(len(df)):
    f = df.loc[i, "Fuerza"]
    if not arriba and (HIGH - tol <= f <= HIGH + tol):
        arriba = True
    if arriba and (LOW - tol <= f <= LOW + tol):
        ciclos += 1
        arriba = False

print(f"\nNúmero total de ciclos detectados (≈{HIGH} → ≈{LOW}): {ciclos}")

# ---------------------------------------------------------
# Graficar
# ---------------------------------------------------------
plt.figure(figsize=(10,5))
plt.plot(df["Deformacion"], df["Fuerza"])
plt.title("Gráfica Deformación vs Fuerza")
plt.xlabel("Deformación (mm)")
plt.ylabel("Fuerza (N)")
plt.grid(True)
plt.show()
