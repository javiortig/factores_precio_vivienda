from __future__ import annotations

from pathlib import Path
import pandas as pd
from pydantic import BaseModel
import yaml

from src.etl.transform_mitma import read_municipal_series, ensure_quarterly_complete
from src.h3.generate_h3_coverage import demo_coverage
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

    # --- 1. Cargar datos ---
    if use_demo:
        demo = pd.read_csv(cfg.data_paths["demo_points_csv"])
        demo["quarter"] = pd.PeriodIndex(demo["date"], freq="Q")
        muni_series = (
            demo.groupby(["municipio_id", "municipio", "quarter"], as_index=False)["price_eur_m2"]
            .mean()
            .rename(columns={"quarter": "date"})
        )
        coverage = demo_coverage(res)
    else:
        muni_series = read_municipal_series(municipal_csv)
        coverage = demo_coverage(res)  # Sustituible por cobertura real

    # --- 2. Forzar tipos coherentes (evita el ValueError int vs object) ---
    for df in [muni_series, coverage]:
        df["municipio_id"] = df["municipio_id"].astype(str)

    muni_series = ensure_quarterly_complete(muni_series)

    # --- 3. Forecast por municipio ---
    metrics_df, fcst_df = fit_and_forecast(
        muni_series, cfg=ForecastConfig(horizon_quarters=horizon, backtest_folds=backfolds)
    )
    hist_df = muni_series.copy()
    hist_df["kind"] = "history"
    fcst_df["kind"] = "forecast"

    # Forzar tipos otra vez (por si statsmodels cambió algo en forecast)
    for df in [hist_df, fcst_df]:
        df["municipio_id"] = df["municipio_id"].astype(str)

    # --- 4. Proyección a H3 ---
    def to_hex(df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.merge(coverage[["h3", "municipio_id"]], on="municipio_id", how="left")
            .dropna(subset=["h3"])
            .reset_index(drop=True)
        )

    hist_hex = to_hex(hist_df)
    fcst_hex = to_hex(fcst_df)

    all_hex = pd.concat([hist_hex, fcst_hex], ignore_index=True)
    all_hex["date"] = pd.PeriodIndex(all_hex["date"], freq="Q")
    all_hex = all_hex.sort_values(["date", "municipio_id", "h3"]).reset_index(drop=True)

    # --- 5. Guardar resultados ---
    Path(hex_parquet).parent.mkdir(parents=True, exist_ok=True)
    all_hex.to_parquet(hex_parquet, index=False)

    metrics_path = Path(hex_parquet).with_name("model_metrics.csv")
    metrics_df.to_csv(metrics_path, index=False)

    print(f"✅ Guardado {hex_parquet} y métricas en {metrics_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", default="configs/settings.yaml")
    parser.add_argument("--demo", action="store_true", help="Usar datos demo")
    args = parser.parse_args()

    build_hex_history(args.settings, use_demo=args.demo)
