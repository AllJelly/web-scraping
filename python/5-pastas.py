from datetime import datetime
from itertools import count
from typing import Any
import pandas as pd
import unicodedata
import os
import re

input_arq   = "./listas/lista-genero-provedor/grupo-20241231.csv"
out_folder  = "./strm"
blacklist = ['with ads', 'amazon channel', 'música', ' tv channel', 'mgm+ apple tv channel', 'docalliance films', '007 colecao']

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
df = df.sort_values(by='name', ascending=True)

df['temporada'] = df['temporada'].astype('Int64')  # Suporte para valores ausentes
df['episodio'] = df['episodio'].astype('Int64')    # Suporte para valores ausentes

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
            caminho = f"{out_folder}/{pasta}/{arquivo}"
            caminho_arquivo = f"{caminho}/{arquivo}"
        else:
            if row['episodio'] is None or row['temporada'] is None:
                break
            caminho = f"{out_folder}/{pasta}/{arquivo}/Season {row['temporada']:02}"
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