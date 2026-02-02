import sys
import os
import grpc

# 1. Configuración de rutas
sys.path.append('/home/ignac/Genoma/alphagenome/src')

from alphagenome.models import dna_client
from alphagenome.models import dna_output
from alphagenome.data import ontology
from Bio import SeqIO
import matplotlib.pyplot as plt

# @title Configuración
API_KEY = 'AIzaSyDLXmTFGqzp73aTl5pZ1CJmySokInyVlsI'

# Conexión gRPC
channel = grpc.secure_channel('alphagenome-api.googleapis.com:443', grpc.ssl_channel_credentials())
client = dna_client.DnaClient(channel=channel, metadata=(('x-goog-api-key', API_KEY),))

# 2. Definir el término ontológico CORRECTO
# Según la clase OntologyTerm en src/alphagenome/data/ontology.py, el campo es 'id'
# Usamos un ID genérico o vacío para obtener la respuesta global
terminos_bio = [ontology.OntologyTerm(id='')] 

print("Cargando tu secuencia personalizada...")
record = next(SeqIO.parse("genoma_fernando_chr22.fasta", "fasta"))
secuencia = str(record.seq)

# Ventana del gen COMT
start_pos = 19_928_000 
fragmento = secuencia[start_pos : start_pos + 131072]

print("Enviando petición final a AlphaGenome...")

try:
    # Llamada con todos los argumentos requeridos por el servidor
    prediction = client.predict_sequence(
        sequence=fragmento,
        requested_outputs=[
            dna_output.OutputType.ATAC, 
            dna_output.OutputType.RNA_SEQ
        ],
        ontology_terms=terminos_bio
    )

    print("¡CONEXIÓN EXITOSA! Generando gráficos...")
    
    # 3. Visualización
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Track de Accesibilidad
    ax1.plot(prediction.tracks[0].values, color='#e63946')
    ax1.set_title("Accesibilidad del ADN (ATAC) - Gen COMT (Fernando)")
    ax1.fill_between(range(len(prediction.tracks[0].values)), 
                     prediction.tracks[0].values, color='#e63946', alpha=0.2)
    
    # Track de Expresión
    ax2.plot(prediction.tracks[1].values, color='#457b9d')
    ax2.set_title("Predicción de Expresión (RNA-seq) - Gen COMT (Fernando)")
    ax2.fill_between(range(len(prediction.tracks[1].values)), 
                     prediction.tracks[1].values, color='#457b9d', alpha=0.2)

    plt.tight_layout()
    plt.savefig("analisis_COMT_fernando_final.png")
    print("¡TERMINADO! Revisa el archivo: analisis_COMT_fernando_final.png")

except Exception as e:
    print(f"Error en el proceso: {e}")