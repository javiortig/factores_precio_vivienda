from __future__ import annotations
import h3

def cell_from_latlon(lat: float, lon: float, res: int) -> str:
    if hasattr(h3, "geo_to_h3"):  # v3
        return h3.geo_to_h3(lat, lon, res)
    if hasattr(h3, "latlng_to_cell"):  # v4
        return h3.latlng_to_cell(lat, lon, res)
    raise RuntimeError("API h3 no reconocida")

def neighbors_disk(origin: str, k: int):
    if hasattr(h3, "k_ring"):
        return h3.k_ring(origin, k)
    if hasattr(h3, "grid_disk"):
        cells = h3.grid_disk(origin, k)
        if isinstance(cells, list) and cells and isinstance(cells[0], list):
            return {c for sub in cells for c in sub}
        return set(cells)
    raise RuntimeError("API h3 no reconocida")
