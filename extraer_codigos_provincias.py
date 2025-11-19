#!/usr/bin/env python
"""
Extrae los códigos de tabla del Padrón por provincia desde la página del INE.

Fuente: https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225
"""
import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225"

print("📥 Descargando página del INE...")
r = requests.get(url, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.content, 'html.parser')

# Buscar todos los enlaces de descarga (icono ii-download)
enlaces_descarga = soup.find_all('a', href=re.compile(r'dlgExport\.htm\?t=\d+'))

print(f"✅ Encontrados {len(enlaces_descarga)} enlaces de descarga\n")

provincias = {}

for enlace in enlaces_descarga:
    href = enlace.get('href')
    
    # Extraer código de tabla
    match = re.search(r't=(\d+)', href)
    if not match:
        continue
    
    codigo_tabla = match.group(1)
    
    # Buscar el nombre de la provincia (está en un elemento anterior)
    # Navegar hacia atrás en el HTML para encontrar el nombre
    parent = enlace.find_parent('li')
    if parent:
        # Buscar el texto que contiene el nombre de la provincia
        texto = parent.get_text(strip=True)
        
        # El nombre suele estar en un elemento anterior
        # Intentar encontrar un <a> o <span> con el nombre
        nombre_elem = parent.find_previous('a', class_=lambda c: c != 'thickbox' if c else True)
        if nombre_elem:
            nombre = nombre_elem.get_text(strip=True)
            
            # Limpiar el nombre (quitar números finales que son códigos)
            nombre = re.sub(r'\s+\d+$', '', nombre)
            
            print(f"Tabla {codigo_tabla}: {nombre}")
            provincias[codigo_tabla] = nombre

print(f"\n📊 Total provincias encontradas: {len(provincias)}")

# Guardar en JSON para fácil importación
output = {
    "provincias": provincias,
    "total": len(provincias)
}

with open('provincias_tablas.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Guardado en: provincias_tablas.json")
