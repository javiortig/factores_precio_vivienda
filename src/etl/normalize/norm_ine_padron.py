# src/etl/normalize/norm_ine_padron.py
from pathlib import Path
import pandas as pd

RAW = Path("data_raw/ine/padron_33775.csv")
OUT = Path("data/curated/padron.parquet")
OUT.parent.mkdir(parents=True, exist_ok=True)

def pick(cols_map, cands):
    for k in cands:
        if k in cols_map: return cols_map[k]
    raise RuntimeError(f"Faltan columnas {cands}.")

def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Falta {RAW}. Ejecuta el fetcher de Padrón.")
    df = pd.read_csv(RAW, sep=";", dtype=str, low_memory=False)
    cols = {c.lower(): c for c in df.columns}

    c_sex = pick(cols, ["sexo"])
    c_age = pick(cols, ["edad (año a año)","edad"])
    c_per = pick(cols, ["periodo"])
    c_geo = pick(cols, ["unidades territoriales","municipios","municipio"])
    c_val = pick(cols, ["valor"])

    df = df.rename(columns={c_sex:"sexo", c_age:"edad", c_per:"year", c_geo:"municipio", c_val:"poblacion"})
    f = (df["sexo"].str.contains("Ambos", case=False, na=False)) & (df["edad"].str.contains("Total", case=False, na=False))
    pad = df[f].copy()
    pad["year"] = pad["year"].astype(str).str.extract(r"(\d{4})")
    pad["poblacion"] = pd.to_numeric(
        pad["poblacion"].astype(str).str.replace(".","", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    )
    out = pad[["municipio","year","poblacion"]].dropna(subset=["poblacion"])
    out.to_parquet(OUT, index=False)
    print(f"✅ {OUT}")

if __name__ == "__main__":
    main()
