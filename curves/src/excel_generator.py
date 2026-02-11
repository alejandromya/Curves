from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from curves.src.tables_generator import generar_tablas_combinadas


# ============================================================
# HELPERS
# ============================================================

def to_number(val):
    """
    Convierte a float si es posible.
    Devuelve None si no es numérico.
    """
    if val in (None, "—", "", "-", "NaN"):
        return None

    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def get_valid_indexes(lst):
    """
    Devuelve índices donde el valor no es None
    """
    return [i for i, v in enumerate(lst) if v is not None]


# ============================================================
# MAIN
# ============================================================

def agregar_hoja_excel(
    bloques,
    col_id,
    excel_path_template="INFORME_COL{col}.xlsx"
):

    excel_path = excel_path_template.format(col=col_id)

    wb = Workbook()

    if wb.active:
        wb.remove(wb.active)

    yellow_fill = PatternFill(
        start_color="FFFF00",
        end_color="FFFF00",
        fill_type="solid"
    )

    black_font = Font(color="000000")

    # Obtener headers y filas
    (headers_cyclic, filas_cyclic), (headers_3rd, filas_3rd) = generar_tablas_combinadas(bloques)

    # Combinar headers
    headers_tabla = headers_cyclic + headers_3rd


    # ========================================================
    # LOOP BLOQUES
    # ========================================================

    for i, bloque in enumerate(bloques):

        sample_name = bloque.get("titulo", "Sample")

        sheet_name = (
            sample_name
            .replace("/", "_")
            .replace("\\", "_")
        )

        ws = wb.create_sheet(title=sheet_name)

        # ====================================================
        # DATOS CSV
        # ====================================================

        df = bloque.get("df")

        deform_list = []
        fuerza_list = []

        if df is not None:

            # Headers
            ws.cell(row=3, column=1, value="Deformacion")
            ws.cell(row=3, column=2, value="Fuerza")
            ws.cell(row=3, column=3, value="Header")

            deform_list = [
                to_number(v) for v in df["Deformacion"]
            ]

            fuerza_list = [
                to_number(v) for v in df["Fuerza"]
            ]

            for r_idx, (_, row) in enumerate(
                df.iterrows(),
                start=4
            ):

                ws.cell(
                    row=r_idx,
                    column=1,
                    value=to_number(row["Deformacion"])
                )

                ws.cell(
                    row=r_idx,
                    column=2,
                    value=to_number(row["Fuerza"])
                )


        # ====================================================
        # TABLA COMBINADA
        # ====================================================

        start_col = 4  # Columna D

        # Headers
        for col_idx, h in enumerate(
            headers_tabla,
            start=start_col
        ):

            cell = ws.cell(
                row=1,
                column=col_idx,
                value=h
            )

            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")


        # Datos
        fila = filas_cyclic[i] + filas_3rd[i]

        for col_idx, value in enumerate(
            fila,
            start=start_col
        ):

            ws.cell(
                row=2,
                column=col_idx,
                value=to_number(value)
            )


        # ====================================================
        # RESALTADO DE VALORES
        # ====================================================

        if df is not None:

            valid_deform = get_valid_indexes(deform_list)
            valid_fuerza = get_valid_indexes(fuerza_list)


            # -------------------------
            # CICLOS
            # -------------------------

            for val_idx, val in enumerate(
                filas_cyclic[i][1:7]   # sin Sample
            ):

                val_float = to_number(val)

                if val_float is None:
                    continue

                if not valid_deform:
                    continue


                idx = min(
                    valid_deform,
                    key=lambda j: abs(
                        deform_list[j] - val_float # type: ignore
                    )
                )

                row_excel = idx + 4

                ws.cell(
                    row=row_excel,
                    column=1
                ).fill = yellow_fill

                ws.cell(
                    row=row_excel,
                    column=1
                ).font = black_font

                ws.cell(
                    row=row_excel,
                    column=3,
                    value=headers_cyclic[val_idx + 1]
                )


            # -------------------------
            # 3RD DATA
            # -------------------------

            for j, val in enumerate(
                filas_3rd[i]
            ):

                val_float = to_number(val)

                if val_float is None:
                    continue


                # Fuerzas
                if j in (1, 3, 4):

                    if not valid_fuerza:
                        continue

                    idx = min(
                        valid_fuerza,
                        key=lambda k: abs(
                            fuerza_list[k] - val_float # type: ignore
                        )
                    )

                    row_excel = idx + 4

                    ws.cell(
                        row=row_excel,
                        column=2
                    ).fill = yellow_fill

                    ws.cell(
                        row=row_excel,
                        column=2
                    ).font = black_font

                    ws.cell(
                        row=row_excel,
                        column=3,
                        value=headers_3rd[j]
                    )


                # Max Disp → Deformacion
                if j == 2:

                    if not valid_deform:
                        continue

                    idx = min(
                        valid_deform,
                        key=lambda k: abs(
                            deform_list[k] - val_float # type: ignore
                        )
                    )

                    row_excel = idx + 4

                    ws.cell(
                        row=row_excel,
                        column=1
                    ).fill = yellow_fill

                    ws.cell(
                        row=row_excel,
                        column=1
                    ).font = black_font

                    ws.cell(
                        row=row_excel,
                        column=3,
                        value=headers_3rd[j]
                    )


    # ========================================================
    # SAVE
    # ========================================================

    wb.save(excel_path)

    return excel_path
