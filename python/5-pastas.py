from datetime import datetime
from itertools import count
import pandas as pd
import unicodedata
import os
import re

input_arq   = "./listas/lista-genero-provedor/grupo-20241231.csv"
out_folder  = "./strm"
blacklist = ['with ads', 'amazon channel', 'música', ' tv channel', 'mgm+ apple tv channel', 'docalliance films', '007 colecao']

if not os.path.exists(out_folder):
    os.makedirs(out_folder)

def extrair_informacoes(nome):
    # Define o padrão para capturar os números da temporada, episódio e o nome
    padrao = r"(.*)\sS(\d{2})\sE(\d{2})"
    # Busca o padrão no nome
    match = re.search(padrao, nome)
    if match:
        titulo, season, episode = match.groups()
        # Remove prefixos e ajusta o nome
        titulo = titulo.split("/")[-1].strip()  # Remove diretórios no caminho
        return titulo, season, episode
    return None, None, None

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

for _, row in df.iterrows():
    if row['tipo'] == 'Filme':
        pastas = ["Filmes"]
    else:
        pastas = ["Series"]
        
    if pd.isna(row['generos']) == False:
        pastas += row['generos'].split(', ')
    if pd.isna(row['provedor']) == False:
        pastas += row['provedor'].split(', ')

    pastas = ['Suspense' if category == 'Thriller' else category for category in pastas]
    pastas = ['Amazon Prime Video' if category == 'Amazon Video' else category for category in pastas]
    pastas = ['Apple TV Plus' if category == 'Apple TV+' else category for category in pastas]
    pastas = ['Disney Plus' if category == 'Disney +' else category for category in pastas]
    pastas = ['Documentario' if category == 'Documentarios' else category for category in pastas]
    pastas = ['Paramount Plus' if category == 'Paramount +' else category for category in pastas]
    pastas = ['Claro TV Plus' if category == 'Claro tv+' else category for category in pastas]
    pastas = ['Star Plus' if category == 'Star +' else category for category in pastas]
    pastas = [
        category for category in pastas
        if not any(blacklisted in category.lower() for blacklisted in blacklist)
    ]
    
    if row['legendado'] == True and not ['Legendados'] in pastas:
        pastas.append("Legendados")


    pastas = [remover_acentos(item.strip()) for item in pastas]
    nome = row['name'].replace("/", " ")

    if row['tipo'] == 'Filme':
        try:
            data = datetime.strptime(row['date'], '%Y-%m-%d')
            arquivo = f"{nome} ({data.year})"
        except Exception as e:
            arquivo = f"{nome}"
    else:
        arquivo = nome
            
    for pasta in pastas:
        if len(pasta) <= 1:
            continue
        
        if row['tipo'] == 'Filme':
            continue
            caminho = f"{out_folder}/{pasta}/{arquivo}"
            caminho_arquivo = f"{caminho}/{arquivo}"
        else:
            titulo, season, episode = extrair_informacoes(arquivo)
            print(titulo, season, episode)
            caminho = f"{out_folder}/{pasta}/{titulo}/Season {season}"
            caminho_arquivo = f"{caminho}/{titulo} S{season}E{episode}"
            
        # resoluc = resolucao(row['largura'], row['altura'])
        # if row['legendado'] == True:
        #     caminho_arquivo = f"{caminho_arquivo} - Legendado"
        # elif resoluc != "":
        #     caminho_arquivo = f"{caminho_arquivo} -"
        # else:
        #     caminho_arquivo = f"{caminho_arquivo}"
        # caminho_arquivo = f"{caminho_arquivo}{resoluc}.strm"
            
        # if not os.path.exists(caminho):
        #     os.makedirs(caminho)
        # with open(caminho_arquivo, 'w') as file:
        #     file.write(row['link'])