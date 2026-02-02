import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# --- CONFIGURACIÓN ---
# Tu archivo de 23andMe
FILE_23ANDME = "genome_Fernando_MartinAlba_v5_Full_20180913002108.txt"
# El cromosoma de referencia que descargaste (ej. chr22)
REF_FASTA = "chr22.fa" 
# El cromosoma que queremos procesar (debe coincidir con el FASTA)
CHROM_TO_PROCESS = "22" 
OUTPUT_FILE = "genoma_fernando_chr22.fasta"
# ---------------------

print(f"1. Leyendo datos de 23andMe para el cromosoma {CHROM_TO_PROCESS}...")

# Leemos el archivo saltando las líneas de comentarios (#)
# Tip: 23andMe usa build 37 (hg19)
df = pd.read_csv(FILE_23ANDME, sep='\t', comment='#', header=None, 
                 names=['rsid', 'chrom', 'pos', 'genotype'], dtype={'chrom': str})

# Filtramos solo el cromosoma que nos interesa para ahorrar memoria RAM
df_chr = df[df['chrom'] == CHROM_TO_PROCESS].copy()
print(f"   -> Encontradas {len(df_chr)} variantes para chr{CHROM_TO_PROCESS}")

print("2. Cargando secuencia de referencia (esto puede tardar unos segundos)...")
# Usamos Biopython para leer la referencia
ref_record = next(SeqIO.parse(REF_FASTA, "fasta"))
# Convertimos a lista mutable para editar (las cadenas en python son inmutables)
# NOTA: 23andMe usa coordenadas base-1, Python usa base-0
seq_mutable = list(str(ref_record.seq).upper())

print("3. 'Parcheando' tu genoma...")
applied_count = 0
ignored_count = 0

for idx, row in df_chr.iterrows():
    pos_0 = row['pos'] - 1 # Ajuste a base-0
    genotype = row['genotype']
    
    # Solo procesamos si la posición está dentro de la referencia descargada
    if pos_0 < len(seq_mutable):
        # 23andMe da genotipos diploides (ej: "AG", "CC"). 
        # Para AlphaGenome necesitamos una secuencia haploide.
        # ESTRATEGIA: Tomamos el primer alelo (o el alternativo si difiere de la ref).
        # Ignoramos deleciones/inserciones ('-', 'D', 'I') para mantener la longitud 
        # y alineación correcta de la referencia (crítico para redes neuronales).
        
        allele = genotype[0] # Tomamos la primera letra
        
        if allele in ['A', 'C', 'G', 'T']:
            # Solo aplicamos si es diferente a la referencia
            if seq_mutable[pos_0] != allele:
                seq_mutable[pos_0] = allele
                applied_count += 1
        else:
            ignored_count += 1

print(f"   -> Variantes aplicadas: {applied_count}")
print(f"   -> Variantes complejas ignoradas (indels/no-calls): {ignored_count}")

print("4. Guardando nuevo archivo FASTA...")
new_seq = "".join(seq_mutable)
new_record = SeqRecord(Seq(new_seq), id=f"Fernando_chr{CHROM_TO_PROCESS}", description="hg19_patched_23andme")
SeqIO.write(new_record, OUTPUT_FILE, "fasta")

print(f"¡Éxito! Archivo listo: {OUTPUT_FILE}")