from __future__ import annotations
import pandas as pd

def read_euribor_to_quarter(csv_path: str) -> pd.DataFrame:
    # Espera: 'date' (YYYY-MM o YYYY-Qn), 'euribor_12m' (float)
    df = pd.read_csv(csv_path)
    if "date" not in df.columns or "euribor_12m" not in df.columns:
        raise ValueError("El CSV de Euríbor debe tener columnas 'date' y 'euribor_12m'")
    if df["date"].astype(str).str.contains("Q").any():
        df["date"] = pd.PeriodIndex(df["date"].astype(str), freq="Q")
        return df.groupby("date", as_index=False)["euribor_12m"].mean()
    # mensual -> trimestral
    dt = pd.to_datetime(df["date"].astype(str) + "-01", errors="coerce")
    df["date"] = dt.dt.to_period("Q")
    return df.groupby("date", as_index=False)["euribor_12m"].mean()
