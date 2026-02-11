from docx import Document
import os
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from src.tables_generator import generar_tablas_combinadas
from desktop.paths import resource_path

# Rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # curves/curves/src
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # curves
UPLOADS_DIR = os.path.join(PROJECT_DIR, "uploads")


def generar_word_unico(bloques, output_doc):
    """
    Añade tablas y gráficas al final de un documento Word existente.
    """
    doc_name = 'FORM-ID-31_V5.0.docx'
    doc_path = resource_path(doc_name)  # la plantilla al mismo nivel que el exe
    print("📄 Usando Word:", doc_path)

    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"No existe la plantilla Word: {doc_path}")

    # Abrir plantilla existente
    doc = Document(doc_path)
    doc.add_page_break()  # empezar en nueva página

    # Función auxiliar para añadir párrafos
    def add_paragraph(text, bold=False, font_name='Arial', font_size=10, align=None):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold
        run.font.name = font_name
        run.font.size = Pt(font_size)
        if align:
            p.alignment = align
        return p

    # Título principal
    add_paragraph("Resultados", bold=True, font_size=14, align=WD_PARAGRAPH_ALIGNMENT.CENTER)
    doc.add_paragraph()  # espacio

    # Generar tablas combinadas
    (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd) = generar_tablas_combinadas(bloques)

    # Función para crear tablas seguras
    def add_table(headers, filas):
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Normal Table'  # estilo seguro

        # Encabezados
        hdr_cells = table.rows[0].cells
        for i, header in enumerate(headers):
            hdr_cells[i].text = str(header)
            hdr_run = hdr_cells[i].paragraphs[0].runs[0]
            hdr_run.bold = True
            hdr_run.font.name = 'Arial'
            hdr_run.font.size = Pt(10)
            hdr_cells[i].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Filas de datos
        for fila in filas:
            row_cells = table.add_row().cells
            for i, value in enumerate(fila):
                row_cells[i].text = str(value)
                row_run = row_cells[i].paragraphs[0].runs[0]
                row_run.font.name = 'Arial'
                row_run.font.size = Pt(10)
                row_cells[i].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        doc.add_paragraph()  # espacio
        return table

    # Agregar tablas
    add_table(headers_cyclic, filas_cyclic)
    add_table(headers_3rd, filas_3rd)

    # Agregar gráficas por bloque
    for bloque in bloques:
        doc.add_page_break()
        add_paragraph(bloque['titulo'], bold=True, font_size=12, align=WD_PARAGRAPH_ALIGNMENT.CENTER)
        doc.add_paragraph()  # espacio
        doc.add_picture(bloque['grafico'], width=Inches(6))

    # Guardar documento
    doc.save(output_doc)
    return output_doc
