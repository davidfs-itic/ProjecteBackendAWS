# Utilitzar imatge base oficial de Python
FROM python:3.11-slim

# Establir el directori de treball
WORKDIR /app

# Copiar els fitxers de requisits primer (per aprofitar la cache de Docker)
COPY requirements.txt .

# Instal·lar les dependències
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codi de l'aplicació
COPY main.py .

# Crear directori per certificats
RUN mkdir -p /app/certificates

# El contenidor esperarà els certificats i el .env com a volums
# o variables d'entorn en temps d'execució

# Executar l'aplicació
CMD ["python", "-u", "main.py"]