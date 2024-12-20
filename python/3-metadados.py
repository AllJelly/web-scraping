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

input_arq = './listas/lista-serie_tv/filtrado-2024113.csv'
output_arq = './listas/lista-metadados/metadados-20241203.csv'

def get_metadados(infos, link, dados):
    if infos.startswith("#EXTINF") and any([True for ext in extensao_videos if ext in link]):       
        match = re.search(r'tvg-name="([^"]*)".*?tvg-logo="([^"]*)".*?group-title="([^"]*)"', infos)
        if match:
            try:
                response = requests.get(link, stream=True)
                if response.status_code != 200:
                    return
            except:
                return
            
            cap = cv2.VideoCapture(link)
            if not cap.isOpened():
                return
            
            tvg_name = str(re.sub(r'\s*\([^)]*\)', '', match.group(1)))              
            tvg_logo = match.group(2)
            group_title = match.group(3)

            size = response.headers.get('Content-Length', None)
            if size:
                size = round(int(size) / _GB, 6)
            else:
                size = None
                
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
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

df = pd.read_csv(input_arq)
extensao_videos = ['.avi', '.mp4', '.mov', '.mkv']

try:
    dados = pd.read_csv(output_arq)
    dados = dados.to_dict(orient="records")
except:
    dados = []
    
for index, row in df.iterrows():
    try:
        response = requests.get(row['Link M3U'], timeout=10)
        m3u_content = response.text

        lines = m3u_content.splitlines()
        multThread = []
        for i in range(1, len(lines), 2):
            if threading.active_count() > 20:
                sleep(0.1)
            thread = threading.Thread(target=get_metadados, args=(lines[i], lines[i+1], dados, ))
            multThread.append(thread)
            thread.start()

        print("Esperando Threads finalizarem")
        for thread in multThread:
            thread.join()
    except Exception as e:
        print(e)

df =  pd.DataFrame(dados)
df.to_csv(output_arq, index=False, encoding='utf-8')