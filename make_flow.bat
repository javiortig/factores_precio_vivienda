@echo off
setlocal

REM ==== 1) SOURCES ====
echo [1/3] Fetch...
python -m src.etl.sources.fetch_municipios_ign || goto :error
python -m src.etl.sources.fetch_mivau_valor_tasado_seed || goto :error
python -m src.etl.sources.fetch_ine_adrh || goto :error
python -m src.etl.sources.fetch_ine_padron || goto :error
python -m src.etl.sources.fetch_sepe_paro_all || goto :error
python -m src.etl.sources.fetch_euribor_bde || goto :error

REM ==== 2) NORMALIZE ====
echo [2/3] Normalize...
python -m src.etl.normalize.norm_geo_municipios || goto :error
python -m src.etl.normalize.norm_mivau_valor_tasado || goto :error
python -m src.etl.normalize.norm_ine_adrh || goto :error
python -m src.etl.normalize.norm_ine_padron || goto :error
python -m src.etl.normalize.norm_sepe_paro || goto :error
python -m src.etl.normalize.norm_euribor || goto :error

REM ==== 3) BUILD ====
echo [3/3] Build...
python -m src.etl.build.build_master_muni || goto :error

echo.
echo ✅ Flujo completo terminado (fetch + normalize + build).
goto :eof

:error
echo.
echo ❌ Error en el flujo. Revisa el mensaje anterior.
exit /b 1
