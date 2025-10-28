# src/etl/normalize/norm_geo_municipios.py
from pathlib import Path
import geopandas as gpd
import re

RAW = Path("data_raw/geo/municipios_ign.geojson")
OUT = Path("data/curated/geo_municipios.geojson")
OUT.parent.mkdir(parents=True, exist_ok=True)

def norm_id(x: str) -> str:
    """Intenta extraer el código INE (5 dígitos) del LAU/ID que venga."""
    s = str(x)
    m = re.search(r"(\d{5})$", s)
    return m.group(1) if m else s

def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Falta {RAW}. Ejecuta primero el fetcher de IGN.")
    g = gpd.read_file(RAW)

    # Intenta mapear a columnas estándar
    cols = {c.lower(): c for c in g.columns}
    id_col = None
    name_col = None
    for k in ["municipio_id","lau_code","localid","inspireid","natcode","codigoine","cod_ine","codine"]:
        if k in cols: id_col = cols[k]; break
    for k in ["municipio","name","officialname","nameunit","lau_name"]:
        if k in cols: name_col = cols[k]; break
    if id_col is None:
        # como fallback, crea un id estable desde el orden
        g["municipio_id"] = g.index.astype(str)
        id_col = "municipio_id"
    if name_col is None and "municipio" not in g.columns:
        # si no hay nombre, crea uno vacío
        g["municipio"] = ""
        name_col = "municipio"
    elif name_col != "municipio":
        g = g.rename(columns={name_col: "municipio"})

    # Normaliza id
    g["municipio_id"] = g[id_col].astype(str).apply(norm_id)

    # Salida
    g[["municipio_id","municipio","geometry"]].to_file(OUT, driver="GeoJSON")
    print(f"✅ {OUT}")

if __name__ == "__main__":
    main()
