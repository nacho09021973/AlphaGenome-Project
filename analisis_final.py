import sys
import os
import grpc

# 1. Configuración de rutas
sys.path.append('/home/ignac/Genoma/alphagenome/src')

import numpy as np
import matplotlib.pyplot as plt
from Bio import SeqIO
from alphagenome.models import dna_client

# Tu API Key
API_KEY = 'AIzaSyDLXmTFGqzp73aTl5pZ1CJmySokInyVlsI'

print("Estableciendo conexión gRPC con DeepMind...")

# 2. Configuración del canal seguro
# El servidor de AlphaGenome suele estar en alphagenome-api.googleapis.com:443
# Usamos credenciales de SSL y añadimos la API Key en los metadatos
target = 'alphagenome-api.googleapis.com:443'
credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel(target, credentials)

# Creamos el cliente pasando el canal y la clave en los metadatos
metadata = (('x-goog-api-key', API_KEY),)
client = dna_client.DnaClient(channel=channel, metadata=metadata)

# 3. Carga de tu secuencia personalizada
print("Cargando tu cromosoma 22 parcheado...")
record = next(SeqIO.parse("genoma_fernando_chr22.fasta", "fasta"))
secuencia = str(record.seq)

# 4. Región COMT
# hg19: 19,928,602. Tomamos ventana de 128kb
start = 19_900_000 
window = 131072 
fragmento = secuencia[start : start + window]

# 5. Predicción Remota
print("Enviando datos al modelo AlphaGenome...")
try:
    # El método oficial según la documentación de la API
    prediction = client.predict_sequence(fragmento)
    print("¡Predicción recibida con éxito!")
    
    # 6. Gráfica de resultados
    plt.figure(figsize=(12, 8))
    
    # Graficamos los tracks principales (Accesibilidad y Expresión)
    for i, track in enumerate(prediction.tracks[:3]):
        plt.subplot(3, 1, i+1)
        plt.plot(track.values)
        plt.title(f"Resultado AlphaGenome: {track.metadata.description}")
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("mi_genoma_COMT.png")
    print("Análisis guardado en 'mi_genoma_COMT.png'")

except Exception as e:
    print(f"Error durante la inferencia: {e}")