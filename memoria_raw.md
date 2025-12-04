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
[Datos padron](https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225) (Para estudiar las variaciones de la poblacion por año)

[Atlas de Distribucion de Renta de los Hogares](https://www.ine.es/ADRH/?config=config_ADRH_2023.json&showLayers=ADRH_2023_Renta_media_por_persona_cache&level=5) (Mora García et al. (2022), Jin et al. (2024))

[Valor Tasado de la vivienda libre](https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=35000000) (Jin et al. (2024))

[Encuesta de Características Esenciales de la Población y las Viviendas. Resultados](https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177092&menu=resultados&idp=1254735572981)

[Etadisticas de Catastro](https://www.catastro.hacienda.gob.es/esp/estadisticas.asp)

[Edificios destinados principal o exclusivamente a viviendas y nº de inmuebles por municipios (con más de 2.000 habitantes), instalaciones del edificio y nº de plantas sobre rasante](https://www.ine.es/jaxi/Tabla.htm?path=/t20/e244/edificios/p04/l0/&file=5mun00.px&L=0) (Mora García et al. (2022) tiene en cuenta si hay ascensor en los edificios)

[Situación del hogar y superficie útil](https://www.ine.es/dynt3/inebase/index.htm?padre=8981&capsel=8981) 

[Superficie por ingreso neto](https://www.ine.es/dynt3/inebase/index.htm?padre=8981&capsel=8981)

[ADRH (Renta)](https://www.ine.es/ADRH/?config=config_ADRH_2023.json&showLayers=ADRH_2023_Renta_media_por_hogar_cache&level=5) (Mora García et al. (2022), Jin et al. (2024))

[Viviendas principales según número de cuartos de baño o aseos por tipo de edificio y año de construcción](https://www.ine.es/jaxi/Tabla.htm?tpx=56866&L=0) (Antipov & Pokryshevskaya, Fu (2024), Mora García et al. (2022))

[Viviendas principales según número de cuartos de baño o aseos por superficie útil de la vivienda y tamaño del municipio.](https://www.ine.es/jaxi/Tabla.htm?tpx=56837&L=0) (Antipov & Pokryshevskaya, Fu (2024), Mora García et al. (2022))

[Población por sexo, edad y nacionalidad](https://www.ine.es/dynt3/inebase/index.htm?padre=11555&capsel=11398) (Jin et al. (2024))

[Compraventa de viviendas (volumen) según régimen y estado](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736171438&menu=resultados&idp=1254735576757#_tabs-1254736171259) (Wu & Brynjolfsson (2015), Beimer & Francke (2019) y Park & Bae (2015))

[Paro municipal por mes y sexo](https://www.sepe.es/HomeSepe/es/que-es-el-sepe/estadisticas/datos-estadisticos.html)(Varios estudios incluyen variales económicas, macro y micro: Park & Bae (2015), Wu & Brynjolfsson (2015) y Jin et al. (2024)). Esta generado con el fetcher de fetch_sepe_paro_all.py 

[Banco de España. Tipos de interés](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv)(Varios estudios incluyen variales económicas, macro y micro: Park & Bae (2015), Wu & Brynjolfsson (2015) y Jin et al. (2024)). Descargado con el fetcher

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
