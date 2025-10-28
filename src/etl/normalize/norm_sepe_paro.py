# src/etl/normalize/norm_sepe_paro.py
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data_raw/sepe")
OUT = Path("data/curated/sepe_paro_muni.parquet")
OUT.parent.mkdir(parents=True, exist_ok=True)

def pick(cols_map, cands, optional=False):
    for k in cands:
        if k in cols_map: return cols_map[k]
    if optional: return None
    raise RuntimeError(f"Faltan columnas {cands}.")

def main():
    files = sorted(RAW_DIR.glob("paro_*.csv"))
    if not files:
        raise FileNotFoundError(f"No hay CSVs en {RAW_DIR}. Ejecuta primero el fetcher de SEPE.")

    dfs = []
    for f in files:
        df = pd.read_csv(f, sep=';', dtype=str, encoding="latin-1", low_memory=False)
        cols = {c.lower(): c for c in df.columns}

        c_muni_id = pick(cols, ["c_municipio","cod_municipio","codigo municipio","cod municipio","codigo_municipio","id_municipio"])
        c_muni    = pick(cols, ["municipio","nombre_municipio","nombremunicipio"])
        c_year    = cols.get("año") or cols.get("anio")
        c_month   = cols.get("mes")
        c_period  = cols.get("periodo")
        c_total   = pick(cols, ["total parados","parados totales","parados_total","total"], optional=True)

        df = df.rename(columns={c_muni_id:"municipio_id", c_muni:"municipio"})

        # Construye fecha mensual
        if c_period and df[c_period].astype(str).str.contains(r"\d{4}[-/]\d{1,2}", na=False).any():
            per = df[c_period].astype(str).str.replace("/", "-", regex=False)
            y = per.str.extract(r"(\d{4})")[0]
            m = per.str.extract(r"(?:\d{4}[-/])(\d{1,2})")[0]
            date_m = y + "-" + m.str.zfill(2)
        else:
            y = df[c_year].astype(str) if c_year in df.columns else None
            m = df[c_month].astype(str) if c_month in df.columns else None
            date_m = (y + "-" + m.str.zfill(2)) if (y is not None and m is not None) else (y + "-12" if y is not None else None)

        df["date_m"] = date_m

        # Paro total
        if c_total and c_total in df.columns:
            df["paro_total"] = pd.to_numeric(df[c_total].str.replace(".","", regex=False), errors="coerce")
        else:
            h, mu = cols.get("hombres"), cols.get("mujeres")
            if h in df.columns and mu in df.columns:
                df["paro_total"] = pd.to_numeric(df[h].str.replace(".","", regex=False), errors="coerce") + \
                                   pd.to_numeric(df[mu].str.replace(".","", regex=False), errors="coerce")
            else:
                df["paro_total"] = pd.NA

        dfs.append(df[["municipio_id","municipio","date_m","paro_total"]])

    allp = (pd.concat(dfs, ignore_index=True)
              .drop_duplicates()
              .assign(date_m=lambda d: pd.PeriodIndex(pd.to_datetime(d["date_m"], errors="coerce"), freq="M").astype(str)))

    allp.to_parquet(OUT, index=False)
    print(f"✅ {OUT}")

if __name__ == "__main__":
    main()
