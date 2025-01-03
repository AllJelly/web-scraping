from tmdbv3api import TMDb, Movie, TV
from datetime import datetime
from time import sleep
import pandas as pd
import threading
import requests
import warnings
import re

warnings.simplefilter(action='ignore', category=FutureWarning)

tmdb = TMDb()
tmdb.language   = 'pt-BR'
tmdb.debug      = True
tmdb.api_key    = '6e347a3898f3f9c7250dc0a46fb27cec'
input_arq       = "./listas/lista-metadados/metadados-20241203.csv"
input_base_arq  = "./listas/lista-genero-provedor/grupo-20241231.csv"
output_arq      = "./listas/lista-genero-provedor/grupo-20241231.csv"

limit = 600
count = 0

movie = Movie()
serie = TV()

url = "https://api.themoviedb.org/3/genre/movie/list?language=pt-BR"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2ZTM0N2EzODk4ZjNmOWM3MjUwZGMwYTQ2ZmIyN2NlYyIsIm5iZiI6MTczNTU4MTg2Ni43MTksInN1YiI6IjY3NzJlMGFhNDExMTU5OWUzODEyOGViZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._AU7_JqIvhQX18nnz9lLGPzMgLKUmhvLhKa2oYu6PKs"
}

def remove_temporada_episodio(nome):
    """
    Remove o padrão ' SXX EXX' do nome e retorna a temporada e o episódio extraídos.
    """
    # Expressão regular para capturar temporada e episódio
    padrao = r'\sS(\d{2})\sE(\d+)'
    match = re.search(padrao, nome, flags=re.IGNORECASE)
    
    if match:
        temporada = int(match.group(1))  # Captura o número da temporada
        episodio = int(match.group(2))  # Captura o número do episódio
        # Remove o padrão do nome
        nome_limpo = re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()
        return nome_limpo, temporada, episodio
    return nome, None, None

def remove_ano(nome):
    # Obtém o ano atual
    ano_atual = datetime.now().year
    
    # Expressão regular para identificar e remover anos entre 1900 e o ano atual
    padrao = rf'\b(19[0-9]{{2}}|20[0-{str(ano_atual)[2]}][0-9])\b'
    
    # Substitui o ano encontrado por uma string vazia e remove espaços extras
    # Substitui o ano encontrado por uma string vazia
    nome_sem_ano = re.sub(padrao, '', nome).strip()
    
    # Se a string resultante estiver vazia, retorna o nome original
    if not nome_sem_ano:
        return nome
    
    return nome_sem_ano

def dados_tmdb(row, dados):
    try:  
        if row['tipo'] == "Filme":
            search = movie.search(str(row['name']))
        else:
            search = serie.search(re.sub(r'\sS\d{2}\sE\d{2}', '', str(row['name'])))
    
        if search:
            result = search[0]  # Considera o primeiro resultado como mais relevante
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
                
            generos_nomes = [g['name'] for g in generos if g['id'] in result['genre_ids']]
            
            # Criando um dicionário com os dados a serem adicionados à nova linha
            new_row = row.to_dict()
            if provedores is None:
                new_row["provedor"] = None
            else:
                new_row["provedor"] = ", ".join(provedores)
                
            if provedores is None:
                new_row["generos"] = None
            else:
                new_row["generos"] = ", ".join(generos_nomes)
            
            if 'release_date' in result:
                new_row["date"] = result['release_date']
            else:
                new_row["date"] = None
        else:
            new_row = row.to_dict()
            new_row["provedor"] = None
            new_row["generos"]  = None
            new_row["date"]     = None
    except Exception as e:
        print(f"Erro {str(e)} - {str(row['name'])}")
        new_row = row.to_dict()
        new_row["provedor"] = None
        new_row["generos"]  = None
        new_row["date"]     = None
    
    dados.append(new_row)

df = pd.read_csv(input_arq)

