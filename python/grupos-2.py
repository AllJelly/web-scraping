from concurrent.futures import ThreadPoolExecutor, as_completed
from tmdbv3api import TMDb, Movie, TV
import unicodedata
from datetime import datetime
from time import sleep
import pandas as pd
import threading
import requests
import warnings
import signal
import re

# Variável de controle para interrupção
interrupted = False

warnings.simplefilter(action='ignore', category=FutureWarning)

tmdb = TMDb()
tmdb.language   = 'pt-BR'
tmdb.debug      = True
tmdb.api_key    = '6e347a3898f3f9c7250dc0a46fb27cec'
arquivo         = "./listas/3-lista-videos/videos-2.csv"

limit = 600
count = 1
n_encontrados = 0

movie = Movie()
serie = TV()

url = "https://api.themoviedb.org/3/genre/movie/list?language=pt-BR"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2ZTM0N2EzODk4ZjNmOWM3MjUwZGMwYTQ2ZmIyN2NlYyIsIm5iZiI6MTczNTU4MTg2Ni43MTksInN1YiI6IjY3NzJlMGFhNDExMTU5OWUzODEyOGViZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._AU7_JqIvhQX18nnz9lLGPzMgLKUmhvLhKa2oYu6PKs"
}

def handle_interrupt(signal_received, frame):
    """
    Função para capturar o sinal de interrupção (Ctrl+C).
    """
    global interrupted
    print("\nInterrupção detectada. Finalizando após concluir threads em execução...")
    interrupted = True

def dados_tmdb(row):
    """
    Função para extrair dados do tmdb.
    """
    
    global n_encontrados
    
    if interrupted:
        return row
    
    if " rock in rio" in row['name'].lower() or  " rock the mountain" in row['name'].lower():
        row['titulo'] = row['name']
        return row
    
    # Criando um dicionário com os dados a serem adicionados à nova linha
    try:  
        if row['tipo'] == "Filme":
            search = movie.search(str(row['name']))
        else:
            search = serie.search(re.sub(r'\sS\d{2}\sE\d{2}', '', str(row['name'])))
    
        if search:
            result = search[0]  # Considera o primeiro resultado como mais relevante
            try:
                row['titulo'] = result['title']
            except:
                try:
                    row['titulo'] = result['name']
                except Exception as e:
                    row['titulo'] = row['name']
                    print(str(e))
            try:
                if row['tipo'] == "Filme":
                    try:
                        provedores = next([r['provider_name']for r in p['BR'][1]['flatrate']] for p in movie.watch_providers(result['id']) if p['results'] == 'BR')
                    except:
                        provedores = next([r['provider_name']for r in p['BR'][1]['rent']] for p in movie.watch_providers(result['id']) if p['results'] == 'BR')
                else:
                    provedores = next(p['BR'][1]['flatrate'][0]['provider_name'] for p in serie.watch_providers(result['id']) if p['results'] == 'BR')
            except:
                provedores = None
            
            if provedores is not None:
                row["provedor"] = ", ".join(provedores)
                
            if 'genre_ids' in result and result['genre_ids'] is not None:
                generos_nomes = [g['name'] for g in generos if g['id'] in result['genre_ids']]
                row["generos"] = ", ".join(generos_nomes)
            
            if 'release_date' in result:
                row["date"] = result['release_date']
        else:
            row['titulo'] = row['name']
    except Exception as e:
        print(f"Erro {str(e)} - {str(row['name'])}")
        row['titulo'] = row['name']
        n_encontrados += 1
    return row
        
# Registrar o manipulador de sinal para Ctrl+C
signal.signal(signal.SIGINT, handle_interrupt)

df = pd.read_csv(arquivo)

response = requests.get(url, headers=headers)
# Verificar se a resposta foi bem-sucedida
if response.status_code == 200 and not df.empty:
    # Converter a resposta em dicionário
    generos = response.json()["genres"]
    
    df["provedor"]  = df.groupby("titulo")["provedor"].transform("first")
    df["generos"]   = df.groupby("titulo")["generos"].transform("first")
    
    # Filtrar as linhas onde as colunas 'provedor' e 'generos' são nulas
    df_filtered = df[df['provedor'].isna() & df['generos'].isna()]

    # Remover duplicatas na coluna 'name', mantendo apenas a primeira ocorrência
    df_unique = df_filtered.drop_duplicates(subset='name', keep='first')
    try:
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {}
            for _, row in df_unique.iterrows():
                if interrupted:
                    print("Interrupção detectada. Não serão lançadas novas threads.")
                    break
                future = executor.submit(dados_tmdb, row)
                futures[future] = row
                
                if not (" rock in rio" in row['name'].lower() or " rock the mountain" in row['name'].lower()):
                    count = count + 1
                    
                if count > limit:
                    break

            for future in as_completed(futures):
                try:
                    row = future.result()
                    df.loc[df['name'] == row['name'], ['date', 'provedor','generos', 'titulo']] = [row['date'], row['provedor'], row['generos'], row['titulo']]
                except Exception as e:
                    print(f"Erro ao processar: {e}")

            print(f"Esperando threads em execução finalizarem... (não encontrados - {n_encontrados})")
    except KeyboardInterrupt:
        print("Interrupção manual detectada. Finalizando...")
    finally:                
        # Preenchendo o provedor baseado no título
        df["provedor"]  = df.groupby("titulo")["provedor"].transform("first")
        df["generos"]   = df.groupby("titulo")["generos"].transform("first")
        
        # Salvar os dados finais antes de sair
        df = df.sort_values(by=['validade', 'name'], ascending=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(arquivo, index=False, encoding='utf-8')
        print("Processo finalizado e dados salvos.")