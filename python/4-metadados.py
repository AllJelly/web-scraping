from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import cv2
import signal
import sys

# Definições de tamanhos em bytes
_B = 1
_KB = _B * 1000
_MB = _KB * 1000
_GB = _MB * 1000

# Extensões de vídeo suportadas
extensao_videos = [
    '.avi', '.mp4', '.m4v', '.mov', '.mkv', '.mpg', '.mpeg',
    '.wmv', '.flv', '.f4v', '.swf', '.avchd', '.webm', '.html5'
]

# Arquivos de entrada e saída
input_arq = './listas/3-lista-videos/videos.csv'
output_arq = './listas/4-lista-metadados/metadados.csv'

# Variável de controle para interrupção
interrupted = False


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
        return None

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
    return {
        **row,
        "largura": width,
        "altura": height,
        "fps": fps,
        "contagem quadros": frame_count,
    }


# Registrar o manipulador de sinal para Ctrl+C
signal.signal(signal.SIGINT, handle_interrupt)

# Carregar dados de entrada
df = pd.read_csv(input_arq)
try:
    df_out = pd.read_csv(output_arq)
    df = df[~df[['name', 'link']].apply(tuple, axis=1).isin(df_out[['name', 'link']].apply(tuple, axis=1))]
except FileNotFoundError:
    df_out = pd.DataFrame(columns=df.columns.tolist())

dados = []
df = df[df["Url do Servidor"] == "http://wateronplay.com:80/"]
try:
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {}
        for _, row in df.iterrows():
            if interrupted:
                print("Interrupção detectada. Não serão lançadas novas threads.")
                break
            future = executor.submit(get_metadados, row)
            futures[future] = row

        for future in as_completed(futures):
            try:
                resultado = future.result()
                if resultado:
                    dados.append(resultado)

                # Salvar dados intermediários em lotes de 500
                if len(dados) >= 100:
                    print("Salvando dados intermediários...")
                    df_out = pd.concat([df_out, pd.DataFrame(dados)], ignore_index=True)
                    df_out.to_csv(output_arq, index=False, encoding='utf-8')
                    dados.clear()
            except Exception as e:
                print(f"Erro ao processar: {e}")

        print("Esperando threads em execução finalizarem...")
except KeyboardInterrupt:
    print("Interrupção manual detectada. Finalizando...")
finally:
    # Salvar os dados finais antes de sair
    df_out = pd.concat([df_out, pd.DataFrame(dados)], ignore_index=True)
    if 'validade' in df_out.columns:
        df_out = df_out.sort_values(by=['validade'], ascending=True)
    df_out.reset_index(drop=True, inplace=True)
    df_out.to_csv(output_arq, index=False, encoding='utf-8')
    print("Processo finalizado e dados salvos.")