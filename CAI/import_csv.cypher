// 1. Copiamos los archivos a importar al directorio /var/lib/neo4j/import/
// sudo cp /home/juan/Escritorio/CAI-scripts/sujetos.csv /var/lib/neo4j/import/

// 2. En el browser de Ne4j
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///objetos.csv" AS row
CREATE (:Sujeto {URI: row.URI, descripcion: row.descripcion});

CREATE INDEX ON :Sujeto(URI);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///literales.csv" AS row
CREATE (:Literal {name: row.descripcion});

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///predicados.csv" AS row
MATCH (sujeto:Sujeto {sujetoID: row.URI_sujeto})
MATCH (objeto:Sujeto {objetoID: row.URI_objeto})
MERGE (sujeto)-[:PREDICADO]->(objeto);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///predicados.csv" AS row
CREATE (:Predicado {name: row.descripcion, sujeto:row.URI_sujeto, URI: row.URI, objeto: row.URI_objeto});

CREATE INDEX ON :Predicado(sujeto, URI, objeto);


sudo neo4j-admin import --database=juancho.db --nodes=/var/lib/neo4j/import/sujetos.csv --nodes=/var/lib/neo4j/import/literales.csv --ignore-duplicate-nodes
sudo neo4j start

sudo neo4j-admin import --database=completa.db --nodes="/var/lib/neo4j/import/csv/sujetos.csv,/var/lib/neo4j/import/csv/literales.csv"  --ignore-duplicate-nodes --relationships="/var/lib/neo4j/import/csv/predicados-sujeto-sujeto.csv,/var/lib/neo4j/import/csv/predicados-sujeto-literal.csv" --ignore-missing-nodes

sudo neo4j-admin import --database=completa.db --nodes="/var/lib/neo4j/import/csv/sujetos.csv,/var/lib/neo4j/import/csv/literales.csv"  --ignore-duplicate-nodes --relationships="/var/lib/neo4j/import/csv/predicados.csv" --ignore-missing-nodes

sudo neo4j-admin import --database=completa1.db --nodes="/var/lib/neo4j/import/csv/sujetos.csv" --nodes="/var/lib/neo4j/import/csv/literales.csv" --relationships="/var/lib/neo4j/import/csv/predicados.csv"  --ignore-duplicate-nodes --ignore-missing-nodes --multiline-fields=true

