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
[Valor Tasado de la vivienda libre](https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=35000000)


## Otros trabajos academicos:
1. **Antipov & Pokryshevskaya (2012)**  
*Mass appraisal of residential apartments: An application of Random Forest for valuation and a CART-based approach for model diagnostics*  
[https://doi.org/10.1016/j.exger.2012.03.004](https://doi.org/10.1016/j.exger.2012.03.004)

2. **Park & Bae (2015)**  
*Using machine learning algorithms for housing price prediction: The case of Fairfax County, Virginia housing data*  
[https://link.springer.com/chapter/10.1007/978-3-319-11599-3_26](https://link.springer.com/chapter/10.1007/978-3-319-11599-3_26)

3. **Wu & Brynjolfsson (2015)**  
*The Future of Prediction: How Google Searches Foreshadow Housing Prices and Sales*  
[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2022293](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2022293) -> searchFreq es una variable interesante, índices de búsquedas en Google Trends para categorías tipo “Real Estate Agencies”, “Real Estate Listings” y frases tipo “housing sales”, etc.

4. **Beimer & Francke (2019)**  
*Out-of-sample house price prediction by hedonic price models and machine learning algorithms*  
[https://doi.org/10.1016/j.regsciurbeco.2019.103451](https://doi.org/10.1016/j.regsciurbeco.2019.103451)

5. **Mora García et al. (2022)**  
*Housing price prediction using machine learning algorithms in COVID-19 times*  
[https://doi.org/10.1016/j.heliyon.2022.e09074](https://doi.org/10.1016/j.heliyon.2022.e09074) -> Location & environment Distancia al centro, distancia a la costa/playa.

6. **Fu (2024)**  
*A comparative study of house price prediction using Linear Regression and Random Forest models*  
[https://arxiv.org/abs/2402.05123](https://arxiv.org/abs/2402.05123)

7. **Jin et al. (2024)**  
*Understanding the effects of socioeconomic factors on housing price appreciation using explainable AI*  
[https://doi.org/10.1016/j.landusepol.2023.106559](https://doi.org/10.1016/j.landusepol.2023.106559) -> Renta per cápita / por declarante, Nivel educativo (% población con estudios universitarios, % sin estudios), Estructura demográfica, Estructura sectorial, Turismo.

## Datos/variables a estudiar, su referencia o paper y su fuente de obtención
- 1.1 % de viviendas en bloques de pisos vs unifamiliares de Antipov & Pokryshevskaya, Beimer & Francke y Mora-García et al.
- 
