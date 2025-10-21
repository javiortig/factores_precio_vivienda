from __future__ import annotations
import pandas as pd

def project_muni_to_h3(muni_series: pd.DataFrame, coverage: pd.DataFrame, weights: pd.DataFrame|None=None) -> pd.DataFrame:
    # muni_series: municipio_id, municipio, date(Period[Q]), price_eur_m2
    # coverage:    h3, municipio_id
    ms = muni_series.copy()
    ms["municipio_id"] = ms["municipio_id"].astype(str)
    cov = coverage[["h3","municipio_id"]].copy()
    cov["municipio_id"] = cov["municipio_id"].astype(str)

    if weights is not None:
        w = weights[["h3","municipio_id","weight"]].copy()
        w["municipio_id"] = w["municipio_id"].astype(str)
        df = ms.merge(w, on="municipio_id", how="left").dropna(subset=["h3"])
        df["price_eur_m2"] = df["price_eur_m2"] * df["weight"]
        out = df.groupby(["h3","date"], as_index=False)["price_eur_m2"].sum()
        return out

    # herencia simple
    df = ms.merge(cov, on="municipio_id", how="left").dropna(subset=["h3"])
    return df[["h3","date","price_eur_m2"]].copy()
