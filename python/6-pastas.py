from curses import beep
from datetime import datetime
import pandas as pd
import unicodedata
import os

input_arq   = "./listas/lista-genero-provedor/grupo.csv"
out_folder  = "./strm"
blacklist = ['with ads', 'amazon channel', 'música', ' tv channel', 'mgm+ apple tv channel', 'docalliance films', '007 colecao', 'cinema tv']
blacklist += ['cultpix', 'eventive', 'microsoft', 'gospel play', 'WOW Presents Plus', 'filmicca', 'spamflix', 'sun nxt', 
              'moviesaints', 'docsville', 'magellan tv', 'true story', 'history play']

mapa = {
    "A, m, a, z, o, n,  , P, r, i, m, e,  , V, i, d, e, o": "Amazon Prime Video",
    "A, m, a, z, o, n,  , V, i, d, e, o": "Amazon Prime Video",
    
    "A, p, p, l, e,  , T, V,  , P, l, u, s": "Apple TV Plus",
    "A, p, p, l, e,  , T, V, +": "Apple TV Plus",
    "A, p, p, l, e,  , T, V": "Apple TV Plus",
    
    "C, l, a, r, o,  , t, v, +": "Claro TV+",
    "C, l, a, r, o,  , v, i, d, e, o": "Claro Video",
    "C, r, u, n, c, h, y, r, o, l, l": "Crunchyroll",
    
    "D, i, s, n, e, y,  , P, l, u, s": "Disney Plus",
    "D, i, s, n, e, y, +": "Disney Plus",
    
    "G, l, o, b, o, p, l, a, y": "Globoplay",
    "G, l, o, o, g, l, e,  , P, l, a, y,  , M, o, v, i, e, s": "Google Play Movies",
    "K, o, c, o, w, a": "Kocowa",
    "L, o, o, k, e": "Looke",
    "M, a, x": "Max",
    "M, U, B, I": "MUBI",
    "N, e, t, f, l, i, x": "Netflix",
    "O, l, d, f, l, i, x": "Oldflix",
    
    "P, a, r, a, m, o, u, n, t,  , P, l, u, s": "Paramount Plus",
    "P, a, r, a, m, o, u, n, t, +": "Paramount Plus",
    
    "R, e, s, e, r, v, a,  , I, m, o, v, i, s, i, o, n": "Reserva Imovision",
    "U, n, i, v, e, r,  , V, i, d, e, o": "Univer Video",
}

qtd_provedores = 1
qtd_generos = 1

if not os.path.exists(out_folder):
    os.makedirs(out_folder)

def remover_acentos(texto):
    # Normaliza a string para decompor os caracteres com acento
    nfkd_form = unicodedata.normalize('NFKD', texto)
    # Filtra os caracteres que não têm acento (retira os acentos)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def resolucao(largura, altura):
    resolucoes = {
        "144p": (256, 144),
        "240p": (426, 240),
        "360p": (640, 360),
        "480p": (854, 480),
        "576p": (720, 576),
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
            return f" {rotulo}"
    return ""
    
df = pd.read_csv(input_arq)
df = df.sort_values(by='validade', ascending=True)

df['temporada'] = df['temporada'].astype('Int64')  # Suporte para valores ausentes
df['episodio'] = df['episodio'].astype('Int64')    # Suporte para valores ausentes


df = df.drop_duplicates(subset=["titulo", "largura","temporada", "episodio"], keep="first").reset_index(drop=True)

# df = df.iloc[4000:,:]
# df = df.iloc[9986:,:]
# df = df.iloc[10015:,:]
# df = df.iloc[32000:,:]

for _, row in df.iterrows():
    if row['tamanho_GB'] <= 0.002033:
        continue
    if pd.isna(row['generos']) == False:
        generos = [prov for prov in row['generos'].split(', ') if len(prov) > 1]
    else:
        generos = []
        
    if pd.isna(row['provedor']) == False:
        for chave, value in mapa.items():
            row['provedor'] = row['provedor'].replace(chave, value)
        provedores = [prov for prov in row['provedor'].split(', ') if len(prov) > 1]
    else:
        provedores = []
    
    # Genero
    generos = [
        category for category in generos
        if not any(blacklisted in category.lower() for blacklisted in blacklist)
    ]
    generos = [remover_acentos(item.strip()) for item in generos]
    generos = ['Suspense' if category.lower() == 'thriller' else category for category in generos]
    generos = ['Documentario' if category.lower() == 'documentarios' else category for category in generos]
    if row['legendado'] == True and not ['Legendados'] in generos:
        if generos == ['Outros']:
            generos = ["Legendados"]
        else:
            generos.append("Legendados")
    if 'Animacao'in generos:
        generos = ['Animacao']
    elif 'Documentario'in generos:
        generos = ['Documentario']
    elif 'Romance'in generos:
        generos = ['Romance']
    elif 'Drama'in generos:
        generos = ['Drama']
    elif 'Comedia'in generos:
        generos = ['Comedia']
    else:
        generos = generos[:qtd_generos]
    if not generos:
        generos = ['Outros']
        
    # Provedores
    provedores = [
        category for category in provedores
        if not any(blacklisted in category.lower() for blacklisted in blacklist)
    ]
    provedores = provedores[:qtd_provedores]
    provedores = [remover_acentos(item.strip()) for item in provedores]
    provedores = ['Amazon Prime Video' if category.lower() == 'amazon video' else category for category in provedores]
    provedores = ['Apple TV Plus' if category.lower() in ['apple tv+', 'apple tv'] else category for category in provedores]
    provedores = ['Disney Plus' if category.lower() == 'disney +' else category for category in provedores]
    provedores = ['Paramount Plus' if category.lower() in ['paramount +', 'paramount plus premium'] else category for category in provedores]
    provedores = ['Claro TV Plus' if category.lower() == 'claro tv+' else category for category in provedores]
    provedores = ['Star Plus' if category.lower() == 'star +' else category for category in provedores]
    if not provedores:
        provedores = ['Outros']
    
    nome = row['titulo'].replace("/", " ")

    if row['tipo'] == 'Filme':
        try:
            data = datetime.strptime(row['date'], '%Y-%m-%d')
            arquivo = f"{nome} ({data.year})"
        except Exception as e:
            arquivo = f"{nome}"
    else:
        arquivo = nome
                
    for genero in generos:
        if row['tipo'] == 'Filme':
            caminho = f"{out_folder}/Filmes/{provedores[0]}/{genero}/{arquivo}"
            caminho_arquivo = f"{caminho}/{arquivo}"
        else:
            if row['episodio'] is None or row['temporada'] is None:
                break
            caminho = f"{out_folder}/Series/{provedores[0]}/{genero}/{arquivo}/Season {row['temporada']:02}"
            caminho_arquivo = f"{caminho}/{arquivo} S{row['temporada']:02}E{row['episodio']:02}"
            
        resoluc = resolucao(row['largura'], row['altura'])
        if row['legendado'] == True:
            caminho_arquivo = f"{caminho_arquivo} - Legendado"
        elif resoluc != "":
            caminho_arquivo = f"{caminho_arquivo} -"
        else:
            caminho_arquivo = f"{caminho_arquivo}"
        caminho_arquivo = f"{caminho_arquivo}{resoluc}.strm"
            
        if not os.path.exists(caminho):
            os.makedirs(caminho)
        with open(caminho_arquivo, 'w') as file:
            file.write(row['link'])