import duckdb

def setup_duckdb(db_path='../projet_geoint.duckdb'):
    """Initialise le moteur spatial et la connexion S3."""
    con = duckdb.connect(db_path)
    con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_region='us-west-2';")
    return con

def run_geoint_pipeline(con):
    """Exécute l'extraction Cloud et le croisement spatial local."""
    print("[1/2] Extraction des bâtiments stratégiques (Cloud -> Local)...")
    con.execute("""
        COPY (
            SELECT id, names.primary AS nom, height AS hauteur, geometry AS geom
            FROM read_parquet('s3://overturemaps-us-west-2/release/2026-09-23.1/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
            WHERE bbox.xmin > -2.20 AND bbox.xmax < -2.05
              AND bbox.ymin > 47.28 AND bbox.ymax < 47.35
        ) TO '../data/processed/infrastructures_donges.parquet' (FORMAT PARQUET);
    """)
    
    print("[2/2] Analyse de vulnérabilité climatique (Jointure Spatiale)...")
    con.execute("""
        COPY (
            SELECT DISTINCT b.id, b.nom, b.geom
            FROM read_parquet('../data/processed/infrastructures_donges.parquet') AS b
            JOIN st_read('../data/raw/234400034_tri-territoires-a-risque-important-dinondation-en-pays-de-la-loire.geojson') AS s
              ON ST_Intersects(b.geom, ST_SetCRS(s.geom, 'OGC:CRS84'))
        ) TO '../data/processed/batiments_menaces.parquet' (FORMAT PARQUET);
    """)
    print("Pipeline terminé avec succès.")

if __name__ == "__main__":
    con = setup_duckdb()
    run_geoint_pipeline(con)