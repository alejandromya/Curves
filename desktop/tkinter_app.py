import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import pathlib

# ============================================
# Importar lógica
# ============================================
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
CURVES_DIR = BASE_DIR / "curves"
sys.path.insert(0, str(CURVES_DIR))

from main import procesar_columna

# ============================================
# UI por columna
# ============================================
class ColumnUI:
    def __init__(self, parent, col_id):
        self.col_id = col_id
        self.files = []

        frame = tk.LabelFrame(parent, text=f"Informe {col_id}", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Button(frame, text="Seleccionar CSVs", command=self.add_files).pack(anchor="w")

        self.listbox = tk.Listbox(frame, width=60)
        self.listbox.pack(pady=5)

        tk.Button(frame, text="Eliminar archivo", command=self.remove_file).pack(anchor="w")

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar CSVs",
            filetypes=[("CSV", "*.csv")]
        )
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def remove_file(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            self.listbox.delete(idx)
            del self.files[idx]

# ============================================
# App principal ****
# ============================================
class App:
    def __init__(self, root):
        root.title("Curves · Generador de Informes")

        self.columns = []

        self.cols_frame = tk.Frame(root)
        self.cols_frame.pack()

        params = tk.Frame(root)
        params.pack(pady=5)

        self.pico = tk.DoubleVar(value=75)
        self.valle = tk.DoubleVar(value=10)
        self.toler = tk.DoubleVar(value=5)

        tk.Label(params, text="Pico").grid(row=0, column=0)
        tk.Entry(params, textvariable=self.pico, width=6).grid(row=0, column=1)

        tk.Label(params, text="Valle").grid(row=0, column=2)
        tk.Entry(params, textvariable=self.valle, width=6).grid(row=0, column=3)

        tk.Label(params, text="Tolerancia").grid(row=0, column=4)
        tk.Entry(params, textvariable=self.toler, width=6).grid(row=0, column=5)

        tk.Button(root, text="Generar Informes", command=self.generar).pack(pady=10)

        self.add_column()

    def add_column(self):
        col = ColumnUI(self.cols_frame, len(self.columns) + 1)
        self.columns.append(col)

    def generar(self):
        for col in self.columns:
            if not col.files:
                continue
            try:
                res = procesar_columna(
                    pico=self.pico.get(),
                    valle=self.valle.get(),
                    toler=self.toler.get(),
                    columna_actual=col.col_id,
                    csv_files=col.files
                )
                messagebox.showinfo(
                    "Éxito",
                    f"Informe {col.col_id} generado:\n\n"
                    f"PDF: {res['pdf']}\n"
                    f"Excel: {res['excel']}\n"
                    f"Word: {res['word']}"
                )
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

# ============================================
# Start
# ============================================
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
