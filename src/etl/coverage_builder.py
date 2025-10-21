from __future__ import annotations
import pandas as pd
from .h3_utils import cell_from_latlon, neighbors_disk

def build_h3_coverage_from_centroids(centroids_df: pd.DataFrame, resolution: int, radius: int) -> pd.DataFrame:
    req = {"municipio_id","municipio","lat","lon"}
    miss = req - set(centroids_df.columns)
    if miss: raise ValueError(f"Faltan columnas en centroides: {miss}")
    rows = []
    for _, r in centroids_df.iterrows():
        h = cell_from_latlon(float(r["lat"]), float(r["lon"]), resolution)
        cells = {h}
        for k in range(1, int(radius)+1):
            cells |= set(neighbors_disk(h, k))
        for c in cells:
            rows.append({"h3": c, "municipio_id": str(r["municipio_id"]), "municipio": r["municipio"]})
    return pd.DataFrame(rows).drop_duplicates("h3")
