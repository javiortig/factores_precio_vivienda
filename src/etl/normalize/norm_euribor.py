# src/etl/normalize/norm_euribor.py
from pathlib import Path
import pandas as pd
import re

RAW = Path("data_raw/macro/ti_1_7.csv")
OUT = Path("data/curated/euribor_q.parquet")
OUT.parent.mkdir(parents=True, exist_ok=True)

def _read_with_fallback(csv_path: Path) -> pd.DataFrame:
    for kw in [{}, {"sep":";"}, {"encoding":"latin-1"}]:
        try:
            df = pd.read_csv(csv_path, **kw)
            if df.shape[1] > 1: return df
        except Exception:
            pass
    # último intento: a pelo
    return pd.read_csv(csv_path)

def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Falta {RAW}. Ejecuta primero el fetcher del BdE.")
    df = _read_with_fallback(RAW)

    # Detecta columnas
    cols = {c.lower(): c for c in df.columns}
    date_col = cols.get("fecha") or next((c for c in df.columns if re.match(r"(?i)fecha", c)), df.columns[0])
    eur_cols = [c for c in df.columns if re.search(r"(?i)eur[ií]bor.*12", c)]
    if not eur_cols:
        raise RuntimeError("No encuentro una columna 'Euríbor 12 meses' en el CSV del BdE.")
    eur_col = eur_cols[0]

    ser = df[[date_col, eur_col]].rename(columns={date_col:"fecha", eur_col:"euribor_12m"}).copy()
    ser["fecha"] = pd.to_datetime(ser["fecha"], errors="coerce")
    ser = ser.dropna(subset=["fecha"])
    ser["euribor_12m"] = pd.to_numeric(ser["euribor_12m"].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    # Mensual -> Trimestral (promedio)
    ser["date_m"] = ser["fecha"].dt.to_period("M")
    eur_q = ser.groupby(ser["date_m"].dt.to_period("Q"), as_index=False)["euribor_12m"].mean()
    eur_q = eur_q.rename(columns={"date_m":"date"})
    eur_q["date"] = eur_q["date"].astype(str)  # 'YYYY-Qn'

    eur_q.to_parquet(OUT, index=False)
    print(f"✅ {OUT}")

if __name__ == "__main__":
    main()
