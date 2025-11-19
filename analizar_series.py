#!/usr/bin/env python
"""
Análisis de las 29,376 series: ¿Son todas de A Coruña o hay más?
"""
import requests
import re
from collections import Counter

print("Descargando series...")
url = "https://servicios.ine.es/wstempus/js/es/SERIES_TABLA/33775"
r = requests.get(url, timeout=60)
series = r.json()

print(f"Total series: {len(series)}")

# Extraer nombres de provincias/municipios de los nombres de las series
provincias = []
municipios = []

for s in series:
    nombre = s.get('Nombre', '')
    
    # Los nombres suelen tener formato: "Dato base. Sexo. Provincia/Municipio. Edad."
    # Extraer la parte del municipio/provincia
    partes = nombre.split('.')
    if len(partes) >= 3:
        lugar = partes[2].strip()
        
        # Detectar si es provincia o municipio
        # Códigos de provincia son 2 dígitos, municipios 5
        codigo_match = re.search(r'\b(\d{2,5})\b', lugar)
        if codigo_match:
            codigo = codigo_match.group(1)
            if len(codigo) == 2:
                provincias.append((codigo, lugar))
            elif len(codigo) == 5:
                municipios.append((codigo, lugar))
        else:
            # Sin código, buscar nombres conocidos
            if 'Coruña' in lugar or 'A Coruña' in lugar:
                provincias.append(('15', lugar))
            else:
                municipios.append((None, lugar))

print(f"\nProvincias detectadas: {len(set(provincias))}")
print(f"Municipios detectados: {len(set(municipios))}")

# Contar frecuencias
if municipios:
    codigos_muni = [m[0][:2] if m[0] and len(m[0]) >= 2 else None for m in municipios]
    codigos_prov = Counter(codigos_muni)
    print(f"\nProvincias en municipios (por código):")
    for prov, count in codigos_prov.most_common(10):
        print(f"   {prov}: {count} series")

# Mostrar ejemplos de nombres
print(f"\nEjemplos de nombres de series (primeras 10):")
for s in series[:10]:
    print(f"   {s['Nombre']}")

# Buscar si hay patrón ID que identifique provincia
print(f"\nAnalizando patrones en COD/Id...")
cods = [s.get('COD', '') for s in series[:100]]
print(f"Primeros 10 CODs:")
for cod in cods[:10]:
    print(f"   {cod}")
