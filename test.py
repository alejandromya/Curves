import pandas as pd

# La fila 1 (segunda fila del Excel, índice 1) será el encabezado
df = pd.read_excel("test.xlsx", header=0)

print(df.head())

columnas = ["Deformacion", "Fuerza"]
df_seleccion = df[columnas]

df_seleccion.to_csv("salida.csv", index=False)
