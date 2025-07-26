# 👇 On part d'une image Python 3.10 propre
FROM python:3.10-slim

# 👇 On définit le dossier de travail
WORKDIR /app

# 👇 On copie les fichiers de l'app dans le conteneur
COPY . /app

# 👇 On installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 👇 On lance le bot
CMD ["python", "bot_villas.py"]
