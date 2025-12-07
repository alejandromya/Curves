from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment
import os
from src.tables_generator import generar_fila_sample

# ---------------------------
# Excel: una hoja por columna
# ---------------------------
def agregar_hoja_excel(bloques, col_id, excel_path="INFORME_TOTAL.xlsx"):
    """
    bloques: lista de bloques de una columna (cada bloque = CSV)
    col_id: número de columna
    excel_path: ruta del Excel a crear/actualizar
    """
    if os.path.exists(excel_path):
        wb = load_workbook(excel_path)
    else:
        wb = Workbook()
        # eliminar hoja activa por defecto
        if wb.active:
            wb.remove(wb.active)

    ws = wb.create_sheet(title=f"Columna {col_id}")
    fila_actual = 1

    if not bloques:
        wb.save(excel_path)
        return excel_path

    # Cabecera fija
    headers = ["Sample", "1", "10", "50", "100", "250", "500",
               "Cyclic Stiffness (N/mm)", "Yield Stiffness (N/mm)",
               "FMax ATM (N)", "Max Disp ATM (mm)", "Force at 2mm (N)", "Force at 3mm (N)"]

    # Escribir cabecera
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=fila_actual, column=col_idx)
        cell.value = h
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
    fila_actual += 1

    # Filas con datos
    for bloque in bloques:
        fila = generar_fila_sample(bloque)
        for col_idx, v in enumerate(fila, start=1):
            ws.cell(row=fila_actual, column=col_idx).value = v
        fila_actual += 1

    wb.save(excel_path)
    return excel_path
