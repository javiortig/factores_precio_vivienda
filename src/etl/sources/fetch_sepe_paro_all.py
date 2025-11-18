# src/etl/sources/fetch_sepe_paro_all.py
from pathlib import Path
import pandas as pd, requests, io, sys

# Añadir src al path para imports absolutos
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes, read_csv_auto_from_bytes

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
except AttributeError:
    pass

def download_year(year: int, base="https://sede.sepe.gob.es/es/portaltrabaja/resources/sede/datos_abiertos/datos"):
    url = f"{base}/Paro_por_municipios_{year}_csv.csv"
    print(f"⬇️ {year} -> {url}")
    try:
        b = download_bytes(url, timeout=30)
    except Exception as e:
        print(f"⚠️ {year}: descarga fallida: {e}")
        return None

    # Intentar parsear automáticamente
    try:
        df = read_csv_auto_from_bytes(b)
    except Exception:
        # Intento manual: decodificar latin-1 y buscar la línea con cabecera
        try:
            raw = b.decode("latin-1", errors="ignore").splitlines()
            # Busca la primera línea que contenga 'MUNICIPIO' y que tenga separador ';' o '\t'
            header_idx = None
            for i, l in enumerate(raw[:10]):
                if ("MUNICIPIO" in l.upper() or "PARO" in l.upper()) and (";" in l or "\t" in l or "," in l):
                    header_idx = i
                    break
            if header_idx is None:
                # fallback: try pandas with default
                df = pd.read_csv(io.StringIO("\n".join(raw)), dtype=str, sep=";", engine="python")
            else:
                df = pd.read_csv(io.StringIO("\n".join(raw[header_idx + 0 :])), dtype=str, engine="python")
        except Exception as e:
            print(f"⚠️ {year}: no pude parsear el CSV: {e}")
            return None

    # Detectar y renombrar columnas relevantes
    col_muni = next((c for c in df.columns if "MUNICIPIO" in c.upper() or "CODIGO" in c.upper()), None)
    if not col_muni:
        print(f"⚠️ {year}: No encuentro columna de municipio. Disponibles: {list(df.columns)[:10]}")
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
