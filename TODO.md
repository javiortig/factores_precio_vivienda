## Problemas bloqueantes

### ⚠️ CRÍTICO: Padrón solo devuelve 1 provincia
**Estado**: Bloqueado
**Descripción**: El fetcher `fetch_ine_padron_all.py` solo obtiene datos de 95 municipios de A Coruña (provincia 15) en lugar de los 8,132 municipios esperados.

**Análisis**:
- API Tempus JSON (`https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775?tip=AM`) devuelve 29,376 items
- Todos los items con dimensión "Municipios" son de provincia 15
- No existe parámetro URL para filtrar por provincia
- Los endpoints CSV (csv_bd, csv_bdsc) también devuelven solo 1 provincia

**Soluciones evaluadas**:
1. ✅ **Descarga manual PC-Axis** (Recomendado)
   - Ir a https://www.ine.es/jaxiT3/Tabla.htm?t=33775
   - Seleccionar TODOS los municipios (8,132)
   - Descargar formato .px
   - Instalar `pip install pyaxis`
   - Parsear el archivo
   
2. ⚙️ **Usar datos ADRH** (tabla 31277)
   - Ya descargado en `fetch_ine_adrh_all.py`
   - Incluye población junto con renta
   - Verificar si tiene todos los municipios
   
3. ❌ **Scraping 52 provincias**
   - La API no acepta filtros por provincia
   - Requeriría scraping de interfaz web
   - Riesgo de violar ToS del INE

**Impacto**: Bloquea creación del dataset maestro completo. Sin datos de población para 8,037 municipios (~98.8%).

---

Ideas:
- Hacer un modelo de clustering que el usuario da unas caracteristicas y el modelo le recomienda casas en tiempo real.
- Regresion para que te predizca el precio de una vivienda.
- Recomendaciones de a qué precio vender tu vivienda dadas unas características y comparando con ventas pasadas.
- UI con un mapa de España con los datos en forma de puntos con hover. Mapa de calor.
