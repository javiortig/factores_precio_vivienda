import os, pandas as pd, requests, io
from pathlib import Path

RAW = Path("data_raw/ine"); RAW.mkdir(parents=True, exist_ok=True)
CUR = Path("data/curated"); CUR.mkdir(parents=True, exist_ok=True)

# Usamos la tabla INE con API-ID=33775 (Población por sexo, municipios y edad año a año)
# CSV con ';' y JSON disponibles según metadata.
# Metadata CSV muestra URL CSV ';': .../jaxiT3/files/t/csv_bdsc/33775.csv
CSV_URL = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/33775.csv"

raw_csv = RAW / "padron_33775.csv"
print(f"⬇️ Descargando Padrón CSV -> {raw_csv}")
r = requests.get(CSV_URL, timeout=120); r.raise_for_status()
raw_csv.write_bytes(r.content)

df = pd.read_csv(raw_csv, sep=';', dtype=str)
# Columnas habituales: "Sexo", "Edad (año a año)" o "Edad", "Periodo", "Unidades territoriales"/"Municipios", "Valor"
cols = {c.lower(): c for c in df.columns}
def pick(cands):
    for k in cands:
        if k in cols: return cols[k]
    raise RuntimeError(f"No encuentro columnas {cands}. Disponibles: {list(df.columns)}")

c_sex = pick(["sexo"])
c_age = pick(["edad (año a año)","edad"])
c_per = pick(["periodo"])
c_geo = pick(["unidades territoriales","municipios","municipio"])
c_val = pick(["valor"])

df = df.rename(columns={
    c_sex:"sexo", c_age:"edad", c_per:"year", c_geo:"municipio", c_val:"poblacion"
})

# Filtramos "Ambos sexos" y "Total" para tener población total municipal por año
f = (df["sexo"].str.contains("Ambos", case=False, na=False)) & (df["edad"].str.contains("Total", case=False, na=False))
pad = df[f].copy()
pad["year"] = pad["year"].astype(str).str.extract(r"(\d{4})")
# valor a numérico
pad["poblacion"] = pd.to_numeric(pad["poblacion"].str.replace(".","", regex=False).str.replace(",", "."), errors="coerce")

pad = pad[["municipio","year","poblacion"]].dropna(subset=["poblacion"])
pad.to_parquet(CUR / "padron.parquet", index=False)
print(f"✅ Guardado Padrón normalizado -> {CUR/'padron.parquet'}")
