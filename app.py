import pydeck as pdk
import streamlit as st
import time
import pandas as pd
import geopandas as gpd

t0 = time.time()

# Configuration de la page web
st.set_page_config(page_title="GEOINT - Climat", layout="wide")

st.title("🌍 Dashboard GEOINT : Vulnérabilité Climatique")
st.markdown("""
Cette application interactive présente l'évaluation de la vulnérabilité des infrastructures 
industrielles face au risque de submersion marine dans l'estuaire de la Loire.
""")

@st.cache_data
def load_data():
    """Charge et met en cache les données pour ne pas les recharger à chaque clic."""
    # 1. Infrastructures saines (Overture Maps)
    gdf_all = gpd.read_parquet('data/processed/infrastructures_donges.parquet')
    
    # 2. Bâtiments menacés (via Pandas + conversion propre)
    df_menaces = pd.read_parquet('data/processed/batiments_menaces.parquet')
    
    if df_menaces.empty:
        gdf_menaces = gpd.GeoDataFrame()
    else:
        # On remplace directement la colonne binaire 'geom' par la géométrie lisible
        df_menaces['geom'] = gpd.GeoSeries.from_wkb(df_menaces['geom'])
        # On crée le GeoDataFrame en précisant que 'geom' est la colonne active
        gdf_menaces = gpd.GeoDataFrame(df_menaces, geometry='geom')
        gdf_menaces = gdf_menaces.set_crs('EPSG:4326', allow_override=True)
        
    # 3. Zones de submersion (Data.gouv.fr)
    gdf_inondations = gpd.read_parquet('data/processed/inondations.parquet')    
    # On force le système de coordonnées pour la carte web (WGS84)
    gdf_all = gdf_all.set_crs('EPSG:4326', allow_override=True)
    if not gdf_menaces.empty:
        gdf_menaces = gdf_menaces.set_crs('EPSG:4326', allow_override=True)
    gdf_inondations = gdf_inondations.to_crs('EPSG:4326')
    
    return gdf_all, gdf_menaces, gdf_inondations

# Chargement des données
with st.spinner("Chargement des données géospatiales..."):
    gdf_all, gdf_menaces, gdf_inondations = load_data()

t1 = time.time()

# Mise en page avec des colonnes pour les statistiques
col1, col2, col3 = st.columns(3)
col1.metric("Bâtiments analysés", f"{len(gdf_all):,}")
col2.metric("Infrastructures menacées", f"{len(gdf_menaces):,}")
col3.metric("Zone d'étude", "Estuaire de la Loire")

st.subheader("🗺️ Carte de vulnérabilité (Rendu GPU WebGL)")

# 1. On définit la vue initiale (Centrée sur l'estuaire, avec un angle 3D)
view_state = pdk.ViewState(
    latitude=47.30, 
    longitude=-2.07,
    zoom=11,
    pitch=45  # Permet d'incliner la carte en 3D !
)

# 2. Couche des zones d'inondation (Bleu transparent)
layer_inondation = pdk.Layer(
    "GeoJsonLayer",
    gdf_inondations,
    opacity=0.3,
    stroked=False,
    filled=True,
    get_fill_color="[0, 100, 255, 100]",  # Code couleur RGBA
)

# 3. Couche des bâtiments menacés (Rouge vif)
layer_batiments = pdk.Layer(
    "GeoJsonLayer",
    gdf_menaces,
    opacity=0.8,
    stroked=True,
    get_line_color="[255, 255, 255]",
    lineWidthMinPixels=1,
    filled=True,
    get_fill_color="[255, 0, 0, 200]",
    pickable=True
)

# 4. Affichage dans Streamlit
r = pdk.Deck(
    layers=[layer_inondation, layer_batiments],
    initial_view_state=view_state,
    # Utilisation d'un fond de carte sombre gratuit pour faire ressortir les couleurs
    map_style=pdk.map_styles.DARK, 
    tooltip={"text": "Infrastructure critique"}
)

st.pydeck_chart(r)

t2 = time.time()

# Affichage des chronomètres
st.write(f"⏱️ Chargement des données : {t1 - t0:.2f}s")
st.write(f"⏱️ Préparation Pydeck : {t2 - t1:.2f}s")