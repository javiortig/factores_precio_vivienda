from __future__ import annotations

from pathlib import Path
import pandas as pd
from pydantic import BaseModel
import yaml

from src.etl.transform_mitma import read_municipal_series, ensure_quarterly_complete
from src.h3.generate_h3_coverage import demo_coverage, krings_for_centers, DEMO_CENTERS
from src.ts.forecast import fit_and_forecast, ForecastConfig

class Settings(BaseModel):
    data_paths: dict
    h3: dict
    forecast: dict

def load_settings(path: str | Path) -> Settings:
    with open(path, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return Settings(**d)

def build_hex_history(settings_path: str | Path, use_demo: bool = False) -> None:
    cfg = load_settings(settings_path)
    res = cfg.h3.get("resolution", 8)
    municipal_csv = cfg.data_paths["municipal_series_csv"]
    hex_parquet = cfg.data_paths["hex_prices_parquet"]
    horizon = cfg.forecast.get("horizon_quarters", 8)
    backfolds = cfg.forecast.get("backtest_folds", 4)

    if use_demo:
        # Crea serie municipal sintética a partir de demo_points (4 ciudades)
        demo = pd.read_csv(cfg.data_paths["demo_points_csv'])
        demo["quarter"] = pd.PeriodIndex(demo["date"], freq="Q")
        muni_series = (demo
            .groupby(["municipio_id", "municipio", "quarter"], as_index=False)["price_eur_m2"].mean()
            .rename(columns={"quarter": "date"})
        )
        coverage = demo_coverage(res)
    else:
        muni_series = read_municipal_series(municipal_csv)
        coverage = demo_coverage(res)  # reemplaza por una cobertura real si la tienes
        # Ejemplo de cobertura real (si defines tus centros): 
        # from src.h3.generate_h3_coverage import MunicipalityCenter
        # centers = [MunicipalityCenter("XXXXXXXX","Nombre", lat, lon, radius), ...]
        # coverage = krings_for_centers(centers, res)

    muni_series = ensure_quarterly_complete(muni_series)

    # Forecast por municipio
    metrics_df, fcst_df = fit_and_forecast(muni_series, cfg=ForecastConfig(horizon_quarters=horizon, backtest_folds=backfolds))
    hist_df = muni_series.copy()
    hist_df["kind"] = "history"

    # Proyección a H3: join por municipio_id
    def to_hex(df: pd.DataFrame) -> pd.DataFrame:
        return (df.merge(coverage[["h3", "municipio_id"]], on="municipio_id", how="left")
                  .dropna(subset=["h3"]))  # descarta hex sin cobertura

    hist_hex = to_hex(hist_df)
    fcst_hex = to_hex(fcst_df)

    all_hex = pd.concat([hist_hex, fcst_hex], ignore_index=True)
    # Orden y tipos
    all_hex["date"] = pd.PeriodIndex(all_hex["date"], freq="Q")
    all_hex = all_hex.sort_values(["date", "municipio_id", "h3"]).reset_index(drop=True)

    Path(hex_parquet).parent.mkdir(parents=True, exist_ok=True)
    all_hex.to_parquet(hex_parquet, index=False)

    # Guarda métricas para inspección
    metrics_path = Path(hex_parquet).with_name("model_metrics.csv")
    metrics_df.to_csv(metrics_path, index=False)

    print(f"✅ Guardado {hex_parquet} y métricas en {metrics_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", default="configs/settings.yaml")
    parser.add_argument("--demo", action="store_true", help="Usar datos demo en lugar de CSV municipal real")
    args = parser.parse_args()
    build_hex_history(args.settings, use_demo=args.demo)
