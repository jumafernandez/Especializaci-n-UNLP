Scripts para el Trabajo Final de Análisis Inteligente de Datos

Para ejecutar el script, deben instalarse previamente las librerías:
+ pyHDT,
+ Pandas.

Luego, debe descargarse y descomprimirse el archivo HDT con la DB dbpedia desde https://wiki.dbpedia.org/data-set-38.

Por último se debe ejecutar el script script-ds.py, debiendo modificar los siguientes parámetros (variables):
- directorio: con el directorio donde se descargaron los scripts.
- archivo_ds: con el path de destino del dataset resultado.
- file_hdt: con el path al archivo HDT.
- proporcion: con la proporción (0-1) de missing values a partir de la cual se eliminan las filas/columnas.
- consulta: con el recurso IRI que se desea consultar para el relevamiento del dataset.


Juan Manuel Fernandez
