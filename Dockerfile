# Utilisez une image Python officielle comme image de base
FROM python:3.9-slim

# Définissez le répertoire de travail à la racine
WORKDIR /

# Copiez tous les fichiers dans le conteneur (y compris main.py et requirements.txt)
COPY . .

# Installez les dépendances Python spécifiées dans requirements.txt, si le fichier existe
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Commande pour exécuter le script Python
CMD ["python", "main.py"]
