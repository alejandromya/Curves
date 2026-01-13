from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from src.tables_generator import generar_tablas_combinadas


def agregar_hoja_excel(bloques, col_id, excel_path_template="INFORME_COL{col}.xlsx"):

    excel_path = excel_path_template.format(col=col_id)

    wb = Workbook()
    if wb.active:
        wb.remove(wb.active)

    headers = [
        "Sample", "1", "10", "50", "100", "250", "500",
        "Cyclic Stiffness (N/mm)", "Yield Stiffness (N/mm)",
        "FMax ATM (N)", "Max Disp ATM (mm)",
        "Force at 2mm (N)", "Force at 3mm (N)"
    ]

    # 🔥 AQUÍ ESTÁ LA CLAVE
    (_, filas_cyclic), (_, filas_3rd) = generar_tablas_combinadas(bloques)


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

        fila = [
            sample_name,
            *filas_cyclic[i][:6],
            filas_cyclic[i][6],
            *filas_3rd[i]
        ]

        for col_idx, value in enumerate(fila, start=1):
            ws.cell(row=2, column=col_idx).value = value

    wb.save(excel_path)
    return excel_path