from curses import beep
from datetime import datetime
import pandas as pd
import unicodedata
import os
import math

input_arq   = "./listas/3-lista-videos/videos-ajustado.csv"
out_folder  = "./strm"
blacklist = ['with ads', 'amazon channel', 'musica', ' tv channel', 'mgm+ apple tv channel', 'docalliance films', '007 colecao', 'cinema tv', 'filme coringa', 'sem data definida', 'nao disponivel', 'n/a', 'n/d']
blacklist += ['horror',
              'cultpix', 'eventive', 'microsoft', 'gospel play', 'WOW Presents Plus', 'filmicca', 'spamflix', 'sun nxt', 'telefe', 'sbt', 'televisa', 'cinema', 'streaming',
              'moviesaints', 'docsville', 'magellan tv', 'true story', 'history play', 'hoichoi', 'shudder', 'vod', 'peacock', 'vudu', 'vimeo', 'youtube', 'twitch', 'filmstruck']

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
        "144p": (256, 144),  # 36864 pixels
        "240p": (426, 240),  # 102240 pixels
        "SVGA": (800, 600),  # 480000 pixels
        "WVGA": (800, 480),  # 384000 pixels
        "SD 480p": (854, 480),  # 410880 pixels
        "WXGA": (1366, 768),  # 1049088 pixels
        "Super HD": (1366, 768),  # 1049088 pixels (marketing termo, geralmente para 1366x768)
        "HD+": (1600, 900),  # 1440000 pixels
        "HD 720p": (1280, 720),  # 921600 pixels
        "WGA": (1280, 800),  # 1024000 pixels
        "Full HD 1080p": (1920, 1080),  # 2073600 pixels
        "2K": (2560, 1440),  # 3686400 pixels
        "QHD (Quad HD)": (2560, 1440),  # 3686400 pixels (mesma resolução que 2K)
        "Ultrawide HD 1080p": (2560, 1080),  # 2764800 pixels
        "Ultrawide 2K 1440p": (3440, 1440),  # 4949760 pixels
        "Super Ultrawide 2K 1440p": (5120, 1440),  # 7372800 pixels
        "4K UHD": (3840, 2160),  # 8294400 pixels
        "Ultra HD 4K": (3840, 2160),  # 8294400 pixels (mesma resolução que 4K)
        "Cinema 4K": (4096, 2160),  # 8847360 pixels
        "Super Ultrawide 4K": (5120, 2160),  # 11059200 pixels
        "5K": (5120, 2880),  # 14745600 pixels
        "8K UHD": (7680, 4320),  # 33177600 pixels
        "16K": (15360, 8640),  # 132710400 pixels
        "UXGA": (1600, 1200),  # 1920000 pixels
        "XGA": (1024, 768),  # 786432 pixels
        "Wide QXGA": (2048, 1152),  # 2359296 pixels
    }

    if pd.isna(largura) or pd.isna(altura):
        return ""
    largura, altura = int(largura), int(altura)
    
    for rotulo, (w, h) in resolucoes.items():
        if largura == w and altura == h:
            return f" {rotulo}"
    
    def proporcao_para_label(proporcao):
        proporcoes_comuns = {
            (16, 9): "16-9",
            (21, 9): "21-9",
            (2, 1): "2-1",
            (4, 3): "4-3",
            (3, 2): "3-2",
        }

        w, h = map(int, proporcao.split(":"))
        
        # Verifica qual proporção mais próxima das predefinidas
        for (px, py), label in proporcoes_comuns.items():
            # Calcula a diferença entre as proporções
            if abs(w * py - h * px) < 10:  # Tolerância de 10 unidades para maior flexibilidade
                return label
        
        return proporcao
    def calcular_diferenca_proporcao(proporcao1, proporcao2):
        w1, h1 = map(int, proporcao1.split(":"))
        w2, h2 = map(int, proporcao2.split(":"))
        return abs(w1 * h2 - h1 * w2)  # Diferença entre as proporções (multiplicação cruzada)
    def calcular_proporcao(largura, altura):
        mdc = math.gcd(largura, altura)
        if mdc == 0:
            return ""
        largura_simplificada = largura // mdc
        altura_simplificada = altura // mdc
        return f"{largura_simplificada}-{altura_simplificada}"
    
    resolucao_mais_proxima = None
    proporcao = calcular_proporcao(largura, altura)
    if proporcao != "":
        menor_diferenca = float('inf')
        for rotulo, (w, h) in resolucoes.items():
            proporcao_resolucao = calcular_proporcao(w, h)
            if proporcao_resolucao == '':
                continue
            diferenca = calcular_diferenca_proporcao(proporcao, proporcao_resolucao)
            if diferenca < menor_diferenca:
                menor_diferenca = diferenca
                resolucao_mais_proxima = rotulo
    
    if resolucao_mais_proxima != None:
        # Converte a proporção calculada para o label de proporção mais próximo
        proporcao_formatada = proporcao_para_label(proporcao)
        return f" {resolucao_mais_proxima} {proporcao_formatada}"
    else:
        return f" {largura}x{altura}"
        
    
