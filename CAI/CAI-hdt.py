#%% Bloque de carga de datos
# Load an HDT file. Missing indexes are generated automatically
from hdt import HDTDocument
from time import time

# import the neo4j driver for Python
from py2neo import  Graph, Node, Relationship

# Definición del directorio del archivo HDT y creación del HDTDocument
file_hdt = "/media/juan/12941B31941B16B7/Users/unlu/Google Drive/PC-Juan/Docencia  & Investigacion/Cursos-Especializacion/Captura y Almacenamiento de Información/utiles/dbpedia-3.8-en.hdt"
document = HDTDocument(file_hdt)

# Definición del grafo
graph = Graph("http://localhost:7474/db/data/", user="neo4j", password="888888")
graph.delete_all()
tx=graph.begin()

#%% Bloque display de triples

# Display some metadata about the HDT document itself
print("nb triples: %i" % document.total_triples)
print("nb subjects: %i" % document.nb_subjects)
print("nb predicates: %i" % document.nb_predicates)
print("nb objects: %i" % document.nb_objects)
print("nb shared subject-object: %i" % document.nb_shared)


#%% Inicialización

# Se instancian los archivos de logs
archivo_triples = open("/home/juan/Escritorio/CAI-scripts/triples-rdf.txt", "w")
archivo_tiempo = open("/home/juan/Escritorio/CAI-scripts/medicion-ejecucion.txt", "w")

# Se inicializan las variables
tiempo_anterior = time()
BANDERA_PRINT=10000
cantidad_registros=0
lista_nodos = []
lista_uris = []

# Se hace la consulta de los triples en funcion del sujeto/predicado/objeto

# Prueba con Lionel_Messi
# (triples, cardinality) = document.search_triples("http://dbpedia.org/resource/Lionel_Messi", "", "")

(triples, cardinality) = document.search_triples("", "", "")

#(triples, cardinality) = document.search_triples("", "", "")
print("cardinality of { ?s ?p ?o }: %i" % cardinality)

#%% Procesamiento

for triple in triples:
    # Tomo solo el texto y el URI del sujeto-predicado-objeto
    #print(triple)

    # Se parsea el sujeto que siempre es como: http://dbpedia.org/resource/Lionel_Messi
    # sujeto_descripcion=Lionel_Messi
    sujeto_descripcion = triple[0].split("/")[len(triple[0].split("/"))-1]
    # URI=http://dbpedia.org/resource/Lionel_Messi
    sujeto_URI = triple[0]
    
    # Se parsea el predicado, que siempre es: http://xmlns.com/foaf/0.1/surname
    #predicado_descripcion=surname
    predicado_descripcion = triple[1].split("/")[len(triple[1].split("/"))-1]
    #predicado_URI=http://xmlns.com/foaf/0.1/surname
    predicado_URI = triple[1]
    
    # Al objeto le hago un parseo especial, verifico si es un URI o no
    # Si no es un URI, asumo que es un literal y debo sacar el tipo de dato
    if triple[2].find("http://")==0 and len(triple[2])<=50:
        objeto_descripcion = triple[2].split("/")[len(triple[2].split("/"))-1]
        objeto_tipo = None
        objeto_URI = triple[2]
    else:
        objeto_descripcion = triple[2]
        objeto_tipo = None
        objeto_URI = None

    # Vamos a definir una lista con los predicados que no nos interesan
    predicados_desechables = ["wikiPage", "Template", "owl#sameAs", "rdf-schema", "subject", "thumbnail", "22-rdf-syntax", "depiction"]
    # Luego buscamos si el predicado se encuentra en esa lista, si está no lo guardamos
    predicado_importante=True
    for termino in predicados_desechables:
        if termino in predicado_descripcion:
            predicado_importante=False
  
    # Si es un predicado importante lo guardamos
    if predicado_importante:
        archivo_triples.write(sujeto_descripcion + "->" + predicado_descripcion + "->" + objeto_descripcion + '\n')
#        print(sujeto_descripcion + " " + predicado_descripcion + ": " + objeto_descripcion + '\n')
        cantidad_registros+=1

        # Me fijo si existe el nodo, sino lo creo. Si existe será el nodo que incorpore
        if sujeto_URI not in lista_uris:
            Nodo_sujeto = Node("Sujeto", descripcion=sujeto_descripcion, URI=sujeto_URI)
            lista_uris.append(sujeto_URI)
            lista_nodos.append(Nodo_sujeto)
        else:
            Nodo_sujeto = lista_nodos[lista_uris.index(sujeto_URI)]
    
        # Me fijo si el objeto es un literal o un URI, si es un URI hago el mismo chequeo
        if objeto_URI:
            if objeto_URI not in lista_uris:
                Nodo_objeto = Node("Sujeto", descripcion=objeto_descripcion, tipo=objeto_tipo, URI=objeto_URI)
                lista_uris.append(objeto_URI)
                lista_nodos.append(Nodo_objeto)
            else:
                Nodo_objeto = lista_nodos[lista_uris.index(objeto_URI)]
        else:
            Nodo_objeto = Node("Literal", descripcion=objeto_descripcion, tipo=objeto_tipo, URI=objeto_URI)
        # Guardo los objetos en el grafo
        Arista_predicado = Relationship(Nodo_sujeto, "predicado" , Nodo_objeto, descripcion=predicado_descripcion)
        tx.create(Arista_predicado)
       
#        print("Cantidad de registros procesados ", cantidad_registros)
        if cantidad_registros % BANDERA_PRINT == 0:
            tiempo_actual=time()
            tiempo_procesamiento = tiempo_actual-tiempo_anterior
            tiempo_anterior=tiempo_actual
            texto=str(cantidad_registros) + " de registros procesados en " + str(tiempo_procesamiento) + '\n'
            archivo_tiempo.write(texto)
            print(texto)
            tx.commit()
            tx=graph.begin()

#        archivo.write(triple[1] + ": " + triple[2] + '\n')
    
print("Cantidad de registros encontrados: ", cantidad_registros)
archivo_triples.close() 
archivo_tiempo.close()

#%% Borrar grafo
#graph.delete_all()    
    
#%%