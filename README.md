# Proyecto AlphaGenome - Análisis Gen COMT (Fernando)

Este repositorio contiene la estructura de archivos y scripts para realizar inferencias genómicas utilizando la API de **AlphaGenome (v0.5.1)** de Google DeepMind.

## 🎯 Objetivo
Predecir la accesibilidad de cromatina (**ATAC**) y la expresión génica (**RNA_SEQ**) del gen **COMT** (Cromosoma 22) utilizando una secuencia personalizada de un informe de 23andMe (secuencia de Fernando).

## 📂 Archivos clave
- `src/alphagenome/data/ontology.py`: Definición de la clase `OntologyTerm` (punto crítico de error).
- `analisis_comt_final_v14.py`: Último script intentado.
- `instrucciones.json`: Guía oficial de comandos esenciales de AlphaGenome.

## 🛑 Estado actual y Errores (RESUELTO)

### Problema resuelto:
La firma correcta de `OntologyTerm` es:
```python
OntologyTerm(type: OntologyType, id: int)
```

### OntologyType Enum Values:
| Enum | Valor | Descripcion |
|------|-------|-------------|
| `OntologyType.CLO` | 1 | Cell Line Ontology |
| `OntologyType.UBERON` | 2 | Uber-anatomy ontology |
| `OntologyType.CL` | 3 | Cell Ontology |
| `OntologyType.EFO` | 4 | Experimental Factor Ontology |
| `OntologyType.NTR` | 5 | New Term Requested |

### Conversion de CURIE a OntologyTerm:
```python
# 'UBERON:0002048' (Lung) -> OntologyTerm(OntologyType.UBERON, 2048)
# 'CL:0000084' (T-cell)   -> OntologyTerm(OntologyType.CL, 84)
# 'EFO:0002067' (K562)    -> OntologyTerm(OntologyType.EFO, 2067)

from alphagenome.data.ontology import OntologyTerm, OntologyType

terminos_bio = [
    OntologyTerm(OntologyType.UBERON, 955),  # Brain (UBERON:0000955)
]
```

## 🛠 Solucion implementada:
Ver archivo `analisis_comt_final_v15.py` con la llamada correcta:
```python
prediction = client.predict_sequence(
    sequence=fragmento,
    requested_outputs=[dna_output.OutputType.ATAC, dna_output.OutputType.RNA_SEQ],
    ontology_terms=[OntologyTerm(OntologyType.UBERON, 955)]  # Brain
)
```

---

## 🚨 Error 404 UNIMPLEMENTED (gRPC) - RESUELTO en v16

### Problema:
El error `StatusCode.UNIMPLEMENTED - Received http2 header with status: 404` era causado por usar el **endpoint incorrecto**.

### Causa raíz:
| Componente | Script v15 (INCORRECTO) | Librería oficial (CORRECTO) |
|------------|-------------------------|------------------------------|
| **Host** | `alphagenome-api.googleapis.com:443` | `gdmscience.googleapis.com:443` |
| **Service Path** | N/A | `/google.gdm.gdmscience.alphagenome.v1main.DnaModelService/` |

### Solución (v16):
Usar `dna_client.create()` que configura el endpoint correcto automáticamente:

```python
from alphagenome.models import dna_client

# CORRECTO - usa gdmscience.googleapis.com internamente
client = dna_client.create(api_key=API_KEY, timeout=30.0)
```

**NO usar** configuración manual del canal con `alphagenome-api.googleapis.com`.

### Archivos actualizados:
- `analisis_comt_final_v16.py` - Script corregido con endpoint correcto
- `diagnostico_grpc.py` - Script de diagnóstico para verificar conectividad

---

**Nota:** Los archivos `.fasta` y `.txt` no se han subido por razones de peso y privacidad.