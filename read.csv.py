import pandas as pd
import matplotlib.pyplot as plt
import csv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

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

archivo_csv = "500Ciclos+Pullout_7.csv"
sep = detectar_separador(archivo_csv)

# ---------------------------------------------------------
# Cargar CSV y limpiar encabezados
# ---------------------------------------------------------
df = pd.read_csv(archivo_csv, sep=sep, encoding="latin1")
df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)

# Detectar columnas correctas
posibles_fuerza = [c for c in df.columns if "fuer" in c.lower()]
posibles_defo = [c for c in df.columns if "deform" in c.lower()]

if not posibles_fuerza or not posibles_defo:
    print("❌ No se encontraron columnas Fuerza / Deformación")
    print("Columnas detectadas:", df.columns.tolist())
    exit()

df.rename(columns={posibles_fuerza[0]: "Fuerza",
                   posibles_defo[0]: "Deformacion"}, inplace=True)

# Convertir a numérico
df["Fuerza"] = pd.to_numeric(df["Fuerza"].astype(str).str.replace(",", "."), errors="coerce")
df["Deformacion"] = pd.to_numeric(df["Deformacion"].astype(str).str.replace(",", "."), errors="coerce")

if df["Fuerza"].dropna().empty:
    print("\n❌ ERROR: La columna Fuerza no contiene datos numéricos válidos.")
    exit()

# ---------------------------------------------------------
# Pedir HIGH y LOW al usuario
# ---------------------------------------------------------
print("\n--- Configuración del ciclo ---")
HIGH = float(input("Introduce el valor alto del ciclo (HIGH, N): "))
LOW = float(input("Introduce el valor bajo del ciclo (LOW, N): "))
TOL = float(input("Tolerancia (ej. 5 o 10): "))

# ---------------------------------------------------------
# Detectar ciclos
# ---------------------------------------------------------
arriba = False
ciclos = 0
detalles_ciclos = []  # Guardar (ciclo, deform_high, deform_low)

deform_high = None

for i in range(len(df)):
    f = df.loc[i, "Fuerza"]
    d = df.loc[i, "Deformacion"]

    # Detecta la parte alta del ciclo
    if not arriba and (HIGH - TOL <= f <= HIGH + TOL):
        arriba = True
        deform_high = d

    # Detecta parte baja → fin del ciclo
    if arriba and (LOW - TOL <= f <= LOW + TOL):
        ciclos += 1
        deform_low = d
        detalles_ciclos.append({
            "ciclo": ciclos,
            "deform_high": deform_high,
            "deform_low": deform_low
        })
        arriba = False

# ---------------------------------------------------------
# Mostrar ciclos específicos: 100, 250, 500
# ---------------------------------------------------------
print("\n---------------------------------")
print("   RESULTADOS CICLOS SELECCIONADOS")
print("---------------------------------")

ciclos_seleccionados = {}
for target in [100, 250, 500]:
    ciclo_data = next((c for c in detalles_ciclos if c["ciclo"] == target), None)
    if ciclo_data:
        print(f"\nCiclo {target}:")
        print(f"  Deformación en HIGH = {ciclo_data['deform_high']:.6f} mm")
        print(f"  Deformación en LOW  = {ciclo_data['deform_low']:.6f} mm")
        ciclos_seleccionados[target] = ciclo_data
    else:
        print(f"\n⚠ Ciclo {target} NO existe en los datos.")

print(f"\nNúmero total de ciclos detectados: {ciclos}")

# ---------------------------------------------------------
# Graficar Fuerza vs Deformación
# ---------------------------------------------------------
plt.figure(figsize=(10, 5))
plt.plot(df["Deformacion"], df["Fuerza"], linewidth=0.8, label="Datos completos")

# Marcar los ciclos detectados
for c in detalles_ciclos:
    plt.scatter(c["deform_high"], HIGH, color="red", s=5)
    plt.scatter(c["deform_low"], LOW, color="blue", s=5)

plt.title("Gráfica Deformación vs Fuerza")
plt.xlabel("Deformación (mm)")
plt.ylabel("Fuerza (N)")
plt.grid(True)
plt.legend(["Datos completos", "HIGH detectado", "LOW detectado"])
plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# Crear PDF
# ---------------------------------------------------------
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
pdf_filename = "reporte_ensayo.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
story = []

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='NormalUTF8', fontName='Arial', fontSize=10))

story.append(Paragraph("Reporte de Ensayo Cíclico", styles["Heading1"]))
story.append(Spacer(1, 12))

reporte_texto = f"Numero total de ciclos detectados: {ciclos}<br/><br/>Deformaciones de ciclos seleccionados:<br/>"
for target, c in ciclos_seleccionados.items():
    reporte_texto += f"Ciclo {target}: HIGH = {c['deform_high']:.6f} mm, LOW = {c['deform_low']:.6f} mm<br/>"

story.append(Paragraph(reporte_texto, styles["NormalUTF8"]))
story.append(Spacer(1, 12))

# Guardar gráfico temporal
grafico_file = "grafico_temp.png"
plt.figure(figsize=(10,5))
plt.plot(df["Deformacion"], df["Fuerza"], linewidth=0.8, label="Datos completos")
for c in detalles_ciclos:
    plt.scatter(c["deform_high"], HIGH, color="red", s=5)
    plt.scatter(c["deform_low"], LOW, color="blue", s=5)
plt.title("Deformación vs Fuerza")
plt.xlabel("Deformación (mm)")
plt.ylabel("Fuerza (N)")
plt.grid(True)
plt.legend(["Datos completos", "HIGH detectado", "LOW detectado"])
plt.tight_layout()
plt.savefig(grafico_file, dpi=150)
plt.close()

story.append(Image(grafico_file, width=500, height=300))
doc.build(story)

print(f"\nPDF generado correctamente: {pdf_filename}")