df = pd.read_csv(input_arq)
df = df.sort_values(by='validade', ascending=True)

df['temporada'] = df['temporada'].astype('Int64')  # Suporte para valores ausentes
df['episodio']  = df['episodio'].astype('Int64')   # Suporte para valores ausentes
df['titulo']    = df['titulo'].astype('string')

df = df.drop_duplicates(subset=["titulo", "largura", "altura","temporada", "episodio"], keep="first").reset_index(drop=True)

# Preenchendo o provedor baseado no título
df["provedor"] = df.groupby("titulo")["provedor"].transform("first")
df["generos"] = df.groupby("titulo")["generos"].transform("first")

# df = df[df["Url do Servidor"] == "http://wateronplay.com:80/"]
for _, row in df.iterrows():
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
    generos = [remover_acentos(item.strip()) for item in generos]
    generos = [
        category[0].upper()+category[1:] for category in generos
        if not any(blacklisted in category.lower() for blacklisted in blacklist)
    ]
    generos = ['Suspense' if category.lower() == 'thriller' else category for category in generos]
    generos = ['Documentario' if category.lower() == 'documentarios' else category for category in generos]
    if row['legendado'] == True and not ['Legendados'] in generos:
        if generos == ['Outros']:
            generos = ["Legendados"]
        else:
            generos.append("Legendados")
    if any([True for genero in generos if 'animacao' in genero.lower()]):
        generos = ['Animacao']
    elif any([True for genero in generos if 'documentario' in genero.lower()]):
        generos = ['Documentario']
    elif any([True for genero in generos if 'faroeste' in genero.lower()]):
        generos = ['Faroeste']
    elif any([True for genero in generos if 'terror' in genero.lower()]):
        generos = ['Terror']
    elif any([True for genero in generos if 'comedia' in genero.lower()]):
        generos = ['Comedia']
    elif any([True for genero in generos if 'guerra' in genero.lower()]):
        generos = ['Guerra']
    elif any([True for genero in generos if 'historia' in genero.lower()]):
        generos = ['Historia']
    elif any([True for genero in generos if 'fantasia' in genero.lower()]):
        generos = ['Fantasia']
    elif any([True for genero in generos if 'ficcao cientifica' in genero.lower()]):
        generos = ['Ficcao cientifica']
    elif any([True for genero in generos if 'romance' in genero.lower()]):
        generos = ['Romance']
    elif any([True for genero in generos if 'drama' in genero.lower()]):
        generos = ['Drama']
    elif any([True for genero in generos if 'crime' in genero.lower()]):
        generos = ['Crime']
    if not generos:
        generos = ['Outros']
        
    # Provedores
    provedores = [remover_acentos(item.strip()) for item in provedores]
    provedores = [
        category[0].upper()+category[1:] for category in provedores
        if not any(blacklisted in category.lower() for blacklisted in blacklist)
    ]
    provedores = ['Amazon Prime Video' if 'amazon' in category.lower() or 'prime video' in category.lower() else category for category in provedores]
    provedores = ['Paramount Plus' if 'paramount' in category.lower() else category for category in provedores]
    provedores = ['Discovery Plus' if 'discovery' in category.lower() else category for category in provedores]
    provedores = ['Apple TV Plus' if 'apple' in category.lower() else category for category in provedores]
    provedores = ['Disney Plus' if 'disney' in category.lower() else category for category in provedores]
    provedores = ['GloboPlay' if 'globo' in category.lower() else category for category in provedores]
    provedores = ['Star Plus' if 'starz' in category.lower() or 'fox' in category.lower()  else category for category in provedores]
    provedores = ['Netflix' if 'netflix' in category.lower() else category for category in provedores]
    provedores = ['FIFA+' if 'fifa' in category.lower() else category for category in provedores]
    provedores = ['Max' if 'hbo' in category.lower() else category for category in provedores]
    provedores = ['Google Play Movies' if 'google play' in category.lower() else category for category in provedores]

    provedores = ['Claro TV Plus' if category.lower() == 'claro tv+' else category for category in provedores]
    if not provedores:
        provedores = ['Outros']
    
    if pd.isna(row['date']):
        ano = ''
    else:
        ano = f"({row['date'].split('-')[0]})"
    
    if pd.notna(row['titulo']):
        arquivo = row['titulo'].replace("/", " ")
        arquivo = arquivo.replace(":", " ")
    else:
        continue
     
    provedores  = sorted(provedores)[:qtd_provedores]
    generos     = sorted(generos)[:qtd_generos]
    for genero in generos:
        if row['tipo'] == 'Filme':
            caminho = f"{out_folder}/Filmes/{provedores[0]}/{genero}/{arquivo} {ano}"
            caminho_arquivo = f"{caminho}/{arquivo} {ano}"
        else:
            if row['episodio'] is None or row['temporada'] is None:
                break
            caminho = f"{out_folder}/Series/{provedores[0]}/{genero}/{arquivo} {ano}/Season {row['temporada']:02}"
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