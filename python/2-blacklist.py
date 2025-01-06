from datetime import datetime
from time import sleep
import pandas as pd
import threading
import requests
import os

# .avi: Arquivo de vídeo do Windows
# .mp4, .m4v, .mov: Arquivo de vídeo MP4
# .mpg ou .mpeg: Arquivo de filme
# .wmv: Arquivo Windows Media Video
# .mkv: Formato de vídeo
# .flv, .f4v e .swf: Formato de vídeo
# .avchd: Formato de vídeo
# .webm ou .html5: Formato de vídeo
extensao_videos = ['.avi', '.mp4', '.m4v', '.mov', '.mkv', '.mpg', '.mpeg', '.wmv', '.flv', '.f4v', '.swf', '.avchd', '.webm', '.html5']
blacklist = []

caminho     = './listas/lista/'
input_arq   = './listas/1-web-scraping/completo.csv'
output_arq  = './listas/2-lista-serie_tv/filtrado.csv'

def checkup(row, index, df, blacklist):
    try:
        if row['Link M3U'] in blacklist:
            return
    
        response = requests.get(row['Link M3U'], timeout=25)
        m3u_content = response.text
    
        qtd_video = [m3u_content.count(ext) for ext in extensao_videos if ext in m3u_content]
    
        if len(qtd_video) == 0:
            print(f"A lista contém apenas canais de TV - {row['Link M3U']}")
            blacklist.append(row['Link M3U'])
        else:
            df.loc[index, 'quantidade_videos'] = sum(qtd_video)
            print("A lista contém conteúdo sob demanda, como filmes ou séries.")
    except Exception as e:
        blacklist.append(row['Link M3U'])
        print(e)
        
try:
    df = pd.read_csv(input_arq)
    try:
        df_out = pd.read_csv(output_arq)
        df = df[~df['Link M3U'].apply(tuple, axis=1).isin(df_out['Link M3U'].apply(tuple, axis=1))]
    except:
        df_out = df
    
    df_out['quantidade_videos'] = 0

    multThread = []

    for index, row in df_out.iterrows():
        while threading.active_count() > 20:
            print("Aguardando...")
            sleep(1)  
        
        thread = threading.Thread(target=checkup, args=(row, index, df, blacklist, ))
        multThread.append(thread)
        thread.start()

    print("Esperando threads finalizarem...")
    for thread in multThread:
        thread.join()

    indices_para_remover = df[df['Link M3U'].isin(blacklist)].index

    df = df.drop(indices_para_remover)
    df_out = pd.concat([df_out, df], ignore_index=True)

    df_out = df_out.sort_values(by=['Validade'], ascending=[False])
    df_out.to_csv(output_arq, index=False, encoding='utf-8')

    # print(blacklist)
except Exception as e:
    print(str(e))