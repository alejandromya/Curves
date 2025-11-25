from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import logging

# Configuración logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
CORS(app)

BASE_UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
RESULTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route("/procesar_csv", methods=["POST"])
def procesar_csv():
    try:
        columna = request.form.get("columna")
        if columna not in {"1", "2", "3"}:
            logging.warning(f"Columna inválida: {columna}")
            return jsonify({"error": "Columna inválida"}), 400

        files = request.files.getlist("csv_files")
        if not files:
            logging.warning("No se recibieron archivos")
            return jsonify({"error": "No se recibieron archivos"}), 400

        # Crear carpeta específica para la columna
        upload_folder = os.path.join(BASE_UPLOAD_FOLDER, f"columna_{columna}")
        os.makedirs(upload_folder, exist_ok=True)

        # Guardar archivos
        for idx, f in enumerate(files):
            safe_name = f"{idx+1}_{f.filename}"
            path = os.path.join(upload_folder, safe_name)
            f.save(path)
            logging.info(f"Archivo guardado: {path}")

        # Parámetros
        try:
            pico = float(request.form["pico"])
            valle = float(request.form["valle"])
            tolerancia = float(request.form["toler"])
        except KeyError as e:
            logging.error(f"Falta parámetro obligatorio: {e}")
            return jsonify({"error": f"Falta parámetro obligatorio: {e}"}), 400
        except ValueError as e:
            logging.error(f"Parámetro inválido: {e}")
            return jsonify({"error": f"Parámetro inválido: {e}"}), 400

        logging.info(f"Parámetros recibidos - Pico: {pico}, Valle: {valle}, Tolerancia: {tolerancia}")

        # Ejecutar main.py pasando carpeta de columna y parámetros
        main_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "curves", "main.py"))
        if not os.path.exists(main_py_path):
            logging.error(f"No se encontró main.py en: {main_py_path}")
            return jsonify({"error": "main.py no encontrado"}), 500

        pdf_path = os.path.join(RESULTS_FOLDER, f"INFORME_COL{columna}.pdf")
        logging.info(f"Ejecutando main.py para columna {columna}...")
        result = subprocess.run(
            ["python", main_py_path, upload_folder, str(pico), str(valle), str(tolerancia), pdf_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logging.error(f"main.py falló en columna {columna}: {result.stderr}")
            return jsonify({"error": f"Error al procesar CSVs columna {columna}", "detalle": result.stderr}), 500

        logging.info(f"PDF generado: {pdf_path}")

        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"INFORME_COL{columna}.pdf"
        )

    except Exception as e:
        logging.exception(f"Error inesperado: {e}")
        return jsonify({"error": "Error inesperado en el servidor", "detalle": str(e)}), 500

@app.route("/")
def index():
    return "Servidor Flask funcionando correctamente"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
