from tmdbv3api import TMDb, Movie, TV
import pandas as pd
import requests
import warnings
import re

warnings.simplefilter(action='ignore', category=FutureWarning)

tmdb = TMDb()
tmdb.language   = 'pt-BR'
tmdb.debug      = True
tmdb.api_key    = '6e347a3898f3f9c7250dc0a46fb27cec'
input_arq       = "./listas/lista-metadados/metadados-20241110.csv"
input_base_arq  = "./listas/lista-genero-provedor/grupo-20241231.csv"
output_arq      = "./listas/lista-genero-provedor/grupo-20241231.csv"

movie = Movie()
serie = TV()

url = "https://api.themoviedb.org/3/genre/movie/list?language=pt-BR"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2ZTM0N2EzODk4ZjNmOWM3MjUwZGMwYTQ2ZmIyN2NlYyIsIm5iZiI6MTczNTU4MTg2Ni43MTksInN1YiI6IjY3NzJlMGFhNDExMTU5OWUzODEyOGViZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._AU7_JqIvhQX18nnz9lLGPzMgLKUmhvLhKa2oYu6PKs"
}

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
            
            if provedores is None and generos_nomes is None:
                return None, None, original_title # type:ignore
            elif provedores is None:
                return None, ", ".join(generos_nomes), original_title # type:ignore
            elif generos_nomes is None:
                return ", ".join(provedores), None, original_title # type:ignore
            else:
                return ", ".join(provedores), ", ".join(generos_nomes), original_title # type:ignore
                
    except Exception as e:
        print(f"Erro {str(e)} - {str(nome)}")
    return None, None, None  

df = pd.read_csv(input_arq)
df_out = pd.read_csv(input_base_arq)
if df_out.empty: 
    df_out = pd.DataFrame(columns=df.columns.tolist() + ["provedor", "generos"])
else:
    df = df[~df[['group-title', 'link']].isin(df_out[['group-title', 'link']]).all(axis=1)]

response = requests.get(url, headers=headers)
# Verificar se a resposta foi bem-sucedida
if response.status_code == 200 and not df.empty:
    # Converter a resposta em dicionário
    generos = response.json()["genres"]

    # Aplicando as transformações
    df["tipo"] = df["group-title"].apply(lambda x: "Filme" if "Filmes" in x else "Série")
    df["legendado"] = df["group-title"].apply(lambda x: True if "legendado" in x.lower() else False)

    # Remover " leg" do nome e marcar como legendado se terminar com " leg"
    df["legendado"] = df["name"].apply(lambda x: True if x[-4:].lower() == " leg" else False)
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " leg" else x) # legendado
    df["name"] = df["name"].apply(lambda x: x[:-3] if x[-3:].lower() == " 4k" else x) # 4k
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " nac" else x) # nacionais
    df["name"] = df["name"].apply(lambda x: x[:-5] if x[-5:].lower() == " nac." else x) # nacionais
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " dub" else x) # dublado
    df["name"] = df["name"].apply(lambda x: x[:-5] if x[-5:].lower() == " cine" else x) # cinema
    
    df["name"] = df["name"].apply(lambda x: x[:-5] if x[-5:].lower() in [" 2020", " 2021", " 2022"," 2023"," 2024"] else x) # anos

    limit = 500
    count = 0
    for _, row in df.iterrows():
        # Buscando os dados de TMDB
        provedor, gen, name = buscar_dados_tmdb(row["name"], row["tipo"])
        
        # Criando um dicionário com os dados a serem adicionados à nova linha
        new_row = row.to_dict()
        new_row["provedor"] = provedor
        new_row["generos"] = gen
        if name != None:
            new_row["name"] = name
        
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