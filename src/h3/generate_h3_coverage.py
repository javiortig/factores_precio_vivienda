from __future__ import annotations

from dataclasses import dataclass
from typing import List
import pandas as pd
import h3  # Compatible con v3 (geo_to_h3/k_ring) o v4 (latlng_to_cell/grid_disk)


@dataclass
class MunicipalityCenter:
    municipio_id: str
    municipio: str
    lat: float
    lon: float
    radius: int  # radio del k-ring/grid-disk


# --- Ciudades demo (puedes cambiar o ampliar) ---
DEMO_CENTERS: List[MunicipalityCenter] = [
    MunicipalityCenter("28079", "Madrid", 40.4168, -3.7038, 14),
    MunicipalityCenter("08019", "Barcelona", 41.3874, 2.1686, 12),
    MunicipalityCenter("46250", "Valencia", 39.4699, -0.3763, 11),
    MunicipalityCenter("41091", "Sevilla", 37.3891, -5.9845, 11),
]


# --- Compatibilidad entre versiones h3 v3/v4 ---
def _latlng_to_cell(lat: float, lon: float, res: int) -> str:
    """Devuelve el identificador H3 dado un punto (lat, lon)."""
    if hasattr(h3, "geo_to_h3"):  # v3
        return h3.geo_to_h3(lat, lon, res)
    elif hasattr(h3, "latlng_to_cell"):  # v4
        return h3.latlng_to_cell(lat, lon, res)
    raise RuntimeError("API de h3 no reconocida: no se encontró geo_to_h3 ni latlng_to_cell")


def _disk(origin: str, k: int):
    """Devuelve un conjunto de celdas vecinas (k-ring o grid_disk)."""
    if hasattr(h3, "k_ring"):  # v3
        return h3.k_ring(origin, k)
    elif hasattr(h3, "grid_disk"):  # v4
        # En v4 devuelve lista de listas → aplanamos
        cells = h3.grid_disk(origin, k)
        if isinstance(cells, list) and isinstance(cells[0], list):
            return {c for sublist in cells for c in sublist}
        return set(cells)
    raise RuntimeError("API de h3 no reconocida: no se encontró k_ring ni grid_disk")


# --- Generación de cobertura ---
def krings_for_centers(centers: List[MunicipalityCenter], resolution: int) -> pd.DataFrame:
    """Genera un DataFrame con todos los hexágonos H3 que cubren los municipios demo."""
    rows = []
    for c in centers:
        h = _latlng_to_cell(c.lat, c.lon, resolution)
        cells = {h}
        for k in range(1, c.radius + 1):
            cells |= set(_disk(h, k))
        for cell in cells:
            rows.append({
                "h3": cell,
                "municipio_id": str(c.municipio_id),
                "municipio": c.municipio,
            })
    return pd.DataFrame(rows).drop_duplicates("h3")


def demo_coverage(resolution: int) -> pd.DataFrame:
    """Crea una cobertura demo de hexágonos H3 para las ciudades principales."""
    return krings_for_centers(DEMO_CENTERS, resolution)
