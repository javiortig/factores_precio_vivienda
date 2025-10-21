from __future__ import annotations
import pandas as pd

def read_mitma_municipal(csv_path: str) -> pd.DataFrame:
    # Espera columnas: municipio_id, municipio, date(YYYY-Qn), price_eur_m2
    df = pd.read_csv(csv_path)
    req = {"municipio_id","municipio","date","price_eur_m2"}
    miss = req - set(df.columns)
    if miss: raise ValueError(f"Faltan columnas en {csv_path}: {miss}")
    df["municipio_id"] = df["municipio_id"].astype(str)
    df["municipio"] = df["municipio"].astype(str)
    df["date"] = pd.PeriodIndex(df["date"].astype(str), freq="Q")
    df = df.sort_values(["municipio_id","date"]).reset_index(drop=True)

    # Completar gaps por municipio con ffill
    out = []
    for mid, g in df.groupby("municipio_id", sort=False):
        idx = pd.period_range(g["date"].min(), g["date"].max(), freq="Q")
        g2 = g.set_index("date").reindex(idx)
        g2["municipio_id"] = mid
        g2["municipio"] = g["municipio"].iloc[0]
        g2["price_eur_m2"] = g2["price_eur_m2"].ffill()
        out.append(g2.reset_index().rename(columns={"index":"date"}))
    return pd.concat(out, ignore_index=True)
