from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd, yaml

from .readers_mitma import read_mitma_municipal
from .readers_ine import download_ipv_ccaa_csv, normalize_ipv_ccaa
from .euribor_reader import read_euribor_to_quarter
from .coverage_builder import build_h3_coverage_from_centroids
from .downscaler import project_muni_to_h3

def ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

def parse_args():
    p = argparse.ArgumentParser("ETL real: MITMA + INE + BdE + H3")
    p.add_argument("--config", default="configs/data_sources.yaml")
    p.add_argument("--download", nargs="*", choices=["ine"], help="Qué descargar automáticamente (ine)")
    p.add_argument("--build-h3", action="store_true", help="Construir cobertura H3 y proyectar")
    return p.parse_args()

def main():
    args = parse_args()
    cfg = yaml.safe_load(open(args.config, "r", encoding="utf-8"))

    out_dir = Path(cfg["out_dir"])
    ensure_dir(out_dir)

    # ---- MITMA (lectura local) ----
    mitma_csv = Path(cfg["mitma_csv"])
    if not mitma_csv.exists():
        raise FileNotFoundError(f"No encuentro {mitma_csv}. Coloca el CSV real de MITMA.")
    muni_series = read_mitma_municipal(str(mitma_csv))  # municipio_id, municipio, date(Period[Q]), price_eur_m2

    # ---- INE IPV (descarga opcional y normalización) ----
    ipv_path = out_dir / "ipv_ccaa_raw.csv"
    if args.download and "ine" in args.download:
        download_ipv_ccaa_csv(cfg["ine_ipv_url"], ipv_path)
    if ipv_path.exists():
        ipv_df = normalize_ipv_ccaa(str(ipv_path))
        ipv_df.to_parquet(out_dir / "ipv_benchmark.parquet", index=False)
        print(f"✅ IPV guardado en {out_dir/'ipv_benchmark.parquet'}")

    # ---- BdE Euríbor (lectura local y trimestralización) ----
    euribor_csv = Path(cfg["euribor_csv"])
    if euribor_csv.exists():
        euribor_q = read_euribor_to_quarter(str(euribor_csv))
        euribor_q.to_parquet(out_dir / "macro_euribor.parquet", index=False)
        print(f"✅ Euríbor guardado en {out_dir/'macro_euribor.parquet'}")
    else:
        print("ℹ️ No hay euribor_csv; sáltate o añádelo más tarde (date, euribor_12m).")

    # ---- Guardar serie municipal base (QA) ----
    muni_series.to_parquet(out_dir / "targets_muni.parquet", index=False)
    print(f"✅ Serie municipal guardada en {out_dir/'targets_muni.parquet'}")

    # ---- Cobertura H3 + proyección ----
    if args.build_h3:
        centroids_csv = Path(cfg["centroids_csv"])
        if not centroids_csv.exists():
            raise FileNotFoundError(f"Falta {centroids_csv}. Crea centroides municipales (municipio_id, municipio, lat, lon).")
        centroids_df = pd.read_csv(centroids_csv)
        cov = build_h3_coverage_from_centroids(
            centroids_df,
            resolution=int(cfg["h3_resolution"]),
            radius=int(cfg["krings_radius_default"])
        )
        cov["municipio_id"] = cov["municipio_id"].astype(str)
        muni_series["municipio_id"] = muni_series["municipio_id"].astype(str)

        hex_prices = project_muni_to_h3(muni_series, cov)
        hex_prices.to_parquet(out_dir / "targets_prices.parquet", index=False)
        print(f"✅ Proyección H3 guardada en {out_dir/'targets_prices.parquet'}")

if __name__ == "__main__":
    main()
