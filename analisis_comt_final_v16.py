"""
AlphaGenome Analysis - Gen COMT (Fernando)
Version: 16 (Corregida - Endpoint gRPC correcto)
Fecha: 2026-02-02

PROBLEMA RESUELTO:
==================
El error 404 UNIMPLEMENTED era causado por usar el HOST INCORRECTO:
  - INCORRECTO: alphagenome-api.googleapis.com:443
  - CORRECTO:   gdmscience.googleapis.com:443

El service path gRPC es:
  /google.gdm.gdmscience.alphagenome.v1main.DnaModelService/PredictSequence

Solucion: Usar dna_client.create() que configura el endpoint correcto
         automaticamente, o especificar el host manualmente.
"""

import sys

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
# CONEXION gRPC - METODO CORRECTO
# =============================================================================
# OPCION 1 (RECOMENDADA): Usar dna_client.create() que configura todo
#                         automaticamente con el endpoint correcto
# =============================================================================
print("="*70)
print("AlphaGenome v0.5.1 - Conexion gRPC CORREGIDA")
print("="*70)
print()
print("Endpoint oficial: gdmscience.googleapis.com:443")
print("Service path: /google.gdm.gdmscience.alphagenome.v1main.DnaModelService")
print()
print("Estableciendo conexion gRPC con AlphaGenome API...")

# Metodo recomendado - deja que la libreria configure el endpoint
client = dna_client.create(
    api_key=API_KEY,
    timeout=30.0  # Timeout de 30 segundos para esperar que el canal este listo
)

# =============================================================================
# OPCION 2 (ALTERNATIVA MANUAL): Si necesitas configurar el canal manualmente
# =============================================================================
# import grpc
#
# # HOST CORRECTO (gdmscience, NO alphagenome-api)
# CORRECT_HOST = 'dns:///gdmscience.googleapis.com:443'
#
# options = [
#     ('grpc.max_send_message_length', -1),
#     ('grpc.max_receive_message_length', -1),
# ]
#
# channel = grpc.secure_channel(
#     CORRECT_HOST,
#     grpc.ssl_channel_credentials(),
#     options=options
# )
# grpc.channel_ready_future(channel).result(timeout=30)
#
# client = dna_client.DnaClient(
#     channel=channel,
#     metadata=[('x-goog-api-key', API_KEY)]
# )
# =============================================================================

print("Conexion establecida exitosamente!")
print()

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
print()

# =============================================================================
# PREDICCION
# =============================================================================
print("Enviando peticion a AlphaGenome...")
print("(Service: /google.gdm.gdmscience.alphagenome.v1main.DnaModelService/PredictSequence)")
print()

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

    print("="*70)
    print("PREDICCION RECIBIDA EXITOSAMENTE!")
    print("="*70)
    print(f"Numero de tracks ATAC: {len(prediction.atac.values) if prediction.atac else 0}")
    print(f"Numero de tracks RNA_SEQ: {len(prediction.rna_seq.values) if prediction.rna_seq else 0}")
    print()

    # =============================================================================
    # VISUALIZACION
    # =============================================================================
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Track de Accesibilidad (ATAC)
    ax1 = axes[0]
    if prediction.atac is not None:
        atac_values = prediction.atac.values[:, 0]  # Primera columna
        ax1.plot(atac_values, color='#e63946', linewidth=0.8)
        ax1.fill_between(
            range(len(atac_values)),
            atac_values,
            color='#e63946',
            alpha=0.2
        )
    ax1.set_title("Accesibilidad de Cromatina (ATAC) - Gen COMT (Fernando)", fontsize=12)
    ax1.set_ylabel("Senal ATAC")
    ax1.grid(True, alpha=0.3)

    # Track de Expresion (RNA-seq)
    ax2 = axes[1]
    if prediction.rna_seq is not None:
        rna_values = prediction.rna_seq.values[:, 0]  # Primera columna
        ax2.plot(rna_values, color='#457b9d', linewidth=0.8)
        ax2.fill_between(
            range(len(rna_values)),
            rna_values,
            color='#457b9d',
            alpha=0.2
        )
    ax2.set_title("Prediccion de Expresion (RNA-seq) - Gen COMT (Fernando)", fontsize=12)
    ax2.set_xlabel("Posicion (bp)")
    ax2.set_ylabel("Senal RNA-seq")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = "analisis_COMT_fernando_v16.png"
    plt.savefig(output_file, dpi=150)
    print(f"Grafico guardado: {output_file}")

except Exception as e:
    print("="*70)
    print("ERROR DURANTE LA INFERENCIA")
    print("="*70)
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensaje: {e}")
    print()
    print("Sugerencias de depuracion:")
    print("1. Verifica que la API key sea valida para gdmscience.googleapis.com")
    print("2. Confirma que tienes acceso a la API de AlphaGenome")
    print("3. Verifica tu conexion a Internet")
    print("4. Si el error persiste, prueba con el metodo manual (OPCION 2)")
