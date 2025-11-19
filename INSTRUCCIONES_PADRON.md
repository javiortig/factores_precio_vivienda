# 📋 Instrucciones: Completar códigos de tabla del Padrón

## Estado actual

✅ **Funcionan correctamente** (11 provincias):
- [01] Álava/Araba - 33589
- [02] Albacete - 33582
- [04] Almería - 33584
- [07] Balears - 33587
- [08] Barcelona - 33588
- [09] Burgos - 33590
- [10] Cáceres - 33591
- [16] Cuenca - 33597
- [28] Madrid - 33847 ✓ (confirmado por usuario)
- [45] Toledo - 33626
- [46] Valencia - 33627
- [47] Valladolid - 33628
- [48] Bizkaia - 33629

❌ **Faltan códigos** (41 provincias): Necesitan inspección manual

---

## 🔧 Cómo obtener los códigos faltantes

### Opción 1: Manual (Lento pero seguro)

Para **cada provincia** que falta:

1. Ir a: https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225

2. Buscar la provincia en la lista del lado izquierdo

3. Expandir la provincia y hacer clic en "Cifras de población" o similar

4. Buscar el icono de descarga (🔽) y hacer clic derecho → "Inspeccionar elemento"

5. El elemento HTML será algo como:
   ```html
   <a href="https://www.ine.es/jaxiT3/dlgExport.htm?t=XXXXX&L=0&nocab=1" ...>
   ```

6. Copiar el número `XXXXX` (código de tabla)

7. Añadirlo al archivo: `src/etl/sources/fetch_ine_padron_provincias.py`
   - Buscar la línea de esa provincia
   - Cambiar `"tabla": None` por `"tabla": "XXXXX"`

### Opción 2: Automatizada (Requiere Selenium)

Si tienes muchas provincias, puedo crear un script con Selenium que automatice esto, pero requiere:
- `pip install selenium`
- Descargar ChromeDriver o similar

---

## 📝 Provincias pendientes de verificar

| Código | Nombre | Código tabla | Estado |
|--------|--------|--------------|--------|
| 03 | Alicante/Alacant | ❓ | Falta |
| 05 | Ávila | ❓ | Falta |
| 06 | Badajoz | ❓ | Falta |
| 11 | Cádiz | ❓ | Falta |
| 12 | Castellón/Castelló | ❓ | Falta |
| 13 | Ciudad Real | ❓ | Falta |
| 14 | Córdoba | ❓ | Falta |
| 15 | Coruña, A | ❓ | Falta |
| 17 | Girona | ❓ | Falta |
| 18 | Granada | ❓ | Falta |
| 19 | Guadalajara | ❓ | Falta |
| 20 | Gipuzkoa | ❓ | Falta |
| 21 | Huelva | ❓ | Falta |
| 22 | Huesca | ❓ | Falta |
| 23 | Jaén | ❓ | Falta |
| 24 | León | ❓ | Falta |
| 25 | Lleida | ❓ | Falta |
| 26 | Rioja, La | ❓ | Falta |
| 27 | Lugo | ❓ | Falta |
| 29 | Málaga | ❓ | Falta |
| 30 | Murcia | ❓ | Falta |
| 31 | Navarra | ❓ | Falta |
| 32 | Ourense | ❓ | Falta |
| 33 | Asturias | ❓ | Falta |
| 34 | Palencia | ❓ | Falta |
| 35 | Palmas, Las | ❓ | Falta |
| 36 | Pontevedra | ❓ | Falta |
| 37 | Salamanca | ❓ | Falta |
| 38 | Santa Cruz de Tenerife | ❓ | Falta |
| 39 | Cantabria | ❓ | Falta |
| 40 | Segovia | ❓ | Falta |
| 41 | Sevilla | ❓ | Falta |
| 42 | Soria | ❓ | Falta |
| 43 | Tarragona | ❓ | Falta |
| 44 | Teruel | ❓ | Falta |
| 49 | Zamora | ❓ | Falta |
| 50 | Zaragoza | ❓ | Falta |
| 51 | Ceuta | ❓ | Falta |
| 52 | Melilla | ❓ | Falta |

---

## ✅ Una vez completados los códigos

Ejecutar:
```powershell
python src\etl\sources\fetch_ine_padron_provincias.py
```

Esto descargará todas las 52 provincias y consolidará ~8,132 municipios.

---

## 🚀 Alternativa rápida (mientras completamos los códigos)

Podemos usar los datos de **ADRH** que ya tenemos descargados. ADRH incluye información de población junto con renta. Verificar:

```powershell
python -c "import pandas as pd; df = pd.read_csv('data_raw/ine/adrh_all_raw.csv'); print('Municipios únicos:', df['municipio'].nunique()); print('Indicadores:', df['indicador'].unique())"
```

Si ADRH tiene población completa, podemos usarlo como fuente primaria y el Padrón como secundaria/complementaria.
