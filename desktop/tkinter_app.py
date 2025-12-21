import tkinter as tk
from tkinter import filedialog, messagebox
import os
from functools import partial
import shutil

# Ajuste de path para importar curvas/main.py
import sys, pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
CURVES_DIR = BASE_DIR / "curves"
sys.path.insert(0, str(CURVES_DIR))

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

from main import procesar_columna  # Lógica principal

class ColumnUI:
    def __init__(self, parent, col_id):
        self.col_id = col_id
        self.files = []

        self.frame = tk.LabelFrame(parent, text=f"Informe {col_id}", padx=10, pady=10)
        self.frame.pack(padx=10, pady=5, fill="x")

        self.add_btn = tk.Button(self.frame, text="Seleccionar CSVs", command=self.add_files)
        self.add_btn.pack(anchor="w")

        self.file_listbox = tk.Listbox(self.frame, width=50)
        self.file_listbox.pack(anchor="w", pady=5)

        self.remove_btn = tk.Button(self.frame, text="Eliminar archivo", command=self.remove_file)
        self.remove_btn.pack(anchor="w")

    def add_files(self):
        files = filedialog.askopenfilenames(title="Seleccionar CSVs", filetypes=[("CSV", "*.csv")])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))

    def remove_file(self):
        selected = self.file_listbox.curselection()
        if selected:
            idx = selected[0]
            self.file_listbox.delete(idx)
            del self.files[idx]

class App:
    def __init__(self, root):
        self.root = root
        root.title("Generador de Informes Local")

        self.columns = []
        self.columns_frame = tk.Frame(root)
        self.columns_frame.pack()

        # Parámetros pico/valle/tolerancia
        self.params_frame = tk.Frame(root)
        self.params_frame.pack(pady=5)

        tk.Label(self.params_frame, text="Pico").grid(row=0, column=0)
        self.pico_var = tk.DoubleVar(value=75)
        tk.Entry(self.params_frame, textvariable=self.pico_var, width=5).grid(row=0, column=1)

        tk.Label(self.params_frame, text="Valle").grid(row=0, column=2)
        self.valle_var = tk.DoubleVar(value=10)
        tk.Entry(self.params_frame, textvariable=self.valle_var, width=5).grid(row=0, column=3)

        tk.Label(self.params_frame, text="Tolerancia").grid(row=0, column=4)
        self.toler_var = tk.DoubleVar(value=5)
        tk.Entry(self.params_frame, textvariable=self.toler_var, width=5).grid(row=0, column=5)

        tk.Button(root, text="Generar Informes", command=self.send_all).pack(pady=10)

        # Inicializa con una columna
        self.add_column()

    def add_column(self):
        col_id = len(self.columns) + 1
        col_ui = ColumnUI(self.columns_frame, col_id)
        self.columns.append(col_ui)

    def send_all(self):
        pico = self.pico_var.get()
        valle = self.valle_var.get()
        toler = self.toler_var.get()

        for col_ui in self.columns:
            if not col_ui.files:
                continue

            # Crear carpeta de la columna
            col_folder = os.path.join(UPLOAD_FOLDER, f"col{col_ui.col_id}")
            os.makedirs(col_folder, exist_ok=True)

            # Copiar todos los CSV seleccionados a la carpeta de la columna
            csv_paths = []
            for f in col_ui.files:
                dest = os.path.join(col_folder, os.path.basename(f))
                shutil.copy2(f, dest)
                csv_paths.append(dest)

            try:
                # Llamar a procesar_columna pasando la lista de archivos
                resultado = procesar_columna(
                    pico=pico,
                    valle=valle,
                    toler=toler,
                    columna_actual=col_ui.col_id,
                    csv_files=csv_paths  # aquí pasamos los archivos
                )

                messagebox.showinfo(
                    "Éxito",
                    f"Columna {col_ui.col_id} procesada.\nPDF: {resultado['pdf']}\nExcel: {resultado['excel']}\nWord: {resultado['word']}"
                )

            except Exception as e:
                messagebox.showerror("Error", f"Error procesando columna {col_ui.col_id}: {e}")
                return

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
