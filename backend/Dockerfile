FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/curves:$PYTHONPATH
ENV FLASK_APP=server.py
ENV FLASK_ENV=development

WORKDIR /app

# Instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar requisitos del backend
COPY backend/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar backend completo
COPY backend/ /app

# Copiar carpeta curves
COPY curves/ /app/curves

EXPOSE 5000

# Ejecutar Flask con hot reload
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
