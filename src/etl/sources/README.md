# Data Sources Fetchers

Este directorio contiene scripts para descargar automáticamente todas las fuentes de datos del data lake.

## Uso rápido

```powershell
# Ejecutar todos los fetchers
python src\etl\sources\run_all_fetchers.py

# O ejecutar individualmente
python src\etl\sources\fetch_municipios_ign.py
python src\etl\sources\fetch_valor_tasado_seed.py
python src\etl\sources\fetch_ine_padron_all.py
python src\etl\sources\fetch_ine_adrh_all.py
python src\etl\sources\fetch_sepe_paro_all.py
python src\etl\sources\fetch_euribor_bde.py
```

## Fetchers disponibles

### 1. `fetch_municipios_ign.py` — Geometrías municipales (IGN)
- **Fuente**: Centro Nacional de Información Geográfica (CNIG)
- **Salida**: `data_raw/geo/` (shapefiles: `.shp`, `.dbf`, `.shx`, `.prj`)
- **Descripción**: Descarga polígonos de municipios españoles en ETRS89/WGS84
- **Nota**: La descarga automática puede fallar; en ese caso, descarga manualmente desde [CNIG](https://centrodedescargas.cnig.es/CentroDescargas/resultados-busqueda)

### 2. `fetch_valor_tasado_seed.py` — Precio de vivienda (MIVAU/ICANE)
- **Fuente**: ICANE (Cantabria) - CSV consolidado público
- **URL**: `https://www.icane.es/data/api/precio-vivienda-libre-municipios-tasaciones.csv`
- **Salida**: `data_raw/mivau/valor_tasado_seed.csv`
- **Columnas**: `municipio_id`, `municipio`, `date`, `price_eur_m2`, `tasaciones`
- **Cobertura**: Municipios ≥25k habitantes

### 3. `fetch_ine_padron_all.py` — Padrón (población)
- **Fuente**: INE - Tabla 33775 (Padrón por municipio, sexo, edad)
- **URL TSV**: `https://www.ine.es/jaxiT3/files/t/csv_bd/33775.csv`
- **Salidas**:
  - `data_raw/ine/padron_all_raw.csv` (datos sin agregar)
  - `data_raw/ine/padron_all.csv` (agregado municipio×periodo)
- **Columnas agregadas**: `municipio`, `periodo`, `valor` (población total)

### 4. `fetch_ine_adrh_all.py` — Renta media (ADRH)
- **Fuente**: INE - Tabla 31277 (Atlas de Distribución de Renta por Municipio)
- **API**: `https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/31277?tip=AM`
- **Salidas**:
  - `data_raw/ine/adrh_all_raw.csv` (todos los indicadores)
  - `data_raw/ine/adrh_all.csv` (filtrado a "Renta neta media por persona")
- **Columnas**: `municipio`, `indicador`, `periodo`, `valor`

### 5. `fetch_sepe_paro_all.py` — Paro registrado
- **Fuente**: SEPE (Servicio Público de Empleo Estatal)
- **URLs**: `https://sede.sepe.gob.es/.../Paro_por_municipios_{YEAR}_csv.csv` (2006-2025)
- **Salida**: `data_raw/sepe/paro_municipal_raw.csv`
- **Columnas**: `municipio`, `year`, + columnas adicionales del SEPE
- **Nota**: Consolida datos de 20 años en un único CSV

### 6. `fetch_euribor_bde.py` — Euríbor (macro)
- **Fuente**: Banco de España - Serie TI_1_7 (Euríbor 12 meses)
- **URL**: `https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv`
- **Salida**: `data_raw/macro/ti_1_7.csv`
- **Descripción**: Variable macroeconómica temporal

## Arquitectura

Todos los fetchers usan `_fetch_utils.py` con funciones comunes:
- `download_bytes(url, timeout, retries)`: Descarga con reintentos
- `read_csv_auto_from_bytes(b)`: Parseo robusto de CSV con detección de encoding/separadores

## Estructura de salida en `data_raw/`

```
data_raw/
├── geo/
│   ├── recintos_municipales_inspire_peninbal_etrs89.shp
│   ├── recintos_municipales_inspire_peninbal_etrs89.dbf
│   └── lineas_limite/...
├── mivau/
│   └── valor_tasado_seed.csv
├── ine/
│   ├── padron_all_raw.csv
│   ├── padron_all.csv
│   ├── adrh_all_raw.csv
│   └── adrh_all.csv
├── sepe/
│   └── paro_municipal_raw.csv
└── macro/
    └── ti_1_7.csv
```

## Próximos pasos

1. Implementar fase `normalize/` para añadir `municipio_id` (código INE 5 dígitos) a todos los datasets
2. Crear `data/geo/municipios.parquet` con geometrías + códigos INE
3. Consolidar todo en `data/master/municipio_panel.parquet`
