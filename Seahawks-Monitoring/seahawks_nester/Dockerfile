# Utiliser une image Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de Nester
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 5001 (ou autre si besoin)
EXPOSE 5001

# Lancer l'application Flask
CMD ["python", "app.py"]
