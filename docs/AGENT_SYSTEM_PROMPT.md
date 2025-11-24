# AGENT SYSTEM PROMPT - TFG Precio Vivienda España

Eres un agente especializado trabajando en un TFG (Trabajo Fin de Grado) de Matemáticas + Ingeniería del Software sobre **predicción de precios de vivienda en España** usando datos públicos a nivel municipal.

## CONTEXTO DEL PROYECTO

**Objetivo**: Sistema reproducible de big data + modelos predictivos + visualización que:
- Agregue y normalice datos públicos municipales
- Permita análisis exploratorio de precios y factores socioeconómicos
- Entrene modelos de regresión/predicción de precios por municipio
- Exponga mapa interactivo con históricos y predicciones

**Stack tecnológico**: Python (conda env `tfg`), ETL propio, pandas, geopandas, requests, streamlit/panel/dash (visualización).

## ARQUITECTURA DE DATOS

### Flujo ETL en 3 fases:

1. **FETCH** (`data_raw/`): Descarga cruda desde fuentes públicas (NO versionado en git)
2. **NORMALIZE** (`data/`): Limpieza, homogeneización, añadir `municipio_id` (NO versionado)
3. **MASTER**: Panel `municipio × periodo` consolidado con todas las variables

### Fuentes de datos principales:

| Fuente | Script | Salida | Columnas clave |
|--------|--------|--------|----------------|
| **IGN Geometrías** | `fetch_municipios_ign.py` | `data_raw/geo/*.shp` | Polígonos municipales ETRS89 |
| **MIVAU Precios** | `fetch_valor_tasado_seed.py` | `data_raw/mivau/valor_tasado_seed.csv` | `municipio_id`, `date`, `price_eur_m2` |
| **INE Padrón** | `fetch_ine_padron_provincias.py` | `data_raw/ine/padron_all.csv` | `municipio`, `periodo`, `valor` (población) |
| **INE ADRH Renta** | `fetch_ine_adrh_all.py` | `data_raw/ine/adrh_all.csv` | `municipio`, `periodo`, `valor` (renta media) |
| **SEPE Paro** | `fetch_sepe_paro_all.py` | `data_raw/sepe/paro_municipal_raw.csv` | `municipio`, `year`, valores paro |
| **BdE Euríbor** | `fetch_euribor_bde.py` | `data_raw/macro/ti_1_7.csv` | Serie temporal macro |

## PROBLEMAS CONOCIDOS Y SOLUCIONES

### 1. INE API filtrada por provincia
**Problema**: APIs Tempus (`DATOS_TABLA/33775`) devuelven solo 1 provincia (ej: A Coruña)
**Causa**: El INE no ofrece endpoint nacional para tabla 33775, solo tablas provinciales individuales
**Solución implementada**: 
- Script `fetch_ine_padron_provincias.py` que itera por 52 provincias
- Cada provincia tiene su propio código de tabla (ej: 33582 Albacete, 33847 Madrid)
- **Estado actual**: 13/52 provincias funcionando (562 municipios, ~25% cobertura nacional)
- **Municipios descargados**: Álava, Albacete, Almería, Balears, Barcelona, Burgos, Cáceres, Cuenca, Madrid, Toledo, Valencia, Valladolid, Bizkaia
- **Provincias pendientes**: 39 provincias necesitan códigos de tabla verificados manualmente

**Cómo completar**:
1. Usuario inspecciona página INE: https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225
2. Para cada provincia, extraer código `t=XXXXX` del enlace de descarga
3. Actualizar diccionario `PROVINCIAS_TABLAS` en `fetch_ine_padron_provincias.py`

### 2. Geometrías IGN
**Problema**: Descarga automática falla por cambios en CNIG
**Solución**: Descarga manual → `data_raw/geo/lineas_limite/` y `recintos_municipales_*.shp`
**Verificado**: 8,132 municipios con código NATCODE (INE en posiciones 4-9)

### 3. Git con archivos grandes
**Problema**: Commit accidental con shapefiles/CSV (100-190MB) rechazado por GitHub
**Solución**: `.gitignore` actualizado, `git reset --soft`, datos excluidos del repositorio

## ESTRUCTURA DE DIRECTORIOS

```
src/
  etl/
    sources/          # Scripts de descarga (fetch_*.py)
      _fetch_utils.py # Utilidades comunes (download_bytes, read_csv_auto)
      run_all_fetchers.py  # Orquestador de todos los fetchers
    normalize/        # Scripts normalización (WIP)
    build/            # Scripts de construcción de datasets maestros (WIP)
data_raw/            # Datos crudos descargados (IGNORADO git)
  geo/               # Shapefiles IGN (8,132 municipios)
  ine/               # Padrón (562 municipios), ADRH (71,260 registros)
  mivau/             # Precios vivienda (104 registros)
  sepe/              # Paro registrado (2006-2025)
  macro/             # Euríbor
data/                # Datos normalizados (IGNORADO git)
  geo/               # municipios.parquet (WIP)
  master/            # Panel consolidado (WIP)
configs/             # Configuración rutas/parámetros
logs/                # Logs de ejecución
docs/                # Documentación técnica
```

## COMANDOS CLAVE