response = requests.get(url, headers=headers)
# Verificar se a resposta foi bem-sucedida
if response.status_code == 200 and not df.empty:
    # Converter a resposta em dicionário
    generos = response.json()["genres"]

    # Aplicando as transformações
    df["legendado"] = df["group-title"].apply(lambda x: True if "legendado" in x.lower() else False)

    # Criando colunas para temporada e episódio
    df[["name", "temporada", "episodio"]] = df["name"].apply(
        lambda x: pd.Series(remove_temporada_episodio(x))
    )
    df['temporada'] = df['temporada'].astype('Int64')  # Suporte para valores ausentes
    df['episodio'] = df['episodio'].astype('Int64')    # Suporte para valores ausentes
    
    df["tipo"] = df.apply(lambda row: "Filme" if pd.isna(row["temporada"]) and pd.isna(row["episodio"]) else "Série", axis=1)
    
    df["name"] = df["name"].apply(lambda x: x[:-1] if x[-1:].lower() == "." else x) # remove ponto .
    
    df["name"] = df["name"].str.replace("[-:/]", " ", regex=True)
    df["name"] = df["name"].str.replace(r"\*", "", regex=True)
    df["name"] = df["name"].str.replace(" 14temp", " ", regex=True)
    df["name"] = df["name"].str.replace(" 19 Temporada", " ", regex=True)
    df["name"] = df["name"].str.replace(" Brasil Paralelo", " ", regex=True)
    df["name"] = df["name"].str.replace("  ", " ", regex=True)
    df["name"] = df["name"].apply(remove_ano) # remove ano
    df['name'] = df['name'].str.split("  ").str[0]
    
    df["name"] = df["name"].str.strip()
    
    # Remover " leg" do nome e marcar como legendado se terminar com " leg"
    df["legendado"] = df["name"].apply(lambda x: True if x[-4:].lower() == " leg" else False)
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " leg" else x)
    df["legendado"] = df["name"].apply(lambda x: True if x[-4:].lower() == " [l]" else False)
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " [l]" else x)
    df["legendado"] = df["name"].apply(lambda x: True if x[-10:].lower() == " legendado" else False)
    df["name"] = df["name"].apply(lambda x: x[:-10] if x[-10:].lower() == " legendado" else x)
    
    df["cam"] = df["name"].apply(lambda x: True if x[-5:].lower() == " cine" or x[-4:].lower() == " cam" else False)
    df["name"] = df["name"].apply(lambda x: x[:-5] if x[-5:].lower() == " cine" else x) # cinema
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " cam" else x) # cinema
    
    df["name"] = df["name"].apply(lambda x: x[:-6] if x[-6:].lower() == " [hdr]" else x) # HDR
    df["name"] = df["name"].apply(lambda x: x[:-3] if x[-3:].lower() == " 4k" else x) # 4k
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " nac" else x) # nacionais
    
    df["dublado"] = df["name"].apply(lambda x: True if x[-4:].lower() == " dub" else False)
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " dub" else x) # dublado
    df["dublado"] = df["name"].apply(lambda x: True if x[-7:].lower() == " [dual]" else False)
    df["name"] = df["name"].apply(lambda x: x[:-7] if x[-7:].lower() == " [dual]" else x) # dublado
    df["dublado"] = df["name"].apply(lambda x: True if x[-5:].lower() == " dual" else False)
    df["name"] = df["name"].apply(lambda x: x[:-5] if x[-5:].lower() == " dual" else x) # dublado
    
    df["name"] = df["name"].apply(remove_ano) # remove ano
    
    try:
        df_out = pd.read_csv(input_base_arq)
        df = df[~df[['name', 'link']].apply(tuple, axis=1).isin(df_out[['name', 'link']].apply(tuple, axis=1))]
    except:
        df_out = pd.DataFrame(columns=df.columns.tolist() + ["provedor", "generos", "date"])

    threads, dados = [], []
    for _, row in df.iterrows():
        while threading.active_count() > 150:  # Limitar o número de threads ativas
            print("Esperando para continuar")
            sleep(1)

        thread = threading.Thread(target=dados_tmdb, args=(row, dados, ))
        threads.append(thread)
        thread.start()
        
        count = count + 1
        if count >= limit and limit != -1:
            break
    
    # Esperar todas as threads finalizarem
    print("Esperando Threads finalizarem")
    for thread in threads:
        thread.join()
    
    # Removendo duplicados e já presentes com base nas colunas 'name' e 'link'
    seen, unique_dados = set(), []
    for item in dados:
        # Criar uma chave única para comparar com o conjunto 'seen'
        chave = (item["name"], item["link"])
        if chave not in seen and not df_out[['name', 'link']].apply(lambda x: (x['name'], x['link']) == (item['name'], item['link']), axis=1).any():
            unique_dados.append(item)
            seen.add(chave)
    
    df_out = pd.concat([df_out, pd.DataFrame(unique_dados)], ignore_index=True) # Adicionando a nova linha ao DataFrame
    
    # Salvando o arquivo em CSV
    df_out.to_csv(output_arq, index=False)
    print("Arquivo CSV atualizado com estúdio e gêneros foi criado com sucesso!")
else:
    # Exibir mensagem de erro
    print(f"Erro na requisição: {response.status_code} - {response.text}")