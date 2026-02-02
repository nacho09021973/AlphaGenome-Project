"""
AlphaGenome Analysis - Gen COMT (Fernando)
Version: 15 (Corregida)
Fecha: 2026-02-02

Correcciones aplicadas:
- OntologyTerm requiere: OntologyTerm(type: OntologyType, id: int)
- type es un valor del enum OntologyType (UBERON, CL, EFO, CLO, NTR)
- id es un entero (no string), extraido del CURIE (ej: 'UBERON:0002048' -> id=2048)
"""

import sys
import grpc

# Configuracion de rutas (ajustar segun tu entorno)
sys.path.append('/home/ignac/Genoma/alphagenome/src')

from alphagenome.models import dna_client
from alphagenome.models import dna_output
from alphagenome.data.ontology import OntologyTerm, OntologyType
from Bio import SeqIO
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURACION
# =============================================================================
API_KEY = 'AIzaSyDLXmTFGqzp73aTl5pZ1CJmySokInyVlsI'

# =============================================================================
# CONEXION gRPC
# =============================================================================
print("Estableciendo conexion gRPC con AlphaGenome API...")
channel = grpc.secure_channel(
    'alphagenome-api.googleapis.com:443',
    grpc.ssl_channel_credentials()
)
client = dna_client.DnaClient(
    channel=channel,
    metadata=(('x-goog-api-key', API_KEY),)
)

# =============================================================================
# TERMINOS ONTOLOGICOS - FIRMA CORRECTA
# =============================================================================
# OntologyTerm(type: OntologyType, id: int)
#
# OntologyType enum values:
#   - OntologyType.CLO    (1) = Cell Line Ontology
#   - OntologyType.UBERON (2) = Uber-anatomy ontology
#   - OntologyType.CL     (3) = Cell Ontology
#   - OntologyType.EFO    (4) = Experimental Factor Ontology
#   - OntologyType.NTR    (5) = New Term Requested
#
# El 'id' es el numero entero del termino CURIE:
#   'UBERON:0002048' (Lung)     -> OntologyTerm(OntologyType.UBERON, 2048)
#   'UBERON:0000955' (Brain)    -> OntologyTerm(OntologyType.UBERON, 955)
#   'CL:0000084' (T-cell)       -> OntologyTerm(OntologyType.CL, 84)
#   'EFO:0002067' (K562 cells)  -> OntologyTerm(OntologyType.EFO, 2067)
# =============================================================================

# Usamos cerebro (UBERON:0000955) como tejido de referencia para COMT
# (COMT tiene alta expresion en sistema nervioso)
terminos_bio = [
    OntologyTerm(OntologyType.UBERON, 955),   # Brain (UBERON:0000955)
]

# Alternativa: usar multiples tejidos para comparacion
# terminos_bio = [
#     OntologyTerm(OntologyType.UBERON, 955),   # Brain
#     OntologyTerm(OntologyType.UBERON, 7844),  # Prefrontal cortex (UBERON:0007844)
#     OntologyTerm(OntologyType.UBERON, 2048),  # Lung (referencia)
# ]

# =============================================================================
# CARGA DE SECUENCIA
# =============================================================================
print("Cargando secuencia personalizada del cromosoma 22...")
record = next(SeqIO.parse("genoma_fernando_chr22.fasta", "fasta"))
secuencia = str(record.seq)

# Ventana del gen COMT (hg38: chr22:19,928,000-19,969,975)
start_pos = 19_928_000
fragmento = secuencia[start_pos : start_pos + 131072]

print(f"Fragmento extraido: {len(fragmento)} bp")
print(f"Region: chr22:{start_pos}-{start_pos + 131072}")

# =============================================================================
# PREDICCION
# =============================================================================
print("Enviando peticion a AlphaGenome...")

try:
    # Llamada con los tres argumentos keyword-only requeridos:
    # - sequence: string de 131,072 bp
    # - requested_outputs: lista de OutputType
    # - ontology_terms: lista de OntologyTerm correctamente construida
    prediction = client.predict_sequence(
        sequence=fragmento,
        requested_outputs=[
            dna_output.OutputType.ATAC,
            dna_output.OutputType.RNA_SEQ
        ],
        ontology_terms=terminos_bio
    )

    print("Prediccion recibida exitosamente!")
    print(f"Numero de tracks recibidos: {len(prediction.tracks)}")

    # =============================================================================
    # VISUALIZACION
    # =============================================================================
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Track de Accesibilidad (ATAC)
    ax1 = axes[0]
    ax1.plot(prediction.tracks[0].values, color='#e63946', linewidth=0.8)
    ax1.fill_between(
        range(len(prediction.tracks[0].values)),
        prediction.tracks[0].values,
        color='#e63946',
        alpha=0.2
    )
    ax1.set_title("Accesibilidad de Cromatina (ATAC) - Gen COMT (Fernando)", fontsize=12)
    ax1.set_ylabel("Senal ATAC")
    ax1.grid(True, alpha=0.3)

    # Track de Expresion (RNA-seq)
    ax2 = axes[1]
    ax2.plot(prediction.tracks[1].values, color='#457b9d', linewidth=0.8)
    ax2.fill_between(
        range(len(prediction.tracks[1].values)),
        prediction.tracks[1].values,
        color='#457b9d',
        alpha=0.2
    )
    ax2.set_title("Prediccion de Expresion (RNA-seq) - Gen COMT (Fernando)", fontsize=12)
    ax2.set_xlabel("Posicion (bp)")
    ax2.set_ylabel("Senal RNA-seq")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = "analisis_COMT_fernando_v15.png"
    plt.savefig(output_file, dpi=150)
    print(f"Grafico guardado: {output_file}")

except Exception as e:
    print(f"Error durante la inferencia: {e}")
    print("\nSugerencias de depuracion:")
    print("1. Verifica que la API key sea valida")
    print("2. Confirma que el archivo FASTA existe y tiene la secuencia")
    print("3. Revisa los terminos ontologicos disponibles en la metadata del modelo")
