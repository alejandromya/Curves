from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def generar_tabla_ciclos(detalles_ciclos, df, fuerza_max, deformacion_max):
    """
    Tabla con columnas 0,100,...,hasta última centena + F2mm, F3mm, Fmax, Dciclico, Stf
    """

    ciclos_ordenados = sorted(detalles_ciclos.keys())

    primer_ciclo_key = ciclos_ordenados[0]
    primer_ciclo = detalles_ciclos[primer_ciclo_key]

    # Último HIGH real entre todos los ciclos
    ultimo_high_real = max(c["deform_high_end"] for c in detalles_ciclos.values())

    # Último ciclo
    ultimo_ciclo_key = ciclos_ordenados[-1]
    ultimo_ciclo = detalles_ciclos[ultimo_ciclo_key]

    # Columnas de ciclos: 0 → última centena
    ult_centena = (ultimo_ciclo_key // 100) * 100
    ciclos_col = [0] + [i for i in range(100, ult_centena + 1, 100)]

    # F2mm / F3mm medidos desde el LOW del último ciclo
    deform_low_last = ultimo_ciclo["deform_low"]
    f2mm_idx = (df["Deformacion"] - deform_low_last - 2.0).abs().idxmin()
    f3mm_idx = (df["Deformacion"] - deform_low_last - 3.0).abs().idxmin()

    f2mm_val = df.loc[f2mm_idx, "Fuerza"]
    f3mm_val = df.loc[f3mm_idx, "Fuerza"]

    # Fmax relativo al LOW (ya existente)
    df_max_rel_low = deformacion_max - deform_low_last

    # Fmax relativo al HIGH_END del último ciclo (nuevo)
    df_max_rel_high = deformacion_max - ultimo_ciclo["deform_high_end"]

    # Dciclico: último HIGH real − primer HIGH start
    Dciclico = ultimo_high_real - primer_ciclo["deform_high_start"]

    # Nuevo: Stf = Fmax / desplazamiento desde high_end
    Stf = fuerza_max / df_max_rel_high if df_max_rel_high != 0 else 0.0

    # Cabecera
    headers = [str(c) for c in ciclos_col] + [
        "F2mm", "F3mm",
        f"Fmax ({fuerza_max:.2f} N)",
        "Dciclico",
        "Stf (N/mm)"
    ]

    # Fila
    fila = []
    for c in ciclos_col:
        if c == 0:
            fila.append(f"{primer_ciclo['deform_high_start']:.4f}")

        elif c == ciclos_col[-1]:
            fila.append(f"{ultimo_high_real:.4f}")

        elif c in detalles_ciclos:
            fila.append(f"{detalles_ciclos[c]['deform_high_end']:.4f}")

        else:
            fila.append("—")

    fila.extend([
        f"{f2mm_val:.2f}",
        f"{f3mm_val:.2f}",
        f"{df_max_rel_low:.4f}",
        f"{Dciclico:.4f}",
        f"{Stf:.4f}"
    ])

    return [headers, fila]



def generar_pdf_unico(bloques, output_pdf="INFORME_FINAL.pdf"):

    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='NormalUTF8', fontName='Arial', fontSize=10))

    for bloque in bloques:
        story.append(Paragraph(f"<b>{bloque['titulo']}</b>", styles["Heading1"]))
        story.append(Spacer(1, 12))

        texto = f"<b>Fuerza máxima:</b> {bloque['fuerza_max']:.6f} N<br/>"
        story.append(Paragraph(texto, styles["NormalUTF8"]))
        story.append(Spacer(1, 12))

        tabla_datos = generar_tabla_ciclos(
            bloque["ciclos"],
            bloque["df"],
            bloque["fuerza_max"],
            bloque["deformacion_max"]
        )

        tabla = Table(tabla_datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))

        story.append(tabla)
        story.append(Spacer(1, 12))

        story.append(Image(bloque["grafico"], width=500, height=300))
        story.append(PageBreak())

    doc.build(story)
    return output_pdf