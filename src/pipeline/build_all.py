from __future__ import annotations

import argparse
import yaml
from pathlib import Path

from src.pipeline.make_h3_history import build_hex_history, load_settings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolution", type=int, default=None, help="Resolución H3 (7-9) opcional para override")
    parser.add_argument("--horizon", type=int, default=None, help="Horizonte de predicción en trimestres")
    parser.add_argument("--backfolds", type=int, default=None, help="Nº folds de backtest rolling")
    parser.add_argument("--demo", action="store_true", help="Usar datos demo")
    parser.add_argument("--settings", default="configs/settings.yaml")
    args = parser.parse_args()

    # Carga settings y aplica overrides del CLI
    cfg_path = Path(args.settings)
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if args.resolution is not None:
        cfg.setdefault("h3", {})["resolution"] = args.resolution
    if args.horizon is not None:
        cfg.setdefault("forecast", {})["horizon_quarters"] = args.horizon
    if args.backfolds is not None:
        cfg.setdefault("forecast", {})["backtest_folds"] = args.backfolds

    # Escribe settings temporales
    tmp_path = cfg_path.with_name("settings.override.yaml")
    with open(tmp_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True)

    # Construye
    build_hex_history(tmp_path, use_demo=args.demo)

if __name__ == "__main__":
    main()
