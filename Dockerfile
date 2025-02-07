# 1. Utiliser une image officielle de Python
FROM python:3.9

# 2. Définir le répertoire de travail
WORKDIR /app

# 3. Installer Nmap (important pour éviter l'erreur)
RUN apt-get update && apt-get install -y nmap

# 4. Copier les fichiers du projet dans le conteneur
COPY . /app

# 5. Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Exposer le port Flask (5000)
EXPOSE 5000

# 7. Lancer l'application
CMD ["python", "app.py"]
