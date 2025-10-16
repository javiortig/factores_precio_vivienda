from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

try:
    import h3
except Exception as e:
    h3 = None

@dataclass
class MunicipalityCenter:
    municipio_id: str
    municipio: str
    lat: float
    lon: float
    radius: int  # k-ring radius at given resolution

# Demo centers (puedes reemplazar por tus municipios reales)
DEMO_CENTERS: List[MunicipalityCenter] = [
    MunicipalityCenter("28079", "Madrid", 40.4168, -3.7038, 14),
    MunicipalityCenter("08019", "Barcelona", 41.3874, 2.1686, 12),
    MunicipalityCenter("46250", "Valencia", 39.4699, -0.3763, 11),
    MunicipalityCenter("41091", "Sevilla", 37.3891, -5.9845, 11),
]

def krings_for_centers(centers: List[MunicipalityCenter], resolution: int) -> pd.DataFrame:
    if h3 is None:
        raise RuntimeError("La librería h3 no está instalada. Ejecuta: pip install h3")
    rows = []
    for c in centers:
        h = h3.geo_to_h3(c.lat, c.lon, resolution)
        cells = set([h])
        for k in range(1, c.radius + 1):
            cells |= set(h3.k_ring(h, k))
        for cell in cells:
            rows.append({"h3": cell, "municipio_id": c.municipio_id, "municipio": c.municipio})
    df = pd.DataFrame(rows).drop_duplicates("h3")
    return df

def demo_coverage(resolution: int) -> pd.DataFrame:
    return krings_for_centers(DEMO_CENTERS, resolution)
