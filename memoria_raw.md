- Busco posibles fuentes de datos de todo tipo. Comienzo comenzando por los datos de sitios de compraventa al estilo idealista.
- Exploro un script de Python para la extracción de información de un archivo de audio. Lo modifico para camuflarlo como un browser normal y no denieguen las peticiones, además de actualizarlo según el nuevo layout de idealista.
- Exploro datasets y metodologías de otros trabajos similares como el de [https://www.kaggle.com/datasets/thedevastator/spanish-housing-dataset-location-size-price-and/data](https://www.kaggle.com/datasets/thedevastator/spanish-housing-dataset-location-size-price-and/data). Creo un script para limpiar un poco los datos y eliminar duplicidades.
- Reestructuro los archivos.
- Me reuno con Icíar para hablar del anteproyecto y de las futuras metas a largo plazo/enfoques para el proyecto (reflejado en el TODO). 
- Genero el anteproyecto 
- exploro multiples estudios del INE y su metodología en distintos estadísticos. Me centro en [monthly basis information on the number of
transfers of rights on property](https://www.ine.es/en/metodologia/t30/t3030168_en.pdf), el cual me acaba llevando al registro mercantil y tras una bue exploración: [Datos de Open Data de los Registradores de España](https://opendata.registradores.org/compraventas-de-inmuebles). Obtengo unos 5000 datos del registro con un intervalo temporal del 2007 a 2024 y a lo largo de todo el territorio español.

- Cambio la estructura/esqueleto general del proyecto para acercarlo al release final. Replanteo el proyecto para centrarme en un posible despliegue más aplicado al big data, y la creación de un mapa de calor basado en h3 r7

- Me centro en crear un ´data lake´ y busco distintas fuentes de datos. Creo un pequeño generador de datos como demo.


## Bibliografia
[Datos padron](https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225)
[Atlas de Distribucion de Renta de los Hogares](https://www.ine.es/ADRH/?config=config_ADRH_2023.json&showLayers=ADRH_2023_Renta_media_por_persona_cache&level=5)