#!/usr/bin/env python
"""
Estrategia alternativa: Navegar directamente a cada tabla provincial
y extraer el código desde la URL de descarga.

Basándonos en el patrón:
- Albacete (02): https://www.ine.es/jaxiT3/Tabla.htm?t=33582
- Madrid (28): https://www.ine.es/jaxiT3/Tabla.htm?t=33847

Vamos a probar rangos de códigos de tabla alrededor de los valores conocidos.
