# Análisis de Factores que Impactan en los precios de Vivienda en España y posibles predicciones de sus futuros valores

En este trabajo se busca realizar una minería de datos de distintas fuentes de datos que puedan ser relevantes para
posteriormente realizar un análisis de las posibles características que afectan con mayor intensidad al precio de la vivienda en España.

**Proyecto**: TFG Matemáticas + Ingeniería del Software (U-TAD) — Sistema reproducible para análisis y predicción del precio de la vivienda en España.

**Estructura rápida**
- `data_raw/`: Descargas crudas (NO versionadas en git). Contiene shapefiles IGN, CSV/JSON de INE, SEPE, MIVAU, BdE.
- `data/`: Salidas normalizadas (parquet/csv) generadas por la fase `normalize`.
- `src/etl/sources/`: Scripts de ingestión (fetch_*.py).
- `src/etl/normalize/`: Scripts de normalización y unión a `municipio_id`.
- `src/app/`: Visualización (streamlit) y utilidades de mapa.

**Principales objetivos**
- Agregar y normalizar datos públicos a nivel municipal.
- Generar un dataset maestro `municipio × periodo` con variables: precio (MIVAU), renta (ADRH), población (Padrón), paro (SEPE), euríbor, geometría municipal.
- Entrenar modelos de regresión/predicción del precio por municipio y periodo.
- Servicio de visualización: mapa coroplético con histórico y predicción por tooltip.

**Cómo reproducir los datos (resumen rápido)**

Preparar entorno:
```powershell
conda create -n tfg python=3.10 -y
conda activate tfg
pip install -r src/requirements.txt
```

Ejecutar fetchers (descarga a `data_raw/`):
```powershell
# Opción 1: Todos los fetchers de una vez
python src\etl\sources\run_all_fetchers.py

# Opción 2: Via batch
.\make_flow.bat fetch

# Opción 3: Individual
python src\etl\sources\fetch_valor_tasado_seed.py
python src\etl\sources\fetch_ine_padron_all.py
python src\etl\sources\fetch_ine_adrh_all.py
python src\etl\sources\fetch_sepe_paro_all.py
python src\etl\sources\fetch_euribor_bde.py
python src\etl\sources\fetch_municipios_ign.py  # Puede requerir descarga manual
```

Fase Normalize (WIP): `.\make_flow.bat normalize`

**Estado actual del Data Lake** ✅

Todos los fetchers funcionan correctamente. Datos disponibles en `data_raw/`:

| Fuente | Script | Salida | Filas/Elementos | Estado |
|--------|--------|--------|-----------------|--------|
| **Geometrías IGN** | `fetch_municipios_ign.py` | `data_raw/geo/*.shp` | 8,132 municipios | ✅ Manual |
| **Precio vivienda (MIVAU)** | `fetch_valor_tasado_seed.py` | `data_raw/mivau/valor_tasado_seed.csv` | 103 municipios×periodo | ✅ |
| **Padrón (INE)** | `fetch_ine_padron_all.py` | `data_raw/ine/padron_all.csv` | ⚠️ 95 municipios (solo A Coruña) | ⚠️ Bloqueado |
| **Renta (ADRH INE)** | `fetch_ine_adrh_all.py` | `data_raw/ine/adrh_all.csv` | 71,260 registros | ✅ |
| **Paro (SEPE)** | `fetch_sepe_paro_all.py` | `data_raw/sepe/paro_municipal_raw.csv` | 2006-2025 consolidado | ✅ |
| **Euríbor (BdE)** | `fetch_euribor_bde.py` | `data_raw/macro/ti_1_7.csv` | Serie temporal | ✅ |

Ver documentación detallada en [`src/etl/sources/README.md`](src/etl/sources/README.md).

**Notas operativas / problemas conocidos**
- `data_raw/` y `data/` deben estar en `.gitignore` — ya configurado.
- Hubo un commit accidental con datos grandes; se hizo `git reset --soft` y nuevo commit sin los datos.
- Descarga automática de shapefiles IGN tiene pasos manuales: se almacenan en `data_raw/geo/`.
- Se empezó con H3 para visualización, pero la decisión final es usar polígonos municipales reales.
- **⚠️ BLOQUEADOR CRÍTICO**: `fetch_ine_padron_all.py` solo obtiene 95 municipios de A Coruña (provincia 15) debido a limitaciones de la API Tempus del INE. La API devuelve 29,376 items JSON pero todos pertenecen a la misma provincia. **Solución requerida**: Descarga manual del archivo PC-Axis (.px) completo desde [INE Tabla 33775](https://www.ine.es/jaxiT3/Tabla.htm?t=33775) seleccionando TODOS los municipios (8,132), o usar datos de población incluidos en ADRH.

**Siguientes pasos útiles**
- Implementar `src/etl/normalize/norm_municipios.py` para generar `data/geo/municipios.parquet` con `municipio_id` (INE) y geometría en WGS84.
- Finalizar `make_flow.bat normalize` y documentarlo.
- Añadir tests mínimos para validación de matches por nombre entre INE y geometría.

Para más detalles técnicos o para obtener un prompt listo para agentes, ver `docs/AGENT_SYSTEM_PROMPT.md`.