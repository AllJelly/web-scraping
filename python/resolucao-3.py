from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import signal
import cv2

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

def get_metadados(row):
    """
    Função para extrair metadados de vídeo.
    """
    if interrupted:
        return row

    try:
        cap = cv2.VideoCapture(row['link'])
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
        else:
            width = height = fps = frame_count = None
    except Exception:
        width = height = fps = frame_count = None

    print(f"Dados encontrados - {row['name']} {width}x{height}")
    row["largura"]          = width
    row["altura"]           = height
    row["fps"]              = fps
    row["contagem quadros"] = frame_count
    return row

# Registrar o manipulador de sinal para Ctrl+C
signal.signal(signal.SIGINT, handle_interrupt)

df = pd.read_csv(arquivo)

# Filtrar as linhas onde as colunas 'provedor' e 'generos' são nulas
df_filtered = df[df['largura'].isna() & df['altura'].isna()]

try:
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {}
        for _, row in df_filtered.iterrows():
            if interrupted:
                print("Interrupção detectada. Não serão lançadas novas threads.")
                break
            future = executor.submit(get_metadados, row)
            futures[future] = row

        for future in as_completed(futures):
            try:
                row = future.result()
                df.loc[df['link'] == row['link'], ['largura', 'altura','fps', 'contagem quadros']] = [row['largura'], row['altura'], row['fps'], row['contagem quadros']]
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