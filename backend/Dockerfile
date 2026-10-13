# ==========================================
# BACKEND DOCKERFILE - Art Manager API
# ==========================================

# Usamos Python 3.12 slim (ligero y oficial)
FROM python:3.12-slim

# Variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el requirements.txt (optimización de caché de Docker)
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del backend
COPY . .

# Creamos la carpeta de uploads si no existe
RUN mkdir -p app/uploads

# Puerto que expone FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]