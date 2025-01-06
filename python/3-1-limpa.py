from time import sleep
import pandas as pd
import threading
import requests

arq  = './listas/2-lista-serie_tv/filtrado.csv'

df = pd.read_csv(arq)

def req(link, remover):
    try:
        response = requests.get(link, timeout=30)
        if response.status_code == 200:
            print(f"Link funcionando - {link}")
            return
    except:
        pass
    remover.append(link)

df = df.drop_duplicates(subset='Link M3U', keep='first').reset_index(drop=True)
df.reset_index(drop=True, inplace=True)

remover, multThread = [], []
for _, row in df.iterrows():
    if threading.active_count() > 30:
        sleep(1)
    thread = threading.Thread(target=req, args=(row["Link M3U"], remover, ))
    multThread.append(thread)
    thread.start()
    
print("Esperando Threads finalizarem")
for thread in multThread:
    thread.join()
     
indices_para_remover = df[df['Link M3U'].isin(remover)].index
df = df.drop(indices_para_remover)
df.reset_index(drop=True, inplace=True)

df.to_csv(arq, index=False)