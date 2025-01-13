from time import sleep
import pandas as pd
import threading
import requests
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
output_arq = './listas/3-lista-videos/videos.csv'
count = 0

def get_metadados(infos, link, dados, url_servidor, validade, df_out):
    match = re.search(r'tvg-name="([^"]*)".*?tvg-logo="([^"]*)".*?group-title="([^"]*)"', infos)
    if match:
        tvg_name = str(re.sub(r'\s*\([^)]*\)', '', match.group(1)))              
        tvg_logo = match.group(2)
        group_title = match.group(3)
        
        if (url_servidor, tvg_name) in df_out[['Url do Servidor', 'name']].itertuples(index=False, name=None):
            mask = (df_out['Url do Servidor'] == url_servidor) & (df_out['name'] == tvg_name)
            if df_out.loc[mask, 'link'].values[0] != link:
                df_out.loc[mask, 'link'] = link
            return df_out
        try:
            response = requests.get(link, stream=True, timeout=30)
            if response.status_code != 200:
                return 
        except:
            return
        
        size = response.headers.get('Content-Length', None)
        if size:
            size = round(int(size) / _GB, 6)
            
            if size == 0.002033:
                return
        else:
            size = None
            
        print(f"Dados encontrados - {tvg_name} ({size})")
        dados.append({
            'Url do Servidor': url_servidor,
            'name': f"{tvg_name}",
            'group-title': group_title,
            'logo-link': tvg_logo,
            'link': link,
            'validade': validade,
            'tamanho_GB': size,
        })

df = pd.read_csv(input_arq)
try:
    df_out = pd.read_csv(output_arq)
except:
    df_out = pd.DataFrame(columns=["Url do Servidor", "name", "group-title", "logo-link", "link", "validade", "tamanho_GB"])
dados, multThread = [], []
for _, row in df.iterrows():
    try:
        response = requests.get(row['Link M3U'], timeout=25)
        if response.status_code != 200:
            continue
        print(f"Lista encontrado - {row['Link M3U']}")
        m3u_content = response.text
        lines = m3u_content.splitlines()
        for i in range(1, len(lines), 2):
            if threading.active_count() > 40:
                sleep(0.1)
            if lines[i+1] in df_out['link'].values or any(dirc.get('link') == lines[i + 1] for dirc in dados):
                continue
            if lines[i].startswith("#EXTINF") and any([True for ext in extensao_videos if ext in lines[i+1]]): 
                thread = threading.Thread(target=get_metadados, args=(lines[i], lines[i+1], dados, row['Url do Servidor'], row['Validade'], df_out, ))
                multThread.append(thread)
                thread.start()
                count+=1
                if count > 1000 and len(dados) > 0:
                    df_out = pd.concat([df_out, pd.DataFrame(dados)], ignore_index=True)
                    df_out.to_csv(output_arq, index=False, encoding='utf-8')
                    count = 0
                    dados = []
    except Exception as e:
        print(e)

print("Esperando Threads finalizarem...")
for thread in multThread:
    try:
        thread.join()
    except:
        thread.join()
try:
    if len(dados) > 0:  
        df_out = pd.concat([df_out, pd.DataFrame(dados)], ignore_index=True)
    df_out = df_out.sort_values(by=['name'], ascending=[False])
    df_out.reset_index(drop=True, inplace=True)
except:
    pass
df_out.to_csv(output_arq, index=False, encoding='utf-8')
    