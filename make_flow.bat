@echo off

set PY=python
set LOGFILE=logs\make_flow.log
if not exist logs mkdir logs

echo === INICIO EJECUCION === > %LOGFILE%
echo [INFO] Log guardado en %LOGFILE%
echo.

if "%1"=="" (
    set TARGET=all
) else (
    set TARGET=%1
)

if "%TARGET%"=="fetch" goto FETCH
if "%TARGET%"=="normalize" goto NORMALIZE
if "%TARGET%"=="build" goto BUILD
if "%TARGET%"=="all" goto ALL
if "%TARGET%"=="app" goto APP
goto END

:FETCH
echo [1/3] DESCARGANDO FUENTES...
echo --- Fetch IGN municipios ---
%PY% -m src.etl.sources.fetch_municipios_ign       >> %LOGFILE% 2>&1
echo --- Fetch MIVAU valor tasado ---
%PY% -m src.etl.sources.fetch_valor_tasado_seed    >> %LOGFILE% 2>&1
echo --- Fetch INE ADRH ---
%PY% -m src.etl.sources.fetch_ine_adrh             >> %LOGFILE% 2>&1
echo --- Fetch INE Padron ---
%PY% -m src.etl.sources.fetch_ine_padron           >> %LOGFILE% 2>&1
echo --- Fetch SEPE Paro ---
%PY% -m src.etl.sources.fetch_sepe_paro_all        >> %LOGFILE% 2>&1
echo --- Fetch BdE Euribor ---
%PY% -m src.etl.sources.fetch_euribor_bde          >> %LOGFILE% 2>&1
echo ✅ Fetch completado.
goto END

:NORMALIZE
echo [2/3] NORMALIZANDO...
%PY% -m src.etl.normalize.norm_geo_municipios      >> %LOGFILE% 2>&1
%PY% -m src.etl.normalize.norm_mivau_valor_tasado  >> %LOGFILE% 2>&1
%PY% -m src.etl.normalize.norm_ine_adrh            >> %LOGFILE% 2>&1
%PY% -m src.etl.normalize.norm_ine_padron          >> %LOGFILE% 2>&1
%PY% -m src.etl.normalize.norm_sepe_paro           >> %LOGFILE% 2>&1
%PY% -m src.etl.normalize.norm_euribor             >> %LOGFILE% 2>&1
echo ✅ Normalización completada.
goto END

:BUILD
echo [3/3] CONSTRUYENDO TABLA MAESTRA...
%PY% -m src.etl.build.build_master_muni            >> %LOGFILE% 2>&1
echo ✅ Build completado.
goto END

:ALL
call "%~f0" fetch
call "%~f0" normalize
call "%~f0" build
echo 🎉 Flujo completo terminado.
goto END

:APP
echo Ejecutando interfaz Streamlit...
streamlit run src/app/municipal_map.py
goto END

:END
echo.
echo [FIN] Revisa el log en %LOGFILE%
exit /b
