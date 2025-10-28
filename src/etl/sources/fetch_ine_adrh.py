import os, pandas as pd, requests
from pathlib import Path

RAW = Path("data_raw/ine"); RAW.mkdir(parents=True, exist_ok=True)
CUR = Path("data/curated"); CUR.mkdir(parents=True, exist_ok=True)

# INE JAXI T3 (tabla ADRH municipal) — CSV con ';'
# Verificado en datos.gob: /jaxiT3/files/t/csv_bdsc/31142.csv
# Doc/tabla HTML: https://www.ine.es/jaxiT3/Tabla.htm?t=31142
URL = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/31142.csv"

raw_csv = RAW / "adrh_31142.csv"
print(f"⬇️ Descargando ADRH CSV -> {raw_csv}")
r = requests.get(URL, timeout=60); r.raise_for_status()
raw_csv.write_bytes(r.content)

df = pd.read_csv(raw_csv, sep=';', dtype=str)
# Columnas típicas (pueden variar mínimamente en tildes/espacios)
# Buscamos: Unidades territoriales (municipio), Indicador, Periodo, Valor
cols = {c.lower(): c for c in df.columns}
def pick(cands):
    for k in cands:
        if k in cols: return cols[k]
    raise RuntimeError(f"No encuentro columnas {cands}. Disponibles: {list(df.columns)}")

c_geo = pick(["unidades territoriales","municipios","municipio"])
c_ind = pick(["indicadores de renta media y mediana","indicador"])
c_per = pick(["periodo"])
c_val = pick(["valor"])

out = df.rename(columns={
    c_geo: "municipio",
    c_ind: "indicador",
    c_per: "year",
    c_val: "renta_val"
})[["municipio","indicador","year","renta_val"]].copy()

# Nos quedamos con un indicador base para el modelo (puedes ampliar luego):
# "Renta neta media por persona"
mask = out["indicador"].str.contains("Renta neta media por persona", case=False, na=False)
out = out[mask].copy()
out["year"] = out["year"].astype(str).str.extract(r"(\d{4})")
out["renta_pc"] = pd.to_numeric(out["renta_val"].str.replace(",", "."), errors="coerce")
out = out.drop(columns=["indicador","renta_val"]).dropna(subset=["renta_pc"])

out.to_parquet(CUR / "adrh.parquet", index=False)
print(f"✅ Guardado ADRH normalizado -> {CUR/'adrh.parquet'}")
