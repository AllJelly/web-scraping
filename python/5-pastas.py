from datetime import datetime
import pandas as pd
import os

input_arq   = "./listas/lista-genero-provedor/grupo-20241231.csv"
out_folder  = "./strm"

if not os.path.exists(out_folder):
    os.makedirs(out_folder)
    
def resolucao(largura, altura):
    resolucoes = {
        "144p": (256, 144),
        "240p": (426, 240),
        "360p": (640, 360),
        "480p": (854, 480),
        "576p (PAL)": (720, 576),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "WUXGA": (1920, 1200),
        "2K": (2560, 1440),
        "4K": (3840, 2160),
        "Cinema 4K": (4096, 2160),
        "8K": (7680, 4320),
    }
    
    for rotulo, (w, h) in resolucoes.items():
        if largura == w and altura == h:
            return f" - [{rotulo}]"
    return ""
    
df = pd.read_csv(input_arq)

for _, row in df.iterrows():
    pastas = row['group-title'].split(' | ')
    if pd.isna(row['generos']) == False:
        pastas += row['generos'].split(', ')
    if pd.isna(row['provedor']) == False:
        pastas += row['provedor'].split(', ')

    pastas = [category for category in pastas if 'with Ads' not in category]
    pastas = ['Suspense' if category == 'Thriller' else category for category in pastas]

    if row['legendado'] == True and not ['Legendados'] in pastas:
        pastas.append("Legendados")

    data = datetime.strptime( row['date'], '%Y-%m-%d')

    pastas = [item.strip() for item in pastas]
    arquivo = f"{row['name']} ({data.year})"

    for pasta in pastas:
        caminho = f"{out_folder}/{pasta}/{arquivo}"
        if not os.path.exists(caminho):
            os.makedirs(caminho)
        
        if row['tipo'] == 'Filme':
            caminho_arquivo = f"{caminho}/{arquivo}{resolucao(row['largura'], row['altura'])}.strm"
            with open(caminho_arquivo, 'w') as file:
                file.write(row['link'])
        else:
            pass