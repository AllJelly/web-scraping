import pandas as pd

_B = 1
_KB = _B * 1000
_MB = _KB * 1000
_GB = _MB * 1000

df = pd.read_csv('./listas/3-lista-metadados/metadados.csv')

df['tamanho_GB'] = pd.to_numeric(df['tamanho_GB'], errors='coerce')
df['tamanho_GB'] = df['tamanho_GB'].fillna(0)

total = int(df['tamanho_GB'].sum()/1000)

sem_lg = 0
for index, row in df.iterrows():
    text = row['name'].lower()
    if (not(" leg " in  text or text[-3:] == 'leg')):
        sem_lg += row['tamanho_GB']
        
sem_lg = int(sem_lg/1000)

print(f"Sem legendados - {sem_lg} TB\nLegendados - {total-sem_lg} TB\nTotal - {total} TB")