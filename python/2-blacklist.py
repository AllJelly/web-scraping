from datetime import datetime
from time import sleep
import pandas as pd
import threading
import requests
import os

extensao_videos = ['.avi', '.mp4', '.mov', '.mkv']
blacklist = []

caminho = './listas/lista/'

arquivos = os.listdir(caminho)

arquivos_csv = [arquivo for arquivo in arquivos if arquivo.startswith('completa-') and arquivo.endswith('.csv')]

arquivo_mais_recente = ''
data_arquivo = None

for arquivo in arquivos_csv:
    data_str = arquivo.split('-')[-1].replace('.csv', '')
    
    data_atual = datetime.strptime(data_str, '%Y%m%d')
    
    if data_arquivo is None or data_atual > data_arquivo:
        data_arquivo = data_atual
        arquivo_mais_recente = arquivo

if data_arquivo is not None:
    df = pd.read_csv(caminho+arquivo_mais_recente)

    df['quantidade_videos'] = 0

    def checkup(row, index, df, blacklist):
        try:
            if row['Url do Servidor'] in blacklist:
                return
            
            response = requests.get(row['Link M3U'], timeout=60*2)
            m3u_content = response.text
            
            qtd_video = [m3u_content.count(ext) for ext in extensao_videos if ext in m3u_content]
            
            if len(qtd_video) == 0:
                print(f"A lista contém apenas canais de TV - {row['Link M3U']}")
                blacklist.append(row['Url do Servidor'])
            else:
                df.loc[index, 'quantidade_videos'] = sum(qtd_video)
                print("A lista contém conteúdo sob demanda, como filmes ou séries.")
        except Exception as e:
            blacklist.append(row['Link M3U'])
            print(e)

    multThread = []

    for index, row in df.iterrows():
        while threading.active_count() > 20:
            sleep(0.1)  
            
        thread = threading.Thread(target=checkup, args=(row, index, df, blacklist, ))
        multThread.append(thread)
        thread.start()

    for thread in multThread:
        thread.join()

    indices_para_remover = df[df['Link M3U'].isin(blacklist)].index.append(df[df['Url do Servidor'].isin(blacklist)].index)

    df = df.drop(indices_para_remover)

    df = df.sort_values(by=['Validade'], ascending=[False])

    df.to_csv(f'./listas/lista-serie_tv/filtrado-{data_arquivo.year}{data_arquivo.month}{data_arquivo.day}.csv', index=False, encoding='utf-8')

    print(blacklist)