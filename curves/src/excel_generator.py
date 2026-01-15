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
            ws.cell(row=1, column=1, value="Deformacion")
            ws.cell(row=1, column=2, value="Fuerza")

            for r_idx, (_, row) in enumerate(df.iterrows(), start=2):
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
            # Crear un diccionario para buscar correspondencias fácilmente
            deform_list = df["Deformacion"].tolist()
            fuerza_list = df["Fuerza"].tolist()

            # 1️⃣ Ciclos: están en filas_cyclic[i], columnas 1 a 6 en los datos resumidos (deform_high_end)
            # Recuerda: filas_cyclic[i] = [Sample, 0, 10, 50, 100, 250, 500, cyclic_stiffness]
            for val in filas_cyclic[i][1:7]:  # omite Sample y cyclic_stiffness
                if val == "—":
                    continue
                try:
                    val_float = float(val)
                    # Buscar el índice más cercano en Deformacion
                    idx = min(range(len(deform_list)), key=lambda j: abs(deform_list[j]-val_float))
                    # Pintar fila idx+2 (porque datos empiezan en fila 2)
                    ws.cell(row=idx+2, column=1).fill = yellow_fill
                    ws.cell(row=idx+2, column=1).font = black_font
                except:
                    continue

            # 2️⃣ Fmax, MaxDisp y fuerzas a 2mm/3mm: columnas 1..5 en filas_3rd[i]
            for j, val in enumerate(filas_3rd[i]):
                if val == "—":
                    continue
                try:
                    val_float = float(val)
                    # Buscar el valor más cercano en Fuerza o Deformacion según columna
                    # FMax y Force at 2/3mm -> Fuerza
                    if j in [0,1,3,4]:  # yield_stiffness, FMax, 2mm, 3mm -> Fuerza
                        idx = min(range(len(fuerza_list)), key=lambda k: abs(fuerza_list[k]-val_float))
                        ws.cell(row=idx+2, column=2).fill = yellow_fill
                        ws.cell(row=idx+2, column=2).font = black_font
                    # Max Disp ATM -> Deformacion
                    if j == 2:
                        idx = min(range(len(deform_list)), key=lambda k: abs(deform_list[k]-val_float))
                        ws.cell(row=idx+2, column=1).fill = yellow_fill
                        ws.cell(row=idx+2, column=1).font = black_font
                except:
                    continue

    wb.save(excel_path)
    return excel_path
