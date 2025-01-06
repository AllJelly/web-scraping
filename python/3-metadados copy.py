from time import sleep
import pandas as pd
import threading
import requests
import cv2
import re

_B   = 1
_KB  = _B * 1000
_MB  = _KB * 1000
_GB  = _MB * 1000

# .avi: Arquivo de vídeo do Windows
# .mp4, .m4v, .mov: Arquivo de vídeo MP4
# .mpg ou .mpeg: Arquivo de filme
# .wmv: Arquivo Windows Media Video
# .mkv: Formato de vídeo
# .flv, .f4v e .swf: Formato de vídeo
# .avchd: Formato de vídeo
# .webm ou .html5: Formato de vídeo
extensao_videos = ['.avi', '.mp4', '.m4v', '.mov', '.mkv', '.mpg', '.mpeg', '.wmv', '.flv', '.f4v', '.swf', '.avchd', '.webm', '.html5']
input_arq = './listas/2-lista-serie_tv/filtrado.csv'
output_arq = './listas/3-lista-metadados/metadados.csv'


def get_metadados(infos, link, dados):
    if infos.startswith("#EXTINF") and any([True for ext in extensao_videos if ext in link]):       
        match = re.search(r'tvg-name="([^"]*)".*?tvg-logo="([^"]*)".*?group-title="([^"]*)"', infos)
        if match:
            try:
                response = requests.get(link, stream=True, timeout=30)
                if response.status_code != 200:
                    return
            except:
                return
            
            tvg_name = str(re.sub(r'\s*\([^)]*\)', '', match.group(1)))              
            tvg_logo = match.group(2)
            group_title = match.group(3)

            cap = cv2.VideoCapture(link)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
            else:
                width       = None
                height      = None
                fps         = None
                frame_count = None
                
            size = response.headers.get('Content-Length', None)
            if size:
                size = round(int(size) / _GB, 6)
            else:
                size = None
                
            print(f"Dados encontrados - {tvg_name} {width}x{height} ({size})")
            dados.append({
                'name': f"{tvg_name}",
                'group-title': group_title,
                'logo-link': tvg_logo,
                'link': link,
                "largura": width,
                "altura": height,
                "fps": fps,
                "contagem quadros": frame_count,
                "tamanho_GB": size,
                "ano": re.search(r'\(([^)]*)\)', match.group(1))
            })
def get_lista(row, df_out, dados):
    try:
        response = requests.get(row['Link M3U'], timeout=25)
        if response.status_code != 200:
            return
        print(f"Lista encontrado - {row['Link M3U']}")
        m3u_content = response.text
        lines = m3u_content.splitlines()
        multThread_local = []
        for i in range(1, len(lines), 2):
            if threading.active_count() > 15:
                sleep(0.1)
            if lines[i+1] in df_out['link'].values:
                continue
            thread = threading.Thread(target=get_metadados, args=(lines[i], lines[i+1], dados, ))
            multThread_local.append(thread)
            thread.start()
        for thread in multThread_local:
            thread.join()
    except Exception as e:
        print(str(e))

df      = pd.read_csv(input_arq)
df_out  = pd.read_csv(output_arq)
dados, multThread = [], []
for _, row in df.iterrows():
    if threading.active_count() > 5:
        sleep(1)
    thread = threading.Thread(target=get_lista, args=(row, df_out, dados, ))
    multThread.append(thread)
    thread.start()
    
print("Esperando Threads finalizarem")
for thread in multThread:
    thread.join()

df_out = pd.concat([df_out, pd.DataFrame(dados)], ignore_index=True)
df.to_csv(output_arq, index=False, encoding='utf-8')