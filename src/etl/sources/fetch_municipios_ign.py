import requests, geopandas as gpd
from shapely.geometry import shape
import pandas as pd
from pathlib import Path

BASE = "https://api-features.ign.es/collections/administrativeunit/items"
out = []
url = BASE + "?limit=1000"
while url:
    r = requests.get(url, timeout=60); r.raise_for_status()
    j = r.json()
    for f in j["features"]:
        props = f.get("properties", {})
        # Heurística de nivel municipal
        level = (props.get("level") or props.get("adminLevel") or "").lower()
        is_muni = any(x in level for x in ["municip", "lau", "municipality"])
        if is_muni:
            muni_id = props.get("lauCode") or props.get("localId") or props.get("inspireId")
            name    = props.get("name") or props.get("officialName")
            if muni_id and name:
                out.append({"municipio_id": str(muni_id), "municipio": name, "geometry": shape(f["geometry"])})
    # paginación
    links = {l["rel"]: l["href"] for l in j.get("links", []) if "rel" in l}
    url = links.get("next")

gdf = gpd.GeoDataFrame(out, geometry="geometry", crs=4326)
# Normaliza municipio_id: si viene con formato LAU (ESXXXXXXX), extrae sufijo numérico si lo deseas
def norm_id(x: str) -> str:
    # intenta quedarte con el tramo numérico final de 5 dígitos si existe
    import re
    m = re.search(r"(\d{5})$", x)
    return m.group(1) if m else x
gdf["municipio_id"] = gdf["municipio_id"].astype(str).apply(norm_id)

Path("data_raw/geo").mkdir(parents=True, exist_ok=True)
gdf.to_file("data_raw/geo/municipios_ign.geojson", driver="GeoJSON")
print("✅ data_raw/geo/municipios_ign.geojson")
