from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List
import pandas as pd
import h3
import numpy as np


@dataclass
class MunicipalityCenter:
    municipio_id: str
    municipio: str
    lat: float
    lon: float
    radius: int


# --- Generador de municipios demo ---
def _generate_random_municipalities(n: int = 50) -> List[MunicipalityCenter]:
    """Genera municipios distribuidos aleatoriamente por España."""
    random.seed(42)
    centers = []
    # límites aproximados España peninsular
    lat_min, lat_max = 36.0, 43.8
    lon_min, lon_max = -9.3, 3.5
    for i in range(n):
        lat = random.uniform(lat_min, lat_max)
        lon = random.uniform(lon_min, lon_max)
        radius = random.randint(8, 14)
        centers.append(
            MunicipalityCenter(
                municipio_id=f"{i:05d}",
                municipio=f"Municipio_{i+1}",
                lat=lat,
                lon=lon,
                radius=radius,
            )
        )
    return centers


# --- Compat helpers para h3 v3/v4 ---
def _latlng_to_cell(lat: float, lon: float, res: int) -> str:
    if hasattr(h3, "geo_to_h3"):
        return h3.geo_to_h3(lat, lon, res)
    elif hasattr(h3, "latlng_to_cell"):
        return h3.latlng_to_cell(lat, lon, res)
    raise RuntimeError("API de h3 no reconocida")


def _disk(origin: str, k: int):
    if hasattr(h3, "k_ring"):
        return h3.k_ring(origin, k)
    elif hasattr(h3, "grid_disk"):
        cells = h3.grid_disk(origin, k)
        if isinstance(cells, list) and isinstance(cells[0], list):
            return {c for sublist in cells for c in sublist}
        return set(cells)
    raise RuntimeError("API de h3 no reconocida")


# --- Demo main functions ---
def krings_for_centers(centers: List[MunicipalityCenter], resolution: int) -> pd.DataFrame:
    """Genera un DataFrame de celdas H3 cubriendo los municipios demo."""
    rows = []
    for c in centers:
        h = _latlng_to_cell(c.lat, c.lon, resolution)
        cells = {h}
        for k in range(1, c.radius + 1):
            cells |= set(_disk(h, k))
        for cell in cells:
            rows.append({"h3": cell, "municipio_id": str(c.municipio_id), "municipio": c.municipio})
    return pd.DataFrame(rows).drop_duplicates("h3")


def demo_coverage(resolution: int) -> pd.DataFrame:
    """Cobertura H3 simulada para unos 50 municipios."""
    centers = _generate_random_municipalities(50)
    return krings_for_centers(centers, resolution)


# --- También generaremos las series simuladas ---
def generate_demo_series() -> pd.DataFrame:
    """Crea series trimestrales sintéticas 2005–2025 para los municipios simulados."""
    centers = _generate_random_municipalities(50)
    quarters = pd.period_range("2005Q1", "2025Q4", freq="Q")
    rows = []
    np.random.seed(42)

    for c in centers:
        base_price = np.random.uniform(900, 4500)
        annual_growth = np.random.uniform(-0.01, 0.06)  # -1 % a +6 % anual
        seasonal_amp = np.random.uniform(0.01, 0.05)
        price = base_price
        for i, q in enumerate(quarters):
            # crecimiento y estacionalidad
            trend = (1 + annual_growth / 4) ** i
            seasonal = 1 + seasonal_amp * np.sin(2 * np.pi * (i % 4) / 4)
            noise = np.random.normal(0, 0.02)
            price_q = price * trend * seasonal * (1 + noise)
            rows.append(
                {
                    "municipio_id": str(c.municipio_id),
                    "municipio": c.municipio,
                    "date": q,
                    "price_eur_m2": round(price_q, 2),
                }
            )
    return pd.DataFrame(rows)
