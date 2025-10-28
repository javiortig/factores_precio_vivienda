# src/etl/__init__.py
"""
ETL package
- sources/: descarga a data_raw/
- normalize/: curación a data/curated/
- build/: ensamblado tablas finales
"""
__all__ = ["sources", "normalize", "build"]
