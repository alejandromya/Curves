import os
import sys
import shutil
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# ================================
# Ajustar PATH para importar /curves
# ================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURVES_PATH = os.path.join(BASE_DIR, "curves")
sys.path.append(CURVES_PATH)

from main import procesar_columna
from src.data_processing import cargar_y_preparar_csv

# ================================
# Logging
# ================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# ================================
# Carpetas temporales
# ================================
UPLOAD_FOLDER = "/tmp/uploads"
RESULTS_FOLDER = "/tmp/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ================================
# Flask App
# ================================
app = Flask(__name__)
CORS(app)

@app.after_request
def cors_headers(response):
    origen = request.headers.get("Origin")
    if origen in ["http://localhost:5173", "https://curves-frontend.vercel.app"]:
        response.headers["Access-Control-Allow-Origin"] = origen
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ===========================================
# Procesar CSVs de una columna → Genera PDF
# ===========================================
@app.route("/procesar_csv", methods=["POST"])
def procesar_csv():
    try:
        columna = request.form.get("columna")
        if not columna:
            return jsonify({"error": "No se recibió columna"}), 400

        files = request.files.getlist("csv_files")
        if not files:
            return jsonify({"error": "No se recibieron archivos"}), 400

        # Carpeta propia para la columna
        col_folder = os.path.join(UPLOAD_FOLDER, f"col{columna}")
        os.makedirs(col_folder, exist_ok=True)

        # Guardar archivos
        for idx, file in enumerate(files):
            filename = f"{idx+1}_{file.filename}"
            path = os.path.join(col_folder, filename)
            file.save(path)
            logging.info(f"Guardado: {path}")

        # Parámetros opcionales
        pico = float(request.form.get("pico", 75))
        valle = float(request.form.get("valle", 10))
        toler = float(request.form.get("toler", 5))

        # Procesamiento real
        resultado = procesar_columna(pico, valle, toler, columna)

        pdf_path = resultado["pdf"]
        if not os.path.exists(pdf_path):
            return jsonify({"error": "No se generó el PDF"}), 500

        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"INFORME_COL{columna}.pdf"
        )

    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error procesando CSV", "detalle": str(e)}), 500


# ===========================================
# Descargar Excel global
# ===========================================
@app.route("/descargar_excel", methods=["GET"])
def descargar_excel():
    try:
        excel_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.xlsx")
        if not os.path.exists(excel_path):
            return jsonify({"error": "Excel no encontrado"}), 404

        return send_file(
            excel_path,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="INFORME_TOTAL.xlsx"
        )
    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error al descargar Excel", "detalle": str(e)}), 500



# ===========================================
# Descargar Word global
# ===========================================
@app.route("/descargar_word", methods=["GET"])
def descargar_word():
    try:
        word_path = os.path.join(RESULTS_FOLDER, "INFORME_TOTAL.docx")
        if not os.path.exists(word_path):
            return jsonify({"error": "Word no encontrado"}), 404

        return send_file(
            word_path,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name="INFORME_TOTAL.docx"
        )
    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error al descargar Word", "detalle": str(e)}), 500



# ===========================================
# Procesar CSV bruto (para preview)
# ===========================================
@app.route("/procesar_csv_bruto", methods=["POST"])
def procesar_csv_bruto():
    try:
        if "csv_file" not in request.files:
            return jsonify({"error": "No se recibió archivo"}), 400

        file = request.files["csv_file"]
        tmp_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(tmp_path)

        df = cargar_y_preparar_csv(tmp_path)
        puntos = df.iloc[:, :2].to_dict(orient="records")

        return jsonify({"puntos": puntos})

    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error procesando CSV bruto", "detalle": str(e)}), 500


# ===========================================
# Limpiar carpetas
# ===========================================
@app.route("/limpiar_carpetas", methods=["POST"])
def limpiar_carpetas():
    try:
        for folder in (UPLOAD_FOLDER, RESULTS_FOLDER):
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}


@app.route("/")
def index():
    return "Backend de Curves funcionando."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
