FROM python:3.11

# Optimisations Python pour Docker
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Dossier de travail
WORKDIR /app

# Copie et install des dépendances (attention à la casse : requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le script de migration dans l'image
COPY migration.py /app/migration.py

# Commande d'exécution
CMD ["python", "-u", "/app/migration.py"]

