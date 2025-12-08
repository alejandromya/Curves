from flask import Flask, request, jsonify, send_file
from flask_cors import cross_origin 
import os
import subprocess
import shutil
import logging
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "curves")))

from src.data_processing import cargar_y_preparar_csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
# CORS(app)

UPLOAD_FOLDER = "/tmp/uploads"
RESULTS_FOLDER = "/tmp/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route("/procesar_csv", methods=["POST"])
@cross_origin(origins="https://curves-frontend.vercel.app") 
def procesar_csv():
    try:
        columna = request.form.get("columna")
        if not columna:
            return jsonify({"error": "No se recibió columna"}), 400

        files = request.files.getlist("csv_files")
        if not files:
            return jsonify({"error": "No se recibieron archivos"}), 400

        col_upload_folder = os.path.join(UPLOAD_FOLDER, f"col{columna}")
        os.makedirs(col_upload_folder, exist_ok=True)

        for idx, f in enumerate(files):
            safe_name = f"{idx+1}_{f.filename}"
            path = os.path.join(col_upload_folder, safe_name)
            f.save(path)
            logging.info(f"Archivo guardado: {path}")

        pico = float(request.form.get("pico", 75))
        valle = float(request.form.get("valle", 10))
        toler = float(request.form.get("toler", 5))

        main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "curves", "main.py"))

        logging.info(f"Ejecutando main.py para columna {columna}...")
        result = subprocess.run(
            ["python", main_py, str(pico), str(valle), str(toler), str(columna)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"main.py falló columna {columna}: {result.stderr}")
            return jsonify({"error": f"Error columna {columna}", "detalle": result.stderr}), 500

        pdf_path = os.path.join(RESULTS_FOLDER, f"INFORME_COL{columna}.pdf")
        if not os.path.exists(pdf_path):
            return jsonify({"error": f"No se generó PDF columna {columna}"}), 500

        return send_file(pdf_path, mimetype="application/pdf", as_attachment=True,
                         download_name=f"INFORME_COL{columna}.pdf")

    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error inesperado", "detalle": str(e)}), 500
    

@app.route("/descargar_excel", methods=["GET"])
@cross_origin(origins="https://curves-frontend.vercel.app") 
def descargar_excel():
    try:
        excel_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.xlsx")
        if not os.path.exists(excel_path):
            return jsonify({"error": "El Excel final no existe"}), 404

        return send_file(excel_path, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         as_attachment=True, download_name="INFORME_TOTAL.xlsx")
    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error al descargar Excel", "detalle": str(e)}), 500

@app.route("/limpiar_carpetas", methods=["POST"])
@cross_origin(origins="https://curves-frontend.vercel.app") 
def limpiar_carpetas():
    try:
        for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        return {"status": "ok", "message": "Carpetas limpiadas"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/procesar_csv_bruto", methods=["POST"])
@cross_origin(origins="https://curves-frontend.vercel.app") 
def procesar_csv_bruto():
    try:
        # Revisar que el archivo se haya enviado
        if "csv_file" not in request.files:
            return jsonify({"error": "No se recibió archivo"}), 400

        archivo = request.files["csv_file"]

        # Guardar archivo en uploads (igual que main.py)
        tmp_path = os.path.join(UPLOAD_FOLDER, archivo.filename)
        archivo.save(tmp_path)

        # Pasar el filepath a cargar_y_preparar_csv
        df = cargar_y_preparar_csv(tmp_path)

        # Convertir a JSON solo las dos primeras columnas (X e Y)
        puntos = df.iloc[:, :2].to_dict(orient="records")
        return jsonify({"puntos": puntos})

    except Exception as e:
        return jsonify({"error": "Error procesando CSV", "detalle": str(e)}), 500


@app.route("/")
def index():
    return "Hello from Curves backend!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
