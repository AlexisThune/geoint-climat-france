import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

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

# Mise en page avec des colonnes pour les statistiques
col1, col2, col3 = st.columns(3)
col1.metric("Bâtiments analysés", f"{len(gdf_all):,}")
col2.metric("Infrastructures menacées", f"{len(gdf_menaces):,}")
col3.metric("Zone d'étude", "Estuaire de la Loire")

st.markdown("### 🗺️ Carte d'Analyse Interactive")

# Initialisation de la carte Folium centrée sur Donges
m = folium.Map(
    location=[47.31, -2.15], 
    zoom_start=13, 
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
)
# Couche 1 : Zone d'inondation (Bleu transparent)
folium.GeoJson(
    gdf_inondations,
    name="Zones de submersion",
    style_function=lambda x: {'fillColor': '#00a8ff', 'color': '#00a8ff', 'weight': 1, 'fillOpacity': 0.2}
).add_to(m)

# Couche 2 : Bâtiments sains (Gris)
folium.GeoJson(
    gdf_all,
    name="Infrastructures (Saines)",
    style_function=lambda x: {'fillColor': '#a9a9a9', 'color': '#a9a9a9', 'weight': 0.5, 'fillOpacity': 0.4}
).add_to(m)

# Couche 3 : Bâtiments en danger (Rouge vif avec infobulles cliquables)
if not gdf_menaces.empty:
    folium.GeoJson(
        gdf_menaces,
        name="Infrastructures (Vulnérables)",
        style_function=lambda x: {'fillColor': '#ff4757', 'color': '#ff4757', 'weight': 2, 'fillOpacity': 0.8},
        tooltip=folium.GeoJsonTooltip(fields=['nom'], aliases=['Bâtiment:'], localize=True)
    ).add_to(m)

# Ajout d'un contrôleur pour activer/désactiver les couches
folium.LayerControl().add_to(m)

# Affichage de la carte dans Streamlit
st_data = st_folium(m, width=1200, height=600, returned_objects=[])