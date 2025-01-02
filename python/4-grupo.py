from tmdbv3api import TMDb, Movie, TV
from datetime import datetime
import pandas as pd
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

limit = 500
count = 0

movie = Movie()
serie = TV()

url = "https://api.themoviedb.org/3/genre/movie/list?language=pt-BR"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2ZTM0N2EzODk4ZjNmOWM3MjUwZGMwYTQ2ZmIyN2NlYyIsIm5iZiI6MTczNTU4MTg2Ni43MTksInN1YiI6IjY3NzJlMGFhNDExMTU5OWUzODEyOGViZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._AU7_JqIvhQX18nnz9lLGPzMgLKUmhvLhKa2oYu6PKs"
}

def remove_temporada_episodio(nome):
    # Expressão regular para remover o padrão ' SXX EXX' (temporada e episódio)
    return re.sub(r'\sS\d{2}\sE\d{2}', '', nome, flags=re.IGNORECASE)

def remove_ano(nome):
    # Obtém o ano atual
    ano_atual = datetime.now().year

    # Verifica se os últimos 5 caracteres correspondem a um ano válido (4 dígitos + espaço)
    if re.match(r'.*\s(\d{4})$', nome):
        ano = int(nome[-4:])
        # Verifica se o ano está dentro de uma faixa válida (exemplo: 1900 até o ano atual)
        if 1900 <= ano <= ano_atual:
            return nome[:-5]  # Remove os últimos 5 caracteres (o ano + espaço)
    return nome  # Retorna o nome original se não for um ano válido

def buscar_dados_tmdb(nome, tipo):
    try:  
        if tipo == "Filme":
            search = movie.search(str(nome))
        else:
            search = serie.search(re.sub(r'\sS\d{2}\sE\d{2}', '', str(nome)))
    
        if search:
            result = search[0]  # Considera o primeiro resultado como mais relevante
            try:
                if tipo == "Filme":
                    original_title = result['title']
                    try:
                        provedores = next([r['provider_name']for r in p['BR'][1]['flatrate']] for p in movie.watch_providers(result['id']) if p['results'] == 'BR')
                    except:
                        provedores = next([r['provider_name']for r in p['BR'][1]['rent']] for p in movie.watch_providers(result['id']) if p['results'] == 'BR')
                else:
                    original_title = nome
                    provedores = next(p['BR'][1]['flatrate'][0]['provider_name'] for p in serie.watch_providers(result['id']) if p['results'] == 'BR')
            except:
                provedores = None
                
            generos_nomes = [g['name'] for g in generos if g['id'] in result['genre_ids']]
            
            if 'release_date' in result:
                if provedores is None and generos_nomes is None:
                    return None, None, original_title, result['release_date'] # type:ignore
                elif provedores is None:
                    return None, ", ".join(generos_nomes), original_title, result['release_date'] # type:ignore
                elif generos_nomes is None:
                    return ", ".join(provedores), None, original_title, result['release_date'] # type:ignore
                else:
                    return ", ".join(provedores), ", ".join(generos_nomes), original_title, result['release_date'] # type:ignore
            else:
                if provedores is None and generos_nomes is None:
                    return None, None, original_title, None # type:ignore
                elif provedores is None:
                    return None, ", ".join(generos_nomes), original_title, None # type:ignore
                elif generos_nomes is None:
                    return ", ".join(provedores), None, original_title, None # type:ignore
                else:
                    return ", ".join(provedores), ", ".join(generos_nomes), original_title, None # type:ignore
                
    except Exception as e:
        print(f"Erro {str(e)} - {str(nome)}")
    return None, None, None, None

df = pd.read_csv(input_arq)

try:
    df_out = pd.read_csv(input_base_arq)
    df = df[~df[['group-title', 'link']].isin(df_out[['group-title', 'link']]).all(axis=1)]
except:
    df_out = pd.DataFrame(columns=df.columns.tolist() + ["provedor", "generos", "date"])
    
response = requests.get(url, headers=headers)
# Verificar se a resposta foi bem-sucedida
if response.status_code == 200 and not df.empty:
    # Converter a resposta em dicionário
    generos = response.json()["genres"]

    # Aplicando as transformações
    df["tipo"] = df["group-title"].apply(lambda x: "Filme" if "filme" in x.lower() else "Série")
    df["legendado"] = df["group-title"].apply(lambda x: True if "legendado" in x.lower() else False)

    df["name"] = df["name"].str.strip()
    df["name"] = df["name"].apply(remove_temporada_episodio)
    df["name"] = df["name"].apply(lambda x: x[:-1] if x[-1:].lower() == "." else x) # remove virgula .
    df["name"] = df["name"].apply(remove_ano) # remove ano
    
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
    
    df["name"] = df["name"].apply(remove_ano) # remove ano
    for _, row in df.iterrows():
        # Buscando os dados de TMDB
        provedor, gen, name, date = buscar_dados_tmdb(row["name"], row["tipo"])
        
        # Criando um dicionário com os dados a serem adicionados à nova linha
        new_row = row.to_dict()
        new_row["provedor"] = provedor
        new_row["generos"]  = gen
        if name != None:
            new_row["name"] = name
        if date != None:
            new_row["date"] = date
        
        # Adicionando a nova linha ao DataFrame
        df_out = pd.concat([df_out, pd.DataFrame([new_row])], ignore_index=True)
        
        count = count + 1
        if count >= limit:
            break
    
    # Salvando o arquivo em CSV
    df_out.to_csv(output_arq, index=False)
    print("Arquivo CSV atualizado com estúdio e gêneros foi criado com sucesso!")
else:
    # Exibir mensagem de erro
    print(f"Erro na requisição: {response.status_code} - {response.text}")