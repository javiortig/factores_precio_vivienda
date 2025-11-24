# Análisis de Factores que Impactan en los precios de Vivienda en España

**Proyecto**: TFG Matemáticas + Ingeniería del Software (U-TAD) — Sistema reproducible para análisis y predicción del precio de la vivienda en España a nivel municipal.

## 📊 Objetivo del proyecto

Construir un sistema end-to-end que:
1. **Agregue y normalice** datos públicos a nivel municipal (8,132 municipios españoles)
2. **Analice** correlaciones entre precio vivienda y factores socioeconómicos (renta, población, paro)
3. **Prediga** precios futuros mediante modelos de regresión/ML
4. **Visualice** resultados en mapa interactivo con históricos y proyecciones

## 🗂️ Estructura del proyecto

```
src/
  etl/
    sources/          # Scripts de descarga (fetch_*.py)
    normalize/        # Normalización y limpieza (WIP)
    build/            # Construcción datasets maestros (WIP)
data_raw/            # Datos crudos descargados (NO versionado)
data/                # Datos normalizados (NO versionado)
configs/             # Configuración
docs/                # Documentación técnica
logs/                # Logs de ejecución
```

### Flujo de datos (3 fases)

1. **FETCH**: Descarga desde fuentes públicas → `data_raw/`
2. **NORMALIZE**: Limpieza, homogeneización, `municipio_id` → `data/`
3. **BUILD**: Panel consolidado `municipio × periodo` → `data/master/`

## ⚙️ Cómo reproducir

### 1. Preparar entorno

```powershell
# Crear entorno conda
conda create -n tfg python=3.11 -y
conda activate tfg

# Instalar dependencias
pip install -r src/requirements.txt

# Instalar geopandas (para geometrías)
pip install geopandas pyproj shapely
```

### 2. Descargar datos

```powershell
# Opción 1: Todos los fetchers de una vez
python src\etl\sources\run_all_fetchers.py

# Opción 2: Individual
python src\etl\sources\fetch_municipios_ign.py
python src\etl\sources\fetch_valor_tasado_seed.py
python src\etl\sources\fetch_ine_padron_provincias.py  # 13/52 provincias
python src\etl\sources\fetch_ine_adrh_all.py
python src\etl\sources\fetch_sepe_paro_all.py
python src\etl\sources\fetch_euribor_bde.py
```

### 3. Normalizar datos (WIP)

```powershell
# Fase de normalización (en desarrollo)
.\make_flow.bat normalize
```

### 4. Verificar datos descargados

```powershell
# Ver municipios en Padrón
python -c "import pandas as pd; df = pd.read_csv('data_raw/ine/padron_all.csv'); print(f'Municipios: {df.municipio.nunique()}, Periodos: {df.periodo.nunique()}')"

# Ver geometrías IGN
python -c "import geopandas as gpd; gdf = gpd.read_file('data_raw/geo/recintos_municipales_inspire_peninbal_etrs89.shp'); print(f'Municipios: {len(gdf)}, CRS: {gdf.crs}')"
```

## 📥 Fuentes de datos

| Fuente | Script | Salida | Estado | Descripción |
|--------|--------|--------|--------|-------------|
| **Geometrías IGN** | `fetch_municipios_ign.py` | `data_raw/geo/*.shp` | ✅ 8,132 municipios | Polígonos municipales ETRS89 |
| **Precio vivienda (MIVAU)** | `fetch_valor_tasado_seed.py` | `data_raw/mivau/valor_tasado_seed.csv` | ✅ 104 registros | €/m² por municipio (≥25k hab) |
| **Padrón (INE)** | `fetch_ine_padron_provincias.py` | `data_raw/ine/padron_all.csv` | ⚠️ 562 municipios | Población (13/52 provincias) |
| **Renta (ADRH INE)** | `fetch_ine_adrh_all.py` | `data_raw/ine/adrh_all.csv` | ✅ 71,260 registros | Renta neta media por persona |
| **Paro (SEPE)** | `fetch_sepe_paro_all.py` | `data_raw/sepe/paro_municipal_raw.csv` | ✅ 2006-2025 | Paro registrado mensual |
| **Euríbor (BdE)** | `fetch_euribor_bde.py` | `data_raw/macro/ti_1_7.csv` | ✅ Serie completa | Indicador macroeconómico |

