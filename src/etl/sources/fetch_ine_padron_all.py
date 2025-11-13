# src/etl/sources/fetch_ine_padron_all.py
from __future__ import annotations
from pathlib import Path
import requests, pandas as pd, sys, unicodedata, time

sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

# INE Tempus API: Padrón por sexo, municipios y edad (año a año)
# Tabla: 33775  -> JSON completo con tip=AM (toda la matriz)
API = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775?tip=AM"
CSV_FALLBACK = "https://www.ine.es/jaxiT3/files/t/csv_bd/33775.csv"  # TSV alternativo
ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data_raw" / "ine"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "padron_33775.json"
OUT_RAW = OUT_DIR / "padron_all_raw.csv"       # versión “ancha” sin agregar (para auditoría)
OUT_AGG = OUT_DIR / "padron_all.csv"           # agregado Municipio×Periodo (población total)

def norm_txt(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).strip().lower()

def fetch_json(url: str, retries: int = 3, sleep=2) -> list[dict]:
    for i in range(retries):
        r = requests.get(url, timeout=180)
        if r.ok:
            return r.json()
        time.sleep(sleep)
    r.raise_for_status()
    return []

def json_to_df(rows: list[dict]) -> pd.DataFrame:
    # Estructura Tempus: cada item tiene 'Cod' y 'Nombre' por dimensión y 'Data' con pares {Fecha, Valor}
    # Detectamos dimensiones por nombre
    # Suelen venir: Sexo, Provincias, Municipios, Edad (año a año)
    recs = []
    for it in rows:
        dims = {d["Nombre"]: d["Codigo"] for d in it.get("MetaData", [])}
        municipio = dims.get("Municipios")
        provincia = dims.get("Provincias")
        sexo      = dims.get("Sexo")
        edad      = dims.get("Edad (año a año)")
        for d in it.get("Data", []):
            recs.append({
                "provincia": provincia,
                "municipio": municipio,
                "sexo": sexo,
                "edad": edad,
                "periodo": d.get("Fecha"),
                "valor": d.get("Valor"),
            })
    return pd.DataFrame.from_records(recs)

def main():
    print(f"⬇️ Padrón (JSON, nacional) → {API}")
    try:
        data = fetch_json(API)
        OUT_JSON.write_text("[]", encoding="utf-8")
        # guardo el JSON crudo por si quieres inspeccionarlo (para ahorrar espacio, lo omito)
        # OUT_JSON.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        df = json_to_df(data)
        if df.empty:
            raise RuntimeError("La API JSON devolvió 0 filas; intentaré TSV de fallback.")
        # Guardamos RAW “ancho”
        df.to_csv(OUT_RAW, index=False)
        print(f"🧾 RAW (no agregado): {OUT_RAW} ({len(df):,} filas)")
    except Exception as e:
        print(f"⚠️ API JSON falló ({e}). Pruebo CSV TSV fallback…")
        # TSV: columnas con “Municipios/Provincias/Sexo/Edad…/Periodo/Total”
        df = pd.read_csv(CSV_FALLBACK, sep="\t", dtype=str, encoding="utf-8")
        df.to_csv(OUT_RAW, index=False)
        print(f"🧾 RAW TSV: {OUT_RAW} ({len(df):,} filas)")

    # Agregamos a “Municipio × Periodo” sumando todo (sexo/edades)
    cols = {norm_txt(c): c for c in df.columns}
    c_muni = next((cols[k] for k in cols if k.startswith("municipios")), None)
    c_per  = next((cols[k] for k in cols if "periodo" in k), None)
    c_val  = next((cols[k] for k in ("total","valor","values","value") if k in cols), None)
    if not all([c_muni, c_per, c_val]):
        raise RuntimeError(f"No encuentro columnas clave en Padrón. Columnas: {list(df.columns)}")

    g = (df[[c_muni, c_per, c_val]]
         .rename(columns={c_muni:"municipio", c_per:"periodo", c_val:"valor"})
         .copy())
    g["valor"] = pd.to_numeric(g["valor"], errors="coerce")
    out = (g.dropna(subset=["valor"])
             .groupby(["municipio","periodo"], as_index=False)["valor"].sum())
    out.to_csv(OUT_AGG, index=False)
    print(f"✅ Guardado agregado Municipio×Periodo: {OUT_AGG} ({len(out):,} filas)")

if __name__ == "__main__":
    main()
