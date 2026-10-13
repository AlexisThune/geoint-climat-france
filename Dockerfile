# 1. On part d'un système Linux ultra-léger avec une version stable de Python
# (On évite ton Python 3.14 trop récent pour éviter les bugs de dépendances !)
FROM python:3.11-slim

# 2. On crée un dossier de travail dans le conteneur
WORKDIR /app

# 3. On copie le fichier des dépendances et on les installe
# (Tu devras créer un fichier requirements.txt avec streamlit, folium, streamlit-folium, pandas, geopandas, pyarrow)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. On copie le code de l'application et les données calculées
COPY app.py .
COPY data/processed/ ./data/processed/

# 5. On indique le port sur lequel Streamlit va communiquer
EXPOSE 8501

# 6. LA COMMANDE MAGIQUE !
# C'est l'équivalent de ton "streamlit run app.py" mais adapté pour un serveur
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]