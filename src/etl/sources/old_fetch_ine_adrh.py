# src/etl/sources/fetch_ine_adrh.py
from pathlib import Path
import pandas as pd, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

def main():
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "data_raw" / "ine"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "adrh_31142.csv"

    url = "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/31142.csv"
    print(f"⬇️ Descargando ADRH CSV -> {out}")
    df = pd.read_csv(url, sep=";", dtype=str)

    # columna de valor puede haberse renombrado
    val_col = None
    for c in ["valor", "Total", "total"]:
        if c in df.columns:
            val_col = c
            break
    if val_col is None:
        raise RuntimeError(f"No encuentro columna de valor. Disponibles: {list(df.columns)}")

    df = df.rename(columns={val_col: "valor"})
    df.to_csv(out, index=False)
    print(f"✅ Guardado: {out}")

if __name__ == "__main__":
    main()
