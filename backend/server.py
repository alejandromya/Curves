from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "../results"  # donde main.py guarda el PDF
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/procesar_csv", methods=["POST"])
def procesar_csv():
    if "csv_files" not in request.files:
        return jsonify({"error": "No se recibieron archivos"}), 400

    files = request.files.getlist("csv_files")
    saved_files = []

    # Guardar archivos en uploads/
    for f in files:
        path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(path)
        saved_files.append(path)

    # Obtener parámetros enviados desde el frontend
    data = request.form
    pico = float(data.get("pico", 75))       # valor por defecto 75
    valle = float(data.get("valle", 10))     # valor por defecto 10
    tolerancia = float(data.get("toler", 5)) # valor por defecto 5

    # Ejecutar main.py con los parámetros
    main_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "curves", "main.py"))
    subprocess.run(
        ["python", main_py_path, str(pico), str(valle), str(tolerancia)],
        check=True
    )

    # PDF final generado por main.py
    pdf_path = os.path.join(RESULTS_FOLDER, "INFORME_FINAL.pdf")

    if not os.path.exists(pdf_path):
        return jsonify({"error": "No se generó el PDF"}), 500

    # Devolver PDF directamente al frontend
    return send_file(pdf_path, mimetype="application/pdf", as_attachment=True, download_name="INFORME_FINAL.pdf")


@app.route("/")
def index():
    return "Servidor Flask funcionando correctamente"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
