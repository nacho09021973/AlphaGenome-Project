import sys
import os

# Añadimos la ruta al código fuente que descargaste
sys.path.append('/home/ignac/Genoma/alphagenome/src')

import alphagenome
from alphagenome import colab_utils
from Bio import SeqIO
import matplotlib.pyplot as plt

# 1. Conexión oficial (detecta la variable ALPHAGENOME_API_KEY)
print("Conectando con los servidores de DeepMind...")
try:
    client = colab_utils.get_client()
    print("Autenticación exitosa.")
except Exception as e:
    print(f"Error de conexión: {e}")
    sys.exit()

# 2. Carga de tu secuencia 'Fernando' (Cromosoma 22)
print("Cargando tu secuencia personalizada...")
record = next(SeqIO.parse("genoma_fernando_chr22.fasta", "fasta"))
secuencia_completa = str(record.seq)

# 3. Definición de la ventana para el gen COMT
# hg19: inicio del gen ~19,928,602
start_pos = 19_928_000 
window_size = 131072 # Tamaño estándar (128kb)
fragmento = secuencia_completa[start_pos : start_pos + window_size]

# 4. Inferencia Remota (Aquí es donde ocurre la magia de la IA)
print("Enviando fragmento de ADN a AlphaGenome...")
prediction = client.predict_sequence(fragmento)

# 5. Visualización de resultados
print("Procesando señales genómicas...")
plt.figure(figsize=(12, 10))

# El modelo devuelve varios 'tracks'. Vamos a ver los más importantes:
# Track 0: Accesibilidad / Track 1: Histonas / Track 2: Expresión (RNA)
for i, track in enumerate(prediction.tracks[:3]):
    plt.subplot(3, 1, i+1)
    plt.plot(track.values, color='navy' if i==0 else 'darkgreen' if i==2 else 'orange')
    plt.title(f"Track {i+1}: {track.metadata.description}")
    plt.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig("resultado_fernando_COMT.png")
print("¡ANÁLISIS COMPLETADO! Mira el archivo 'resultado_fernando_COMT.png'")