Ver documentación detallada en [`src/etl/sources/README.md`](src/etl/sources/README.md).

## ⚠️ Problemas conocidos y soluciones

### 1. Padrón solo cubre 13 provincias (BLOQUEADOR)

**Problema**: La API del INE no ofrece endpoint nacional para la tabla 33775 (Padrón). Cada provincia tiene su propia tabla (ej: 33582 Albacete, 33847 Madrid).

**Estado actual**: 
- ✅ 13 provincias funcionando: Álava, Albacete, Almería, Balears, Barcelona, Burgos, Cáceres, Cuenca, Madrid, Toledo, Valencia, Valladolid, Bizkaia
- ✅ 562 municipios con datos completos (~7% cobertura nacional, ~25% poblacional)
- ⚠️ 39 provincias pendientes de códigos de tabla

**Solución**:
1. Inspeccionar manualmente página INE: https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225
2. Extraer códigos de tabla `t=XXXXX` del enlace de descarga de cada provincia
3. Actualizar `PROVINCIAS_TABLAS` en `src/etl/sources/fetch_ine_padron_provincias.py`

**Próximos códigos prioritarios**: Sevilla (41), Málaga (29), Alicante (03), Murcia (30)

Ver instrucciones detalladas en [`INSTRUCCIONES_PADRON.md`](INSTRUCCIONES_PADRON.md)

### 2. Geometrías IGN requieren descarga manual

**Problema**: Descarga automática desde CNIG falla por cambios en la API.

**Solución**: Descargar manualmente shapefiles y colocar en `data_raw/geo/`:
- `recintos_municipales_inspire_peninbal_etrs89.shp` (y archivos asociados)
- Fuente: https://centrodedescargas.cnig.es/

### 3. Git y archivos grandes

**Solución aplicada**: 
- `data_raw/` y `data/` añadidos a `.gitignore`
- Historial limpiado con `git reset --soft`
- ⚠️ **IMPORTANTE**: NUNCA commitear archivos de datos

## 📝 Siguientes pasos

### Prioridad ALTA:
1. **Completar códigos Padrón provincial** → alcanzar 8,132 municipios (100% cobertura)
2. **Implementar scripts de normalización**:
   - `norm_municipios.py`: IGN → `municipios.parquet` con `municipio_id` + geometría WGS84
   - `norm_ine_*.py`: Añadir `municipio_id` por matching de nombres
   - `norm_master.py`: Crear panel `municipio × periodo` consolidado

### Prioridad MEDIA:
3. **Validación de datos**: Tests de cobertura, municipios faltantes, integridad temporal
4. **Modelos ML**: Regresión precio ~ renta + población + paro + euríbor
5. **Visualización web**: Mapa coroplético con Streamlit/Panel + time slider

## 📚 Documentación adicional

- **Para agentes/LLMs**: [`docs/AGENT_SYSTEM_PROMPT.md`](docs/AGENT_SYSTEM_PROMPT.md) - Contexto completo del proyecto
- **Fetchers**: [`src/etl/sources/README.md`](src/etl/sources/README.md) - Documentación de fuentes de datos
- **Padrón manual**: [`INSTRUCCIONES_PADRON.md`](INSTRUCCIONES_PADRON.md) - Cómo completar códigos provinciales

## 🎯 Visión producto final

1. **ETL automatizado**: `make_flow.bat fetch → normalize → build`
2. **Dataset maestro**: Panel `municipio × periodo` con 6+ variables (precio, renta, población, paro, euríbor, geometría)
3. **Modelos predictivos**: Regresión + series temporales para predicción de precios 2025-2030
4. **Web interactiva**:
   - Mapa coroplético de España (8,132 municipios)
   - Time slider (histórico 2006-2024 + predicciones)
   - Tooltip hover con métricas por municipio
   - Filtros por CCAA/provincia/rango precio