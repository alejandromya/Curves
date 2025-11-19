from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def generar_pdf_unico(bloques, output_pdf="INFORME_FINAL.pdf"):

    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='NormalUTF8', fontName='Arial', fontSize=10))

    for bloque in bloques:
        story.append(Paragraph(f"<b>ARCHIVO: {bloque['titulo']}</b>", styles["Heading1"]))
        story.append(Spacer(1, 12))

        texto = f"<b>Fuerza máxima:</b> {bloque['fuerza_max']:.6f} N<br/>"
        texto += f"<b>Desplazamiento en fuerza máxima:</b> {bloque['deformacion_max']:.6f} mm<br/><br/>"
        texto += f"<b>Número total de ciclos detectados:</b> {bloque['total_ciclos']}<br/><br/>"
        texto += "<b>Deformaciones de ciclos seleccionados:</b><br/>"

        # Filtrar solo ciclos 0, 100, 200, 300, ...
        for k in sorted(bloque["ciclos"].keys()):
            if k % 100 == 0 or k == 0:
                c = bloque["ciclos"][k]
                texto += (f"Ciclo {k}: HIGH inicio = {c['deform_high_start']:.6f}, "
                          f"LOW = {c['deform_low']:.6f}, "
                          f"HIGH final = {c['deform_high_end']:.6f}<br/>")

        story.append(Paragraph(texto, styles["NormalUTF8"]))
        story.append(Spacer(1, 12))

        story.append(Image(bloque["grafico"], width=500, height=300))
        story.append(PageBreak())

    doc.build(story)
    return output_pdf