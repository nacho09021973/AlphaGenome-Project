# Proyecto AlphaGenome - Análisis Gen COMT (Fernando)

Este repositorio contiene la estructura de archivos y scripts para realizar inferencias genómicas utilizando la API de **AlphaGenome (v0.5.1)** de Google DeepMind.

## 🎯 Objetivo
Predecir la accesibilidad de cromatina (**ATAC**) y la expresión génica (**RNA_SEQ**) del gen **COMT** (Cromosoma 22) utilizando una secuencia personalizada de un informe de 23andMe (secuencia de Fernando).

## 📂 Archivos clave
- `src/alphagenome/data/ontology.py`: Definición de la clase `OntologyTerm` (punto crítico de error).
- `analisis_comt_final_v14.py`: Último script intentado.
- `instrucciones.json`: Guía oficial de comandos esenciales de AlphaGenome.

## 🛑 Estado actual y Errores
Hemos superado los errores de conexión gRPC (404), pero estamos bloqueados en la instanciación de los parámetros biológicos.

### Último Error detectado:
`TypeError: OntologyTerm.__init__() missing 1 required positional argument: 'type'`

### Intentos fallidos en `OntologyTerm`:
1. `OntologyTerm(id='')` -> Falla por falta de 'type'.
2. `OntologyTerm(term_id='')` -> Falla porque el argumento se llama 'id'.

## 🛠 Instrucciones para Claude/Asistente:
Por favor, analiza el archivo `src/alphagenome/data/ontology.py` para determinar el orden exacto de los argumentos del constructor `__init__` de la clase `OntologyTerm`. 
Necesitamos construir una petición válida para `client.predict_sequence` que incluya:
- `sequence`: (Fragmento de 131,072 bp).
- `requested_outputs`: [ATAC, RNA_SEQ].
- `ontology_terms`: Una lista con al menos un término válido (probablemente requiere un `OntologyType`).

**Nota:** Los archivos `.fasta` y `.txt` no se han subido por razones de peso y privacidad.