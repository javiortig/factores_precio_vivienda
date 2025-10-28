import pandas as pd, geopandas as gpd
from pathlib import Path
import numpy as np
Path("data/curated").mkdir(exist_ok=True, parents=True)

# 1) Geometría municipal
g = gpd.read_file("data_raw/geo/municipios_ign.geojson")  # municipio_id, municipio, geometry
g["municipio_norm"] = g["municipio"].str.upper().str.normalize("NFKD").str.encode("ascii","ignore").str.decode("ascii")

# 2) Precio (valor tasado)
vt = pd.read_csv("data_raw/mivau/valor_tasado_seed.csv", dtype=str)
vt["date"] = vt["date"].str.replace("T","Q")
vt["municipio_id"] = vt["municipio_id"].astype(str)
vt["municipio_norm"] = vt["municipio"].str.upper().str.normalize("NFKD").str.encode("ascii","ignore").str.decode("ascii")
vt["price_eur_m2"] = pd.to_numeric(vt["price_eur_m2"], errors="coerce")
# trimestral -> Period[Q]
vt["date"] = pd.PeriodIndex(vt["date"], freq="Q")

# 3) ADRH (renta) y Padrón (población)
adrh = pd.read_parquet("data/curated/adrh.parquet") if Path("data/curated/adrh.parquet").exists() else pd.DataFrame()
pad  = pd.read_parquet("data/curated/padron.parquet") if Path("data/curated/padron.parquet").exists() else pd.DataFrame()

for df in (adrh, pad):
    if not df.empty:
        df["municipio_norm"] = df["municipio"].str.upper().str.normalize("NFKD").str.encode("ascii","ignore").str.decode("ascii")

# 4) Euríbor trimestral
eur = pd.read_parquet("data/curated/euribor_q.parquet")
eur["date"] = eur["date"].astype(str).str.replace("Q","Q")
eur["date"] = pd.PeriodIndex(eur["date"], freq="Q")

# 5) Master (join por municipio_id cuando haya; si falta, por municipio_norm)
# Mantén sólo los municipios que aparezcan en geometría (para el mapa)
base = vt.merge(g[["municipio_id","municipio_norm"]], on="municipio_id", how="left")
# fallback por nombre si municipio_id faltara
mask = base["municipio_id"].isna() & base["municipio_norm"].notna()
if mask.any():
    base.loc[mask, "municipio_id"] = base[mask].merge(
        g[["municipio_id","municipio_norm"]],
        on="municipio_norm",
        how="left"
    )["municipio_id_y"].values

# Join con renta (anual) y población (anual) vía año=Q.year
def add_annual(df, name, col_value):
    if df.empty: return None
    df2 = df.copy()
    df2["year"] = df2["year"].astype(str).str.extract(r"(\d{4})")
    df2 = df2.rename(columns={col_value: name})
    return df2[["municipio_norm","year", name]]

m_renta = add_annual(adrh, "renta_pc", "renta_pc")
m_pob   = add_annual(pad,  "poblacion", "poblacion")

master = base.copy()
master["year"] = master["date"].dt.year.astype(str)
for extra in [m_renta, m_pob]:
    if extra is not None:
        master = master.merge(extra, on=["municipio_norm","year"], how="left")

# Join euríbor por trimestre
master = master.merge(eur, on="date", how="left")

# Lags para modelo
master = master.sort_values(["municipio_id", "date"])
master["price_lag1"] = master.groupby("municipio_id")["price_eur_m2"].shift(1)
master["price_yoy"]  = master.groupby("municipio_id")["price_eur_m2"].pct_change(4)

# Salidas
master.to_parquet("data/curated/municipios_master.parquet", index=False)
g.to_file("data/curated/municipios_geo.geojson", driver="GeoJSON")
print("✅ data/curated/municipios_master.parquet")
print("✅ data/curated/municipios_geo.geojson")
