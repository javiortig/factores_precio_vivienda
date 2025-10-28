# src/etl/normalize/norm_ine_adrh.py
from pathlib import Path
import pandas as pd

RAW = Path("data_raw/ine/adrh_31142.csv")
OUT = Path("data/curated/adrh.parquet")
OUT.parent.mkdir(parents=True, exist_ok=True)

def pick(cols_map, cands):
    for k in cands:
        if k in cols_map: return cols_map[k]
    raise RuntimeError(f"Faltan columnas {cands}.")

def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Falta {RAW}. Ejecuta el fetcher de ADRH.")
    df = pd.read_csv(RAW, sep=";", dtype=str)
    cols = {c.lower(): c for c in df.columns}

    c_geo = pick(cols, ["unidades territoriales","municipios","municipio"])
    c_ind = pick(cols, ["indicadores de renta media y mediana","indicador"])
    c_per = pick(cols, ["periodo"])
    c_val = pick(cols, ["valor"])

    out = df.rename(columns={c_geo:"municipio", c_ind:"indicador", c_per:"year", c_val:"renta_val"})
    mask = out["indicador"].str.contains("Renta neta media por persona", case=False, na=False)
    out = out[mask].copy()
    out["year"] = out["year"].astype(str).str.extract(r"(\d{4})")
    out["renta_pc"] = pd.to_numeric(out["renta_val"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    out = out[["municipio","year","renta_pc"]].dropna(subset=["renta_pc"])

    out.to_parquet(OUT, index=False)
    print(f"✅ {OUT}")

if __name__ == "__main__":
    main()
