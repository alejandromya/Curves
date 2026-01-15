from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from src.tables_generator import generar_tablas_combinadas


def agregar_hoja_excel(bloques, col_id, excel_path_template="INFORME_COL{col}.xlsx"):

    excel_path = excel_path_template.format(col=col_id)

    wb = Workbook()
    if wb.active:
        wb.remove(wb.active)

    # Obtener headers y filas directamente
    (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd) = generar_tablas_combinadas(bloques)

    # Combinar headers para Excel
    headers = headers_cyclic + headers_3rd

    for i, bloque in enumerate(bloques):
        sample_name = bloque.get("titulo", "Sample")
        sheet_name = sample_name.replace("/", "_").replace("\\", "_")

        ws = wb.create_sheet(title=sheet_name)

        # Cabecera
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = h
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # Fila: ya incluye 'Sample' como primera columna
        fila = filas_cyclic[i] + filas_3rd[i]

        for col_idx, value in enumerate(fila, start=1):
            ws.cell(row=2, column=col_idx).value = value

    wb.save(excel_path)
    return excel_path