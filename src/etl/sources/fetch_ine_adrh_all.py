# src/etl/sources/fetch_ine_adrh_all.py
from __future__ import annotations
from pathlib import Path
import requests, pandas as pd, sys, time, unicodedata

# Añadir src al path para imports absolutos
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes, read_csv_auto_from_bytes

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
except AttributeError:
    pass

# Tabla correcta para MUNICIPIOS (ADRH): 31277
API_JSON = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/31277?tip=AM"
CSV_SC   = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/31277.csv"  # ; separado
CSV_TSV  = "https://www.ine.es/jaxiT3/files/t/csv_bd/31277.csv"    # \t separado

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data_raw" / "ine"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_RAW = OUT_DIR / "adrh_all_raw.csv"
OUT     = OUT_DIR / "adrh_all.csv"

def norm_txt(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).strip().lower()

def fetch_json(url: str):
    for _ in range(2):
        r = requests.get(url, timeout=180)
        if r.ok:
            return r.json()
        time.sleep(1)
    r.raise_for_status()
    return []

def json_to_df(rows: list[dict]) -> pd.DataFrame:
    recs = []
    for it in rows:
        meta = {d["Nombre"]: (d.get("NombreDetalle") or d.get("Codigo")) for d in it.get("MetaData", [])}
        muni = meta.get("Municipios")
        indic= meta.get("Indicadores de renta media y mediana")
        for d in it.get("Data", []):
            recs.append({
                "municipio": muni,
                "indicador": indic,
                "periodo": d.get("Fecha"),
                "valor": d.get("Valor"),
            })
    return pd.DataFrame.from_records(recs)

def read_csv_auto(url: str) -> pd.DataFrame:
    try:
        return pd.read_csv(url, sep=";", dtype=str, encoding="utf-8")
    except Exception:
        return pd.read_csv(url, sep="\t", dtype=str, encoding="utf-8")

def main():
    print(f"⬇️ ADRH (municipios, JSON) → {API_JSON}")
    try:
        js = fetch_json(API_JSON)
        df = json_to_df(js)
        if df.empty:
            raise RuntimeError("JSON vacío; pruebo CSV")
    except Exception as e:
        print(f"⚠️ JSON falló ({e}); pruebo CSVs…")
        try:
            df = read_csv_auto(CSV_SC)
        except Exception:
            df = read_csv_auto(CSV_TSV)

        # Normaliza CSV -> columnas esperadas
        cols = {norm_txt(c): c for c in df.columns}
        c_muni = next((cols[k] for k in cols if k.startswith("municipios")), None)
        c_ind  = next((cols[k] for k in cols if k.startswith("indicadores de renta")), None)
        c_per  = next((cols[k] for k in cols if "periodo" in k), None)
        c_val  = next((cols[k] for k in ("total","valor","values","value") if k in cols), None)
        if not all([c_muni, c_ind, c_per, c_val]):
            raise RuntimeError(f"No encuentro columnas clave en ADRH CSV. Columnas: {list(df.columns)}")
        df = df.rename(columns={c_muni:"municipio", c_ind:"indicador", c_per:"periodo", c_val:"valor"})

    # Filtra el indicador que quieres (renta neta media por persona, por ejemplo)
    target = "renta neta media por persona"
    mask = df["indicador"].str.strip().str.lower().eq(target)
    if not mask.any():
        # si no está, no filtramos; te quedas con todos los indicadores
        print("ℹ️ No encontré el indicador 'Renta neta media por persona'; guardo todos los indicadores.")
        out = df.copy()
    else:
        out = df[mask].copy()

    # Limpieza de valor
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")
    out = out.dropna(subset=["valor"])
    out.to_csv(OUT_RAW, index=False)
    print(f"🧾 RAW ADRH: {OUT_RAW} ({len(out):,} filas)")

    # Quedarnos en forma (municipio, periodo, valor) solamente para ese indicador
    out_simple = out[["municipio","periodo","valor"]].copy()
    out_simple.to_csv(OUT, index=False)
    print(f"✅ ADRH (municipio×periodo): {OUT} ({len(out_simple):,} filas)")

if __name__ == "__main__":
    main()
