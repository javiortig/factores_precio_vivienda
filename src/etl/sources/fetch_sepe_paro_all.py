# src/etl/sources/fetch_sepe_paro_all.py
from pathlib import Path
import pandas as pd, requests, io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

def download_year(year: int, base="https://sede.sepe.gob.es/es/portaltrabaja/resources/sede/datos_abiertos/datos"):
    url = f"{base}/Paro_por_municipios_{year}_csv.csv"
    print(f"⬇️ {year} -> {url}")
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        print(f"⚠️ {year}: {r.status_code}")
        return None

    raw = r.content.decode("latin-1", errors="ignore").splitlines()
    # Buscar la línea donde empieza la cabecera real
    start_idx = next((i for i, l in enumerate(raw) if "PARO REGISTRADO" in l.upper()), None)
    if start_idx is None:
        print(f"⚠️ {year}: No se encontró cabecera válida")
        return None

    df = pd.read_csv(io.StringIO("\n".join(raw[start_idx + 1 :])), sep=";", dtype=str)
    # Detectar y renombrar columnas relevantes
    col_muni = next((c for c in df.columns if "MUNICIPIO" in c.upper()), None)
    if not col_muni:
        print(f"⚠️ {year}: No encuentro columna de municipio. Disponibles: {list(df.columns)}")
        return None

    df = df.rename(columns={col_muni: "municipio"})
    df["year"] = year
    return df

def main():
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "data_raw" / "sepe"
    out_dir.mkdir(parents=True, exist_ok=True)
    dfs = []
    for y in range(2006, 2026):
        d = download_year(y)
        if d is not None:
            dfs.append(d)
    if not dfs:
        print("❌ No se consolidó ningún CSV de SEPE")
        return
    all_df = pd.concat(dfs, ignore_index=True)
    out = out_dir / "paro_municipal_raw.csv"
    all_df.to_csv(out, index=False)
    print(f"✅ Consolidado -> {out}")

if __name__ == "__main__":
    main()
