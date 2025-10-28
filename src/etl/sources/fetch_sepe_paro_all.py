import os, re, pandas as pd, requests
from pathlib import Path
from datetime import date

RAW = Path("data_raw/sepe"); RAW.mkdir(parents=True, exist_ok=True)
CUR = Path("data/curated"); CUR.mkdir(parents=True, exist_ok=True)

BASE = "https://sede.sepe.gob.es/es/portaltrabaja/resources/sede/datos_abiertos/datos"
# Patrón más común observado (ejemplos oficiales):
# Paro_por_municipios_2025_csv.csv, Paro_por_municipios_2023_csv.csv, etc.  (y "Contratos_por_municipios_YYYY_csv.csv")
# Ver catálogo SEPE y ejemplos. 
# NOTE: el SEPE ha ido publicando por años/semestres; este fetcher apunta a los CSV anuales principales. Ajusta el rango si necesitas histórico más profundo.

def try_urls(year: int):
    # Probar variantes conocidas de nombre (por seguridad)
    return [
        f"{BASE}/Paro_por_municipios_{year}_csv.csv",
        f"{BASE}/Paro_por_municipios_{year}.csv",
        f"{BASE}/paro_por_municipios_{year}_csv.csv",
    ]

def download_year(y: int):
    for url in try_urls(y):
        try:
            r = requests.get(url, timeout=60)
            if r.ok and r.content and len(r.content) > 1000:
                out = RAW / f"paro_{y}.csv"
                out.write_bytes(r.content)
                print(f"✅ {y} -> {url}")
                return out
        except requests.RequestException:
            pass
    print(f"⚠️ No disponible {y}")
    return None

start, end = 2006, date.today().year  # ampliar si hace falta
files = [download_year(y) for y in range(start, end+1)]
files = [f for f in files if f]

# Normalización básica y concatenación
dfs = []
for f in files:
    try:
        df = pd.read_csv(f, sep=';', dtype=str, encoding="latin-1", low_memory=False)
        # Columnas típicas (pueden variar algo por año): COD_MUNICIPIO, MUNICIPIO, PERIODO o MES/AÑO, PARADOS_TOT, HOMBRES/MUJERES/SECTORES...
        cols = {c.lower(): c for c in df.columns}
        def pick(cands, optional=False):
            for k in cands:
                if k in cols: return cols[k]
            if optional: return None
            raise RuntimeError(f"{f.name}: faltan columnas {cands}. Disponibles: {list(df.columns)}")

        c_muni_id = pick(["c_municipio","cod_municipio","codigo municipio","cod municipio","codigo_municipio","id_municipio"])
        c_muni    = pick(["municipio","nombre_municipio","nombremunicipio"])
        # periodo puede venir como "mes" + "año" o "periodo" tipo "2025/01"
        c_year    = cols.get("año") or cols.get("anio") or None
        c_month   = cols.get("mes") or None
        c_period  = cols.get("periodo") or None
        c_total   = pick(["total parados","parados totales","parados_total","total"], optional=True)

        df2 = df.rename(columns={
            c_muni_id: "municipio_id",
            c_muni: "municipio"
        })
        # construir date (mensual) como YYYY-MM
        if c_period and df2[c_period].str.contains(r"\d{4}[-/]\d{1,2}", na=False).any():
            per = df2[c_period].str.replace("/", "-", regex=False)
            y = per.str.extract(r"(\d{4})"); m = per.str.extract(r"(?:\d{4}[-/])(\d{1,2})")
        else:
            y = df2[c_year] if c_year in df2.columns else None
            m = df2[c_month] if c_month in df2.columns else None
        df2["date_m"] = None
        if y is not None and m is not None:
            df2["date_m"] = (y.astype(str) + "-" + m.astype(str).str.zfill(2))
        elif y is not None:
            # algunos ficheros anuales sin mes concreto: usa diciembre
            df2["date_m"] = y.astype(str) + "-12"

        if c_total and c_total in df2.columns:
            df2["paro_total"] = pd.to_numeric(df2[c_total].str.replace(".","", regex=False), errors="coerce")
        else:
            # si no hay total explícito, intenta sumar columnas hombre/mujer si existen
            c_h = cols.get("hombres"); c_m = cols.get("mujeres")
            if c_h in df2.columns and c_m in df2.columns:
                df2["paro_total"] = pd.to_numeric(df2[c_h].str.replace(".","", regex=False), errors="coerce") + \
                                    pd.to_numeric(df2[c_m].str.replace(".","", regex=False), errors="coerce")
            else:
                df2["paro_total"] = pd.NA

        dfs.append(df2[["municipio_id","municipio","date_m","paro_total"]])
    except Exception as e:
        print(f"⚠️ {f.name}: {e}")

if dfs:
    allp = pd.concat(dfs, ignore_index=True).drop_duplicates()
    # limpia ids y fechas
    allp["municipio_id"] = allp["municipio_id"].astype(str).str.strip()
    allp["date_m"] = pd.to_datetime(allp["date_m"], errors="coerce").dt.to_period("M").astype(str)
    allp.to_parquet(CUR / "sepe_paro_muni.parquet", index=False)
    print(f"✅ Guardado paro municipal -> {CUR/'sepe_paro_muni.parquet'}")
else:
    print("❌ No se pudo consolidar ningún CSV de SEPE (revisa el catálogo o nombres de archivo).")
