# src/etl/normalize/norm_mivau_valor_tasado.py
from pathlib import Path
import pandas as pd

RAW = Path("data_raw/mivau/valor_tasado_seed.csv")
OUT = Path("data/curated/valor_tasado.parquet")
OUT.parent.mkdir(parents=True, exist_ok=True)

def _read(csv_path: Path) -> pd.DataFrame:
    # Intento con ; y luego con ,
    try:
        return pd.read_csv(csv_path, sep=";", dtype=str)
    except Exception:
        return pd.read_csv(csv_path, dtype=str)

def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Falta {RAW}. Ejecuta primero el fetcher de MIVAU seed.")
    df = _read(RAW).rename(columns={
        "codigo_municipio":"municipio_id",
        "municipio":"municipio",
        "periodo":"date",
        "valor_tasado_vivienda_libre":"price_eur_m2",
        "numero_tasaciones":"tasaciones"
    })
    # Normaliza tipos
    df["municipio_id"] = df["municipio_id"].astype(str)
    df["date"] = df["date"].astype(str).str.replace("T","Q", regex=False)
    df["price_eur_m2"] = pd.to_numeric(df["price_eur_m2"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    if "tasaciones" in df.columns:
        df["tasaciones"] = pd.to_numeric(df["tasaciones"].astype(str).str.replace(".","", regex=False), errors="coerce")

    # Mantén solo columnas clave
    cols = ["municipio_id","municipio","date","price_eur_m2"]
    if "tasaciones" in df.columns: cols.append("tasaciones")
    df[cols].to_parquet(OUT, index=False)
    print(f"✅ {OUT}")

if __name__ == "__main__":
    main()
