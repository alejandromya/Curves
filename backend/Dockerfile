FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/curves:$PYTHONPATH

WORKDIR /app

# Instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar backend y carpeta curves (para inicial build)
COPY backend/ /app
COPY curves/ /app/curves

EXPOSE 5000

# Flask en modo desarrollo con hot reload
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]