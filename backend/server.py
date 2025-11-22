from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import os
import subprocess
import logging
import shutil

# Configuración logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
RESULTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route("/procesar_csv", methods=["POST"])
def procesar_csv():
    try:
        # Archivos
        if "csv_files" not in request.files:
            logging.warning("No se recibieron archivos")
            return jsonify({"error": "No se recibieron archivos"}), 400

        files = request.files.getlist("csv_files")
        if not files:
            logging.warning("Lista de archivos vacía")
            return jsonify({"error": "No se recibieron archivos"}), 400

        # Guardar archivos
        for f in files:
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            logging.info(f"Archivo guardado: {path}")

        # Parámetros obligatorios
        data = request.form
        try:
            pico = float(data["pico"])
            valle = float(data["valle"])
            tolerancia = float(data["toler"])
        except KeyError as e:
            logging.error(f"Falta parámetro obligatorio: {e}")
            return jsonify({"error": f"Falta parámetro obligatorio: {e}"}), 400
        except ValueError as e:
            logging.error(f"Parámetro inválido: {e}")
            return jsonify({"error": f"Parámetro inválido: {e}"}), 400

        logging.info(f"Parámetros recibidos - Pico: {pico}, Valle: {valle}, Tolerancia: {tolerancia}")

        # Ejecutar main.py
        main_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "curves", "main.py"))
        if not os.path.exists(main_py_path):
            logging.error(f"No se encontró main.py en: {main_py_path}")
            return jsonify({"error": "main.py no encontrado"}), 500

        logging.info("Ejecutando main.py...")
        result = subprocess.run(
            ["python", main_py_path, str(pico), str(valle), str(tolerancia)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logging.error(f"main.py falló: {result.stderr}")
            return jsonify({"error": "Error al procesar CSVs", "detalle": result.stderr}), 500

        logging.info("main.py ejecutado correctamente")

        # PDF generado
        pdf_path = os.path.join(RESULTS_FOLDER, "INFORME_FINAL.pdf")
        if not os.path.exists(pdf_path):
            logging.error(f"No se generó el PDF en: {pdf_path}")
            return jsonify({"error": "No se generó el PDF"}), 500

        logging.info(f"PDF generado: {pdf_path}")

        # Limpiar carpetas después de enviar la respuesta
        @after_this_request
        def cleanup(response):
            try:
                for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
                    for f in os.listdir(folder):
                        path = os.path.join(folder, f)
                        if os.path.isfile(path):
                            os.remove(path)
                        elif os.path.isdir(path):
                            shutil.rmtree(path)
                logging.info("Carpetas uploads y results limpiadas")
            except Exception as e:
                logging.error(f"Error limpiando carpetas: {e}")
            return response

        return send_file(pdf_path, mimetype="application/pdf", as_attachment=True, download_name="INFORME_FINAL.pdf")

    except Exception as e:
        logging.exception(f"Error inesperado: {e}")
        return jsonify({"error": "Error inesperado en el servidor", "detalle": str(e)}), 500

@app.route("/")
def index():
    return "Servidor Flask funcionando correctamente"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