```powershell
# Activar entorno
conda activate tfg

# Descargar todas las fuentes
python src\etl\sources\run_all_fetchers.py

# O individual:
python src\etl\sources\fetch_ine_padron_provincias.py
python src\etl\sources\fetch_ine_adrh_all.py
python src\etl\sources\fetch_valor_tasado_seed.py
python src\etl\sources\fetch_sepe_paro_all.py

# Ver estado de datos descargados
python -c "import pandas as pd; df = pd.read_csv('data_raw/ine/padron_all.csv'); print(f'Municipios: {df.municipio.nunique()}, Periodos: {df.periodo.nunique()}')"

# Verificar geometrías IGN
python -c "import geopandas as gpd; gdf = gpd.read_file('data_raw/geo/recintos_municipales_inspire_peninbal_etrs89.shp'); print(f'Municipios IGN: {len(gdf)}, CRS: {gdf.crs}')"
```

## TAREAS PENDIENTES PRIORITARIAS

### 1. Completar códigos Padrón provincial (BLOQUEADOR)
- **Objetivo**: Pasar de 562 a ~8,132 municipios
- **Acción**: Usuario proporcionará códigos de tabla para:
  - Sevilla (41), Málaga (29), Alicante (03), Murcia (30)
- **Con 4 códigos más**: Buscar patrón numérico o rellenar restantes
- **Archivo a editar**: `src/etl/sources/fetch_ine_padron_provincias.py` → diccionario `PROVINCIAS_TABLAS`

### 2. Scripts de normalización
- `norm_municipios.py`: IGN → `data/geo/municipios.parquet` 
  - Columnas: `municipio_id` (5 dígitos INE), `municipio` (nombre), `geometry` (WGS84)
- `norm_ine_padron.py`: Añadir `municipio_id` por match de nombres con IGN
- `norm_ine_adrh.py`: Ídem
- `norm_sepe_paro.py`: Ídem
- `norm_mivau_precios.py`: Ya tiene `municipio_id`, solo validar formato

### 3. Dataset maestro
- `build_master_panel.py`: 
  - Join de todas las tablas normalizadas por `municipio_id` + `periodo`
  - Output: `data/master/municipio_panel.parquet`
  - Columnas: `municipio_id`, `periodo`, `poblacion`, `renta`, `paro`, `precio_m2`, `euribor`

### 4. Validación y tests
- Verificar cobertura temporal (¿desde qué año tenemos datos completos?)
- Identificar municipios con datos faltantes
- Tests de integridad (municipios IGN vs municipios datos)

## DECISIONES TÉCNICAS IMPORTANTES

- **NO usar H3**: Visualización final con polígonos municipales reales (choropleth)
- **municipio_id**: Código INE 5 dígitos como clave primaria universal
- **Normalización de nombres**: 
  - Quitar tildes para matching: `unidecode` o normalización NFKD
  - Variantes: A Coruña/La Coruña, Valencia/València, Alicante/Alacant
  - Crear tabla de alias (`configs/alias_municipios.yaml`)
- **Formato preferido**: Parquet para tablas grandes (compresión + tipos), CSV para auditoría
- **CRS**: ETRS89 (EPSG:4258) en shapefiles → convertir a WGS84 (EPSG:4326) para web
- **Encoding**: UTF-8 siempre, `errors='ignore'` en lectura de CSVs del INE

## VISION PRODUCTO FINAL

### 1. ETL automatizado
```powershell
.\make_flow.bat fetch      # Descarga todo a data_raw/
.\make_flow.bat normalize  # Limpia y añade municipio_id → data/
.\make_flow.bat build      # Construye panel maestro → data/master/
```

### 2. Modelos ML
- Regresión: precio_m2 ~ renta + población + paro + euríbor + dummies_provincia
- Temporal: ARIMA/Prophet para predicciones futuras por municipio
- Features engineering: ratios (renta/precio, paro/población), lags temporales

### 3. Visualización web
- **Tecnología**: Streamlit o Panel (más interactivo)
- **Componentes**:
  - Mapa coroplético con `folium` o `plotly`
  - Polígonos municipales coloreados por precio/renta
  - Time slider para cambiar año (histórico 2006-2024 + predicciones 2025-2030)
  - Tooltip hover: municipio, precio actual/predicho, renta, población, paro
  - Filtros laterales: CCAA, provincia, rango precio, población min/max
  - Gráficos temporales: evolución precio/renta al hacer clic en municipio

## CUANDO TRABAJES EN ESTE PROYECTO

### Reglas de oro:
1. **Git**: NUNCA commitear `data_raw/` ni `data/` (verificar `.gitignore`)
2. **Idempotencia**: Los fetchers deben sobrescribir archivos existentes sin errores
3. **Encoding**: UTF-8 con BOM para CSVs que se abran en Excel
4. **Logs**: Formato `print("✅ OK")`, `print("⚠️ Warning")`, `print("❌ Error")`
5. **Documentación**: Docstrings en scripts con formato de salida y columnas

### Debugging común:
- **Error "No columns to parse"**: CSV vacío o encoding incorrecto → usar `read_csv_auto_from_bytes`
- **Municipios faltantes en join**: Nombres no coinciden → usar normalización + alias
- **CRS mismatch**: Siempre verificar `gdf.crs` antes de merge/plot
- **API INE devuelve datos vacíos**: Verificar código de tabla correcto o usar fallback CSV

### Próximo paso sugerido:
Esperar a que usuario proporcione 4 códigos de tabla (Sevilla, Málaga, Alicante, Murcia) para completar Padrón y alcanzar >70% cobertura poblacional.
