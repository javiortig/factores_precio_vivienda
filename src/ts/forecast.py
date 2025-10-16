from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Tuple
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

@dataclass
class ForecastConfig:
    horizon_quarters: int = 8
    backtest_folds: int = 4

def _fit_ets(y: pd.Series):
    # ETS aditivo con estacionalidad anual (4 trimestres)
    model = ExponentialSmoothing(y, trend="add", seasonal="add", seasonal_periods=4)
    return model.fit(optimized=True, use_brute=True)

def backtest_rolling(y: pd.Series, horizon: int, folds: int) -> pd.DataFrame:
    results = []
    for i in range(folds, 0, -1):
        split = -i * horizon
        y_train = y.iloc[:split] if split != 0 else y
        y_test = y.iloc[split: split + horizon] if split != 0 else pd.Series(dtype=float)
        if len(y_train) < 8 or len(y_test) == 0:
            continue
        try:
            fit = _fit_ets(y_train)
            fcst = fit.forecast(horizon)
            df = pd.DataFrame({"y_true": y_test.values, "y_pred": fcst.values}, index=y_test.index)
            results.append(df)
        except Exception:
            continue
    if not results:
        return pd.DataFrame(columns=["y_true", "y_pred"])
    out = pd.concat(results)
    out["mae"] = (out["y_true"] - out["y_pred"]).abs()
    out["ape"] = (out["y_true"] - out["y_pred"]).abs() / out["y_true"].replace(0, np.nan)
    return out

def fit_and_forecast(df: pd.DataFrame, cfg: ForecastConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Entrena ETS por municipio y devuelve (metrics_df, forecast_df). 
    df: columnas municipio_id, municipio, date (Period[Q]), price_eur_m2
    """
    metrics = []
    forecasts = []
    for mid, g in df.groupby("municipio_id", sort=False):
        g = g.sort_values("date")
        y = pd.Series(g["price_eur_m2"].values, index=g["date"].values)
        bt = backtest_rolling(y, cfg.horizon_quarters, cfg.backtest_folds)
        mae = bt["mae"].mean() if not bt.empty else np.nan
        mape = (bt["ape"].mean() * 100) if not bt.empty else np.nan
        metrics.append({"municipio_id": mid, "municipio": g["municipio"].iloc[0], "MAE": mae, "MAPE": mape})
        # Fit final
        try:
            fit = _fit_ets(y)
            fcst = fit.forecast(cfg.horizon_quarters)
            fdf = pd.DataFrame({
                "municipio_id": mid,
                "municipio": g["municipio"].iloc[0],
                "date": fcst.index,
                "price_eur_m2": fcst.values,
                "kind": "forecast"
            })
            forecasts.append(fdf)
        except Exception:
            continue
    metrics_df = pd.DataFrame(metrics)
    forecast_df = pd.concat(forecasts, ignore_index=True) if forecasts else pd.DataFrame(columns=["municipio_id","municipio","date","price_eur_m2","kind"])
    return metrics_df, forecast_df
