from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def generar_pdf(ciclos_totales, ciclos_seleccionados, grafico_file, output_pdf="reporte_ensayo.pdf"):
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='NormalUTF8', fontName='Arial', fontSize=10))

    story.append(Paragraph("Reporte de Ensayo Cíclico", styles["Heading1"]))
    story.append(Spacer(1, 12))

    texto = f"<b>Número total de ciclos detectados:</b> {ciclos_totales}<br/><br/>"
    texto += "<b>Deformaciones de ciclos seleccionados:</b><br/>"
    for k, c in ciclos_seleccionados.items():
        texto += f"Ciclo {k}: HIGH = {c['deform_high']:.6f} mm, LOW = {c['deform_low']:.6f} mm<br/>"

    story.append(Paragraph(texto, styles["NormalUTF8"]))
    story.append(Spacer(1, 15))

    story.append(Image(grafico_file, width=500, height=300))

    doc.build(story)
    return output_pdf
