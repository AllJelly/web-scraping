from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import pandas as pd
import requests
import signal

_B   = 1
_KB  = _B * 1000
_MB  = _KB * 1000
_GB  = _MB * 1000

# Variável de controle para interrupção
interrupted = False
arquivo     = "./listas/3-lista-videos/videos-2.csv"

def handle_interrupt(signal_received, frame):
    """
    Função para capturar o sinal de interrupção (Ctrl+C).
    """
    global interrupted
    print("\nInterrupção detectada. Finalizando após concluir threads em execução...")
    interrupted = True

def verificacao(row):
    """
    Função para extrair metadados de vídeo.
    """
    if interrupted:
        return row
    try:
        response = requests.get(row["link"], stream=True, timeout=30)
        if response.status_code != 200:
            row['ativo'] = False
            return row
    except:
        row['ativo'] = False
        return row
    
    size = response.headers.get('Content-Length', None)
    print(f"Tamanho encontrado {row["title"]} - ({size})")
    if size:
        row['tamanho_GB'] = round(int(size) / _GB, 6)
        row['ativo'] = True
    else:
        row['ativo'] = False
    return row

# Registrar o manipulador de sinal para Ctrl+C
signal.signal(signal.SIGINT, handle_interrupt)

df = pd.read_csv(arquivo)

try:
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}
        for _, row in df.iterrows():
            if interrupted:
                print("Interrupção detectada. Não serão lançadas novas threads.")
                break
            future = executor.submit(verificacao, row)
            futures[future] = row

        for future in as_completed(futures):
            try:
                row = future.result()
                df.loc[df['link'] == row['link'], ['tamanho_GB', 'ativo']] = [row['tamanho_GB'], row['ativo']]
            except Exception as e:
                print(f"Erro ao processar: {e}")

        print("Esperando threads em execução finalizarem...")
except KeyboardInterrupt:
    print("Interrupção manual detectada. Finalizando...")
finally:    
    # Salvar os dados finais antes de sair
    df = df.sort_values(by=['validade', 'name'], ascending=True)
    df.reset_index(drop=True, inplace=True)
    df.to_csv(arquivo, index=False, encoding='utf-8')
    print("Processo finalizado e dados salvos.")