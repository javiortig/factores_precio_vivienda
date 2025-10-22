import geopandas as gpd
import pandas as pd
from pathlib import Path

# --- RUTAS: añade aquí tus shapefiles de MUNICIPIOS (polígonos) ---
shps = [
    "data_raw/geo/recintos_municipales_inspire_peninbal_etrs89.shp",
    # "data_raw/geo/recintos_municipales_inspire_canarias_etrs89.shp",  # opcional si lo tienes
]

# 1) Lee y concatena (soporta que vengan en ETRS89; convertimos a WGS84)
gdfs = [gpd.read_file(s) for s in shps]
g = pd.concat(gdfs, ignore_index=True)
if g.crs is None:
    raise RuntimeError("El shapefile no tiene CRS definido; asígnalo antes de transformar.")
g = g.to_crs(4326)

# 2) Detecta columnas de ID/nombre típicas (ajusta si difiere en tu fichero)
cols_lower = {c.lower(): c for c in g.columns}
id_candidates = ["cod_ine","codigoine","codine","ine_muni","codmun","codmuni"]
name_candidates = ["nombre","nombre_ofi","namemun","municipio","muni"]

def pick(cands):
    for k in cands:
        if k in cols_lower: return cols_lower[k]
    raise RuntimeError(f"No encuentro columnas esperadas. Columnas disponibles: {list(g.columns)}")

id_col = pick(id_candidates)
name_col = pick(name_candidates)

# 3) Punto representativo dentro del polígono (mejor que centroid para polígonos raros)
pts = g.geometry.representative_point()
out = g.assign(lat=pts.y, lon=pts.x)[[id_col, name_col, "lat", "lon"]]
out = out.rename(columns={id_col: "municipio_id", name_col: "municipio"})

# (opcional) si tus códigos INE son numéricos de 5 dígitos:
out["municipio_id"] = out["municipio_id"].astype(str)  # .str.zfill(5) si procede

# 4) Exporta al CSV que usa el ETL
Path("data_raw").mkdir(parents=True, exist_ok=True)
out.to_csv("data_raw/municipios_centroids.csv", index=False)
print("OK -> data_raw/municipios_centroids.csv")
