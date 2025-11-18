FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code Python dans le conteneur
COPY tests/ .

# Par défaut : exécuter le script de migration
CMD ["python", "script_python_mongo.py"]

