from __future__ import annotations

import pandas as pd
from pathlib import Path

def read_municipal_series(csv_path: str | Path) -> pd.DataFrame:
    """Lee series municipales en formato mínimo:
    columnas: municipio_id, municipio, date (YYYY-Qn), price_eur_m2
    Devuelve DataFrame normalizado con columnas: municipio_id, municipio, date, price_eur_m2
    """
    df = pd.read_csv(csv_path)
    expected = {"municipio_id", "municipio", "date", "price_eur_m2"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en {csv_path}: {missing}")
    # Normaliza tipos
    df["municipio_id"] = df["municipio_id"].astype(str)
    df["municipio"] = df["municipio"].astype(str)
    # convierte date tipo periodo trimestral
    df["quarter"] = pd.PeriodIndex(df["date"], freq="Q")
    df = df.drop(columns=["date"]).rename(columns={"quarter": "date"})
    df = df.sort_values(["municipio_id", "date"]).reset_index(drop=True)
    return df

def to_quarter_end(dt: pd.Period) -> pd.Timestamp:
    return dt.asfreq("Q").to_timestamp(how="end")

def ensure_quarterly_complete(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura que cada municipio tiene una serie trimestral completa (relleno por ffill si hay gaps)."""
    out = []
    for mid, g in df.groupby("municipio_id", sort=False):
        idx = pd.period_range(g["date"].min(), g["date"].max(), freq="Q")
        g2 = g.set_index("date").reindex(idx)
        g2["municipio_id"] = mid
        g2["municipio"] = g["municipio"].iloc[0]
        g2["price_eur_m2"] = g2["price_eur_m2"].ffill()
        g2 = g2.reset_index().rename(columns={"index": "date"})
        out.append(g2)
    return pd.concat(out, ignore_index=True)
