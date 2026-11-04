# Imagen base: Debian mínimo con Python 3.11 ya instalado ("slim" = versión ligera)
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor; los comandos siguientes se ejecutan aquí
WORKDIR /code

# La imagen base trae un setuptools antiguo que lleva dentro copias de otras librerías
# (jaraco.context, wheel) con vulnerabilidades conocidas. Actualizarlo las arregla
RUN pip install --no-cache-dir --upgrade setuptools wheel

# Primero solo las dependencias: mientras requirements.txt no cambie,
# Docker reutiliza esta capa de la caché y no reinstala nada al cambiar el código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Después el código (lo que más cambia va al final para aprovechar la caché)
COPY app ./app

# Documenta el puerto en el que escucha la app (no lo publica por sí solo)
EXPOSE 8000

# Comando que se ejecuta al arrancar el contenedor.
# --host 0.0.0.0 es necesario: con el valor por defecto (127.0.0.1) la app
# solo sería accesible desde dentro del propio contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
