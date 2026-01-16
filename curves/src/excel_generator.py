from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from src.tables_generator import generar_tablas_combinadas


def agregar_hoja_excel(bloques, col_id, excel_path_template="INFORME_COL{col}.xlsx"):

    excel_path = excel_path_template.format(col=col_id)

    wb = Workbook()
    if wb.active:
        wb.remove(wb.active)

    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    black_font = Font(color="000000")

    # Obtener headers y filas directamente
    (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd) = generar_tablas_combinadas(bloques)

    # Combinar headers para la tabla combinada
    headers_tabla = headers_cyclic + headers_3rd

    for i, bloque in enumerate(bloques):
        sample_name = bloque.get("titulo", "Sample")
        sheet_name = sample_name.replace("/", "_").replace("\\", "_")

        ws = wb.create_sheet(title=sheet_name)

        # ===============================
        # Datos brutos CSV en columna A y B
        # ===============================
        df = bloque.get("df")
        if df is not None:
            # Encabezado en fila 1
            ws.cell(row=3, column=1, value="Deformacion")
            ws.cell(row=3, column=2, value="Fuerza")
            ws.cell(row=3, column=3, value="Header")  # Nueva columna C

            deform_list = df["Deformacion"].tolist()
            fuerza_list = df["Fuerza"].tolist()

            for r_idx, (_, row) in enumerate(df.iterrows(), start=4):
                ws.cell(row=r_idx, column=1, value=row["Deformacion"])
                ws.cell(row=r_idx, column=2, value=row["Fuerza"])

        # ===============================
        # Tabla combinada a partir de columna D
        # ===============================
        start_col = 4  # columna D
        # Cabecera
        for col_idx, h in enumerate(headers_tabla, start=start_col):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = h
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # Fila de datos combinados (ya incluye 'Sample')
        fila = filas_cyclic[i] + filas_3rd[i]
        for col_idx, value in enumerate(fila, start=start_col):
            ws.cell(row=2, column=col_idx, value=value)

        # ===============================
        # Pintar los valores que aparecen en la tabla combinada
        # ===============================
        if df is not None:
            # 1️⃣ Ciclos (deform_high_end)
            for val_idx, val in enumerate(filas_cyclic[i][1:7]):  # omite Sample y cyclic_stiffness
                if val == "—":
                    continue
                try:
                    val_float = float(val)
                    # Buscar índice más cercano en Deformacion
                    idx = min(range(len(deform_list)), key=lambda j: abs(deform_list[j]-val_float))
                    row_excel = idx + 4
                    ws.cell(row=row_excel, column=1).fill = yellow_fill
                    ws.cell(row=row_excel, column=1).font = black_font
                    ws.cell(row=row_excel, column=3, value=headers_cyclic[val_idx+1])  # +1 porque omite Sample
                except:
                    continue

            # 2️⃣ Fmax, MaxDisp y fuerzas a 2mm/3mm
            for j, val in enumerate(filas_3rd[i]):
                if val == "—":
                    continue
                try:
                    val_float = float(val)
                    # FMax, Force at 2/3mm -> Fuerza (column B)
                    if j in [1,3,4]:  # FMax ATM, Force at 2mm, Force at 3mm
                        idx = min(range(len(fuerza_list)), key=lambda k: abs(fuerza_list[k]-val_float))
                        row_excel = idx + 4
                        ws.cell(row=row_excel, column=2).fill = yellow_fill
                        ws.cell(row=row_excel, column=2).font = black_font
                        ws.cell(row=row_excel, column=3, value=headers_3rd[j])
                    # Yield Stiffness (j=0) -> Fuerza? usualmente lo ignoramos para los datos brutos
                    # Max Disp ATM (j=2) -> Deformacion (col A)
                    if j == 2:
                        idx = min(range(len(deform_list)), key=lambda k: abs(deform_list[k]-val_float))
                        row_excel = idx + 4
                        ws.cell(row=row_excel, column=1).fill = yellow_fill
                        ws.cell(row=row_excel, column=1).font = black_font
                        ws.cell(row=row_excel, column=3, value=headers_3rd[j])
                except:
                    continue

    wb.save(excel_path)
    return excel_path
