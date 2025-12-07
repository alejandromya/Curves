from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from src.tables_generator import generar_tablas_combinadas

# Carpeta de fuentes dentro del proyecto
FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# Ruta relativa a DejaVuSans.ttf incluida en el proyecto
deja_vu_path = os.path.join(FONTS_DIR, "DejaVuSans.ttf")

# Registrar fuente con fallback
try:
    if os.path.exists(deja_vu_path):
        pdfmetrics.registerFont(TTFont("DejaVu", deja_vu_path))
        DEFAULT_FONT = "DejaVu"
    else:
        # Fuente estándar de PDF (funciona en cualquier OS)
        DEFAULT_FONT = "Helvetica"
except Exception as e:
    print("No se pudo cargar DejaVuSans.ttf, usando Helvetica por defecto:", e)
    DEFAULT_FONT = "Helvetica"
    

def generar_pdf_unico(bloques, output_pdf="INFORME_FINAL.pdf"):
    # Carpeta de fuentes dentro del proyecto
    FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
    deja_vu_path = os.path.join(FONTS_DIR, "DejaVuSans.ttf")

    # Registrar fuente con fallback
    try:
        if os.path.exists(deja_vu_path):
            pdfmetrics.registerFont(TTFont('DejaVu', deja_vu_path))
            default_font = 'DejaVu'
        else:
            default_font = 'Helvetica'
    except Exception as e:
        print("No se pudo cargar DejaVuSans.ttf, usando Helvetica:", e)
        default_font = 'Helvetica'

    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='NormalUTF8', fontName=default_font, fontSize=10))

    story.append(Paragraph("<b>Resultados</b>", styles["Heading1"]))
    story.append(Spacer(1, 12))

    # Generar tablas combinadas
    (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd) = generar_tablas_combinadas(bloques)

    # Tabla Cyclic
    tabla_cyclic = Table([headers_cyclic] + filas_cyclic)
    tabla_cyclic.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(tabla_cyclic)
    story.append(Spacer(1, 12))

    # Tabla 3rd Phase
    tabla_3rd = Table([headers_3rd] + filas_3rd)
    tabla_3rd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(tabla_3rd)
    story.append(PageBreak())

    # Gráficas
    for bloque in bloques:
        story.append(Paragraph(f"<b>{bloque['titulo']}</b>", styles["Heading2"]))
        story.append(Spacer(1, 12))
        story.append(Image(bloque["grafico"], width=500, height=300))
        story.append(PageBreak())

    doc.build(story)
    return output_pdf
