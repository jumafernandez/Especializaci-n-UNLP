#%% Bloque de carga de datos
# Load an HDT file. Missing indexes are generated automatically
from hdt import HDTDocument
from time import time

# import the neo4j driver for Python
# from py2neo import  Graph, Node, Relationship

# Definición del directorio del archivo HDT y creación del HDTDocument
file_hdt = "/media/juan/12941B31941B16B7/Users/unlu/Google Drive/PC-Juan/Docencia  & Investigacion/Cursos-Especializacion/Captura y Almacenamiento de Información/utiles/dbpedia-3.8-en.hdt"
document = HDTDocument(file_hdt)

#%% Inicialización

# Se instancian los archivos de logs
archivo_tiempo = open("/home/juan/Escritorio/CAI-scripts/medicion-ejecucion.txt", "w")

# Inicializo el archivo de sujetos
archivo_sujetos_csv = open("/home/juan/Escritorio/CAI-scripts/csv/sujetos.csv", "w")
archivo_sujetos_csv.write("URI:ID, name, Sujeto:LABEL" + '\n')
# Inicializo el archivo de predicados
archivo_predicados_csv = open("/home/juan/Escritorio/CAI-scripts/csv/predicados.csv", "w")
archivo_predicados_csv.write("URI_sujeto:START_ID" + ", " + "URI" + ", " + "descripcion:TYPE" + ", " + "URI_objeto:END_ID" + '\n')
# Inicializo el archivo de literales
archivo_literales_csv = open("/home/juan/Escritorio/CAI-scripts/csv/literales.csv", "w")
archivo_literales_csv.write("URI:ID, valor, tipo, Literal:LABEL" + '\n')

# Se inicializan las variables
tiempo_anterior = time()
BANDERA_PRINT=1000000
cantidad_registros=0
lista_nodos = []
lista_uris = []

# Se hace la consulta de los triples en funcion del sujeto/predicado/objeto
# Prueba con Lionel_Messi
# (triples, cardinality) = document.search_triples("http://dbpedia.org/resource/Lionel_Messi", "", "")
(triples, cardinality) = document.search_triples("", "", "")
print("Cantidad de triples de la consulta { ?s ?p ?o }: %i" % cardinality)

#%% Funciones de parseo

def get_sujeto_atr(text):
    '''Se parsea el sujeto que siempre es como: http://dbpedia.org/resource/Lionel_Messi
        sujeto_descripcion=Lionel_Messi '''
    sujeto_descripcion = text.split("/")[len(text.split("/"))-1]
    # URI=http://dbpedia.org/resource/Lionel_Messi
    sujeto_URI = text
    sujeto_descripcion = '"' + sujeto_descripcion + '"'   
    sujeto_URI = '"' + sujeto_URI + '"'   

    return sujeto_descripcion, sujeto_URI

def get_predicado_atr(text):
    '''Se parsea el predicado, que siempre es: http://xmlns.com/foaf/0.1/surname
    predicado_descripcion=surname'''
    predicado_descripcion = text.split("/")[len(text.split("/"))-1]
    #predicado_URI=http://xmlns.com/foaf/0.1/surname
    predicado_URI = text

    return predicado_descripcion, predicado_URI

def get_objeto_atr(text):
    ''' Al objeto le hago un parseo especial, verifico si es un literal o no
        Si no es un literal, asumo que es un URI '''
    URI = '"' + text.replace('"', '""') + '"'
    # Solo para los objetos que son sujetos
    descripcion = None
    
    # Solo para los objetos que son literales
    valor = None
    tipo = None
  
    # Verifico si es un literal y actuo en consecuencia
    literal = not(text.find("http://")==0 and len(text)<=110)

    if (literal):
        numerico=text.find("^^")!=-1
        texto=text.find("@")!=-1
#        otro_tipo=not(texto or numerico)
        
        if numerico:
            valor = text.split("^^")[0].replace('"', "")
            tipo = '"' + text.split("^^")[1].replace("\n","") + '"' 
        elif texto:
            valor = '"' + text.split("@")[0].replace('"', "") + '"'
            tipo = '"' + text.split("@")[1].replace("\n","") + '"' 
#        elif (otro_tipo):
#            print(text)
    else: # Sino es literal, es URI 
        descripcion, URI = get_sujeto_atr(text)
    
    return descripcion, URI, valor, tipo, literal



#%% Procesamiento
# triple = s p o
for triple in triples:
    s = triple[0]
    p = triple[1]
    o = triple[2]
    sujeto_descripcion, sujeto_URI = get_sujeto_atr(s)
    predicado_descripcion, predicado_URI = get_predicado_atr(p)
    objeto_descripcion, objeto_URI, objeto_valor, objeto_tipo, objeto_literal = get_objeto_atr(o)
            
    # Vamos a definir una lista con los predicados que no nos interesan
    predicados_desechables = ["wikiPage", "Template", "owl#sameAs", "rdf-schema", "subject", "thumbnail", "22-rdf-syntax", "depiction"]
    # Luego buscamos si el predicado se encuentra en esa lista, si está no lo guardamos
    predicado_importante=True
    for termino in predicados_desechables:
        if termino in predicado_descripcion:
            predicado_importante=False
  
    # Si es un predicado importante lo guardamos
    if predicado_importante:
        cantidad_registros+=1

        # Guardo los sujetos
        archivo_sujetos_csv.write(str(sujeto_URI) + ", " + str(sujeto_descripcion) + ", Sujeto" + '\n')
        
        # Guardo los objetos (según sean sujetos o literales)
        if not(objeto_literal): # Objetos
            archivo_sujetos_csv.write(str(objeto_URI) + ", " + str(objeto_descripcion) + ", Sujeto" + '\n')
        else: # Literales
            archivo_literales_csv.write(str(objeto_URI) +  ", " + str(objeto_valor) + ", " + str(objeto_tipo) + ", Literal" + '\n')
       
        # Guardo los predicados
        archivo_predicados_csv.write(str(sujeto_URI) + ", " + str(predicado_URI) + ", " + str(predicado_descripcion) + ", " + str(objeto_URI) + '\n')
        
        # Se computan los tiempos y se guardan las cantidades de registros por tiempo
        if cantidad_registros % BANDERA_PRINT == 0:
            tiempo_actual=time()
            tiempo_procesamiento = tiempo_actual-tiempo_anterior
            tiempo_anterior=tiempo_actual
            texto=str(cantidad_registros) + ": " + str(tiempo_procesamiento) + '\n'
            archivo_tiempo.write(texto)
            print(texto)
   
#%% Se cierran archivos
archivo_tiempo.close()
archivo_sujetos_csv.close()
archivo_predicados_csv.close()
archivo_literales_csv.close()
    
#%%