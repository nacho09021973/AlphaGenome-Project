import alphagenome
import numpy as np
import matplotlib.pyplot as plt
from Bio import SeqIO

# 1. Cargar el modelo pre-entrenado
# Nota: La primera vez descargará varios GB de parámetros
print("Cargando modelo AlphaGenome...")
model = alphagenome.AlphaGenomeModel.from_pretrained("human_hg19_v1")

# 2. Cargar tu secuencia personalizada
print("Cargando tu secuencia del cromosoma 22...")
record = next(SeqIO.parse("genoma_fernando_chr22.fasta", "fasta"))
secuencia_completa = str(record.seq)

# 3. Seleccionar una ventana de interés
# AlphaGenome brilla analizando regiones de regulación. 
# Vamos a analizar un segmento de 128kb (estándar para ver efectos locales)
start_pos = 20_000_000 # Ejemplo: una región central del chr22
end_pos = start_pos + 131072 
fragmento = secuencia_completa[start_pos:end_pos]

# 4. Predicción
print(f"Analizando región {start_pos} - {end_pos}...")
# El modelo espera un array de strings o secuencias codificadas
prediction = model.predict_sequence(fragmento)

# 5. Visualización de resultados
# AlphaGenome suele devolver tracks de: Accesibilidad (ATAC-seq), Histonas y Expresión
print("Generando visualización de actividad genómica...")

plt.figure(figsize=(15, 8))

# Graficamos la predicción de accesibilidad de la cromatina (ejemplo)
plt.subplot(2, 1, 1)
plt.plot(prediction['chromatin_accessibility'][0])
plt.title("Accesibilidad de la Cromatina Predicha (Tus datos)")
plt.ylabel("Señal")

# Graficamos la predicción de transcripción
plt.subplot(2, 1, 2)
plt.plot(prediction['transcription_rates'][0], color='green')
plt.title("Tasa de Transcripción Estimada")
plt.xlabel("Posición relativa en la ventana")
plt.ylabel("Nivel de expresión")

plt.tight_layout()
plt.savefig("mi_analisis_genomico.png")
print("Análisis guardado en 'mi_analisis_genomico.png'")