#%% Bloque de carga de datos
# Load an HDT file. Missing indexes are generated automatically
from hdt import HDTDocument
from functions import get_sujeto_atr, get_predicado_atr, get_objeto_atr 
import pandas as pd

# Definición del directorio del archivo HDT y creación del HDTDocument
file_hdt = "/media/juan/12941B31941B16B7/Users/unlu/Google Drive/PC-Juan/Docencia  & Investigacion/Cursos-Especializacion/Captura y Almacenamiento de Información/utiles/dbpedia-3.8-en.hdt"
document = HDTDocument(file_hdt)

# Inicialización
directorio = "/home/juan/Escritorio/AID-BD/"
archivo_ds = open("/home/juan/Escritorio/AID-BD/csv/dataset.csv", "w")
archivo_estadistica = open("/home/juan/Escritorio/AID-BD/csv/estadistica.csv", "w")
sep=";"
archivo_ds.write("sujeto"+sep+"predicado"+sep+"objeto\n")
archivo_estadistica.write("objeto"+sep+"atributos_finales"+sep+"atributos_originales\n")

#%% Consulta
# Ontología: http://mappings.dbpedia.org/server/ontology/classes/
#consulta = "http://dbpedia.org/ontology/University"
#consulta = "http://dbpedia.org/ontology/Film"
consulta = "http://dbpedia.org/ontology/Actor"
#consulta = "http://dbpedia.org/ontology/HistoricPlace"

# Proporcion Faltantes, se eliminan los que no tengan esta cota minima de datos:
proporcion=0.3

# Se hace la consulta de los triples en funcion del sujeto/predicado/objeto
(triples, cardinality) = document.search_triples("", "", consulta)

print(consulta + ": " + str(cardinality) + " objetos.")
#%% Procesamiento
# triple = s p o
lista_objetos = []
for triple in triples:
    s = triple[0]
    p = triple[1]
    o = triple[2]
    sujeto_descripcion, sujeto_URI = get_sujeto_atr(s)
    lista_objetos.append(sujeto_URI.replace('"', ""))

numero=0
for sujeto_URI in lista_objetos:
    (atributos, cantidad) = document.search_triples(sujeto_URI, "", "")
    sujeto_descripcion, sujeto_URI = get_sujeto_atr(sujeto_URI)
    cantidad_atributos=0
    print(str(numero) + ':' + sujeto_descripcion)
    numero+=1
    for atr in atributos:
        # Levanto los atributos/subgrafos
        atr_sujeto = atr[0]
        atr_predicado = atr[1]
        atr_objeto = atr[2]
        nombre_objeto=sujeto_descripcion

        # Parseo cada subgrafo que contiene el objeto buscado para obetner los atributos
        predicado_descripcion, predicado_URI = get_predicado_atr(atr_predicado)
        objeto_descripcion, objeto_URI, objeto_valor, objeto_tipo, objeto_literal = get_objeto_atr(atr_objeto)
        
        # Vamos a definir una lista con los predicados que no nos interesan
        predicados_desechables = ["abstract", "thumbnail", "wikiPageExternalLink", "wikiPageExternalLink", "wikiPageID", "wikiPageInterLanguageLink", "wikiPageRevisionID", "wikiPageWikiLink", "website", "wikiPageUsesTemplate", "Template:Infobox_university", "owl#sameAs", "prov#wasDerivedFrom", "depiction", "homepage", "isPrimaryTopicOf", "imageName", "imageSize", "title", "titlestyle", "Template:Infobox_US_university_ranking", "Template:Navboxes", "subject", "point", "rdf-schema#comment", "rdf-schema#label"]
        # Luego buscamos si el predicado se encuentra en esa lista, si está no lo guardamos
        predicado_importante=True
        for termino in predicados_desechables:
            if termino in predicado_descripcion:
                predicado_importante=False
        
        if predicado_importante:
            if predicado_descripcion.find("Template:")!=-1:
                predicado_importante=False
    
        # Si es un predicado importante lo guardamos
        if predicado_importante:
            cantidad_atributos+=1
            if not(objeto_literal):
                archivo_ds.write(sujeto_descripcion + sep + predicado_descripcion + sep + str(objeto_descripcion) + "\n")
#                df_rdf=df_rdf.append({'sujeto': sujeto_descripcion, 'predicado': predicado_descripcion, 'objeto': objeto_descripcion}, ignore_index=True)
#                if predicado_descripcion=="name":
#                    nombre_objeto=objeto_descripcion
            else:
                archivo_ds.write(sujeto_descripcion + sep + predicado_descripcion + sep + str(objeto_valor) + "\n")
#                df_rdf=df_rdf.append({'sujeto': sujeto_descripcion, 'predicado': predicado_descripcion, 'objeto': objeto_valor}, ignore_index=True)
#                if predicado_descripcion=="name":
#                        nombre_objeto=objeto_valor
                        
    # Cambio la descripción del recurso por el nombre del objeto en caso que exista ese atributo para ese sujeto
#    if nombre_objeto!=sujeto_descripcion:
#        df_rdf=df_rdf.replace(sujeto_descripcion, nombre_objeto)
        
#    print(nombre_objeto + ": " + str(cantidad) + "/" + str(cantidad_atributos) + " atributos")
    archivo_estadistica.write(nombre_objeto + sep + str(cantidad_atributos) + sep + str(cantidad) + "\n")

archivo_estadistica.close()
archivo_ds.close()

#%% Se levanta el dataset del csv
df_rdf = pd.read_csv("/home/juan/Escritorio/AID-BD/csv/dataset.csv", sep=";")

#%% Preparación para el pivoteo del dataframe

# Trabajo en pivotear el dataframe para que me quede con formato dataset
# Genero un numero de nivel para cada predicado -por los predicados repetidos-
df_rdf['nivel_atributo'] = df_rdf.groupby(['sujeto', 'predicado']).cumcount()
# Concateno al predicado el nivel así unifico el nombre del predicado para el objeto
df_rdf['atributo']=df_rdf['predicado']+"_"+df_rdf['nivel_atributo'].map(str)
# Elimino las columnas que sobran
df_rdf = df_rdf.drop(columns=["nivel_atributo", 'predicado'])
# Pivoteo el dataframe
dataset=df_rdf.pivot(index='sujeto', columns='atributo', values='objeto')

#%% Eliminación de filas y columnas con missings
###############################################

filas_minimas=int(len(dataset.index)*proporcion)
# Se borran las columnas
columnas_minimas=int(len(dataset.columns)*proporcion)
dataset=dataset.dropna(thresh=filas_minimas, axis=1)
# Se borran las filas
columnas_minimas=int(len(dataset.columns)*proporcion)
dataset=dataset.dropna(thresh=columnas_minimas, axis=0)

# Se guarda el dataset
dataset.to_csv("/home/juan/Escritorio/AID-BD/csv/dataset-final.csv", index = None, header=True, sep=";")
#%% Se muestran los resultados
objeto_descripcion, objeto_URI, objeto_valor, objeto_tipo, objeto_literal = get_objeto_atr(consulta)
print("###### RESULTADOS #########")
print("Objeto consultado: " + objeto_descripcion)
print("Registros: " + str(len(dataset.index)))
print("Atributos: " + str(len(dataset.columns)))
print("Proporcion de missings: "+str(dataset.isnull().sum(axis=0).mean()/len(dataset.index)*100))
print("##### FIN RESULTADOS #####")
