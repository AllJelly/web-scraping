import pandas as pd

arq   = "./listas/3-lista-videos/videos-2.csv"
arq2   = "./listas/3-lista-videos/videos-3.csv"

df = pd.read_csv(arq)

df['name'] = df['name'].apply(lambda x: f'-{x}-')

df['date'] = df['provedor'] = df['generos'] = df['titulo'] = None

df.to_csv(arq2, index=False)