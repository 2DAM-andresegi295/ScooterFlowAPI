# 1. Imagen base ligera y estable
FROM python:3.13-slim

# 2. Variables de entorno para optimizar Python en contenedores
# No escribe archivos .pyc y envía logs directamente a la consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecer el directorio de trabajo
WORKDIR /app

# 4. Instalar dependencias del sistema (si son necesarias)
# Limpiamos la caché de apt para mantener la imagen pequeña
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalar dependencias de Python
# Copiamos solo el requirements primero para aprovechar la caché de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Crear un usuario no-root por seguridad
# Por defecto, Docker corre como root, lo cual es un riesgo de seguridad
RUN useradd -m myuser
# Añade esto para que el usuario sea dueño de la carpeta de trabajo
RUN chown -R myuser:myuser /app
USER myuser

# 7. Copiar el resto del código
COPY ./app ./app

# 8. Exponer el puerto (FastAPI suele usar el 8000)
EXPOSE 8000

# 9. Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]