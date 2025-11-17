import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Cargar CSV
# ---------------------------------------------------------
df = pd.read_csv(
    "salida.csv",
    sep=";",          # separador correcto
    decimal=".",      # usar punto decimal
    encoding="latin1"
)



# --- LIMPIEZA DE ENCABEZADOS ---
df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)


# Asegurarse de que sean numéricos
df["Deformacion"] = pd.to_numeric(df["Deformacion"].str.replace(",", "."), errors="coerce")
df["Fuerza"] = pd.to_numeric(df["Fuerza"].str.replace(",", "."), errors="coerce")


# --- VALIDACIÓN ---
if df["Fuerza"].dropna().empty:
    print("\n❌ ERROR: La columna Fuerza no contiene números válidos")
    print(df.head())
    exit()


# --- MAXIMO TOTAL ---
idx = df["Fuerza"].idxmax()
maximo_total = df.loc[idx]

print("\nMáximo Absoluto:", maximo_total["Fuerza"])
#print("Fila del máximo:", maximo_total.to_dict())

# ---------------------------------------------------------
# Cálculo del máximo total válido (regla del +1 mm)
# ---------------------------------------------------------

umbral_mm = 1.0  # umbral en mm

# Detectar máximos locales
df["es_max_local"] = (df["Fuerza"] > df["Fuerza"].shift(1)) & (df["Fuerza"] > df["Fuerza"].shift(-1))
maximos = df[df["es_max_local"]].copy()

if len(maximos) == 0:
    maximo_total_valido = df.loc[df["Fuerza"].idxmax()]
else:
    # Ordenar máximos por deformación
    maximos = maximos.sort_values("Deformacion").reset_index(drop=True)

    # Lista para almacenar máximos válidos por grupo de deformación
    maximos_grupos = []

    # Inicializar el primer grupo
    grupo = [maximos.iloc[0]]
    deformacion_grupo = maximos.iloc[0]["Deformacion"]

    for i in range(1, len(maximos)):
        fila = maximos.iloc[i]
        deformacion_actual = fila["Deformacion"]

        if abs(deformacion_actual - deformacion_grupo) < umbral_mm:
            # Mismo grupo: añadir
            grupo.append(fila)
        else:
            # Guardar máximo del grupo anterior
            grupo_df = pd.DataFrame(grupo)
            maximos_grupos.append(grupo_df.loc[grupo_df["Fuerza"].idxmax()])
            # Empezar nuevo grupo
            grupo = [fila]
            deformacion_grupo = deformacion_actual

    # Guardar último grupo
    grupo_df = pd.DataFrame(grupo)
    maximos_grupos.append(grupo_df.loc[grupo_df["Fuerza"].idxmax()])

    # Elegir el máximo absoluto entre todos los máximos válidos
    maximo_total_valido = pd.DataFrame(maximos_grupos).loc[
        pd.DataFrame(maximos_grupos)["Fuerza"].idxmax()
    ]

print("Máximo total de Fuerza válido según regla +1 mm:")
print(maximo_total_valido.to_dict())


# ---------------------------------------------------------
# Valor objetivo pedido al usuario
# ---------------------------------------------------------
# try:
#     valor_objetivo = float(input("\nIntroduce el valor objetivo de fuerza (N): "))
# except:
#     print("Entrada inválida, usando 50 N por defecto.")
#     valor_objetivo = 50.0

valor_objetivo = 80
tolerancia = 10

# Filtrar valores cercanos al objetivo
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
# CONTAR CICLOS (50N → 10N)
# ---------------------------------------------------------

HIGH = valor_objetivo           # Parte alta del ciclo (≈50)
LOW = 30                        # Parte baja del ciclo (≈10)
tol = 10                        # Tolerancia para ambos

arriba = False                  # Estado: estamos en la parte alta
ciclos = 0                      # Contador final

for i in range(len(df)):

    f = df.loc[i, "Fuerza"]

    # Detecta cruce por la zona alta (≈50)
    if not arriba and (HIGH - tol <= f <= HIGH + tol):
        arriba = True  # Entramos en zona alta

    # Detecta cruce por la zona baja (≈10)
    if arriba and (LOW - tol <= f <= LOW + tol):
        ciclos += 1
        arriba = False   # Reiniciamos para esperar el próximo ciclo

print(f"\nNúmero total de ciclos detectados (≈{HIGH} → ≈{LOW}): {ciclos}")


# --------- GRAFICAR ---------
plt.figure(figsize=(10,5))
plt.plot(df["Deformacion"], df["Fuerza"])
plt.title("Gráfica Deformación vs Fuerza")
plt.xlabel("Deformación (mm)")
plt.ylabel("Fuerza (N)")
plt.grid(True)

plt.show()