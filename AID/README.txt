Scripts para el Trabajo Final de Análisis Inteligente de Datos

Para ejecutar el script, deben instalarse previamente las librerías:
+ hdt,
+ Pandas.

Luego, debe descargarse y descomprimirse el archivo HDT con la DB dbpedia desde
https://wiki.dbpedia.org/data-set-38.

Por último se debe ejecutar el script script-ds.py, debiendo modificar los
siguientes parámetros (variables) en el archivos settings.py o crear un archivo
settings_local.py y sobrescribirlas:

- HDT_FILE: con el path al archivo HDT.
- OUTPUT_DATASET_FILE: con el path de destino del dataset resultado.
- RATIO: con la proporción (0-1) de missing values a partir de la cual se eliminan las filas/columnas.
- QUERY: con el recurso IRI que se desea consultar para el relevamiento del dataset.


Juan Manuel Fernandez
