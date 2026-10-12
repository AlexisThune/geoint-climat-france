import duckdb

# Crée un fichier de base de données local
con = duckdb.connect('projet_geoint.duckdb')

print("Installation de l'extension spatiale...")
con.execute("INSTALL spatial;")

print("Chargement de l'extension...")
con.execute("LOAD spatial;")

# Test rapide pour vérifier que la géométrie fonctionne
resultat = con.execute("SELECT ST_GeomFromText('POINT(2.2945 48.8584)') AS tour_eiffel;").df()
print("Test réussi ! Voici le point géographique :")
print(resultat)