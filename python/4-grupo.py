from tmdbv3api import TMDb, Movie, TV
import pandas as pd
import requests
import time
import re

tmdb = TMDb()
tmdb.language   = 'pt-BR'
tmdb.debug      = True
tmdb.api_key    = '6e347a3898f3f9c7250dc0a46fb27cec'
input_arq       = "./listas/lista-metadados/metadados-20241110.csv"
output_arq       = "./listas/lista-genero-provedor/grupo-20241231.csv"

url = "https://api.themoviedb.org/3/genre/movie/list?language=pt-BR"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2ZTM0N2EzODk4ZjNmOWM3MjUwZGMwYTQ2ZmIyN2NlYyIsIm5iZiI6MTczNTU4MTg2Ni43MTksInN1YiI6IjY3NzJlMGFhNDExMTU5OWUzODEyOGViZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._AU7_JqIvhQX18nnz9lLGPzMgLKUmhvLhKa2oYu6PKs"
}

movie = Movie()
serie = TV()

response = requests.get(url, headers=headers)
# Verificar se a resposta foi bem-sucedida
if response.status_code == 200:
    # Converter a resposta em dicionário
    generos = response.json()["genres"]

    # Função para buscar dados da midia
    def buscar_dados_tmdb(nome, tipo):
        time.sleep(0.1)
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
        except Exception as e:
            print(f"Erro {str(e)} - {str(nome)}")
        return None, None, None  

    df = pd.read_csv(input_arq)
    # df = df.iloc[19:20,:]
    
    # Aplicando as transformações
    df["tipo"] = df["group-title"].apply(lambda x: "Filme" if "Filmes" in x else "Série")
    df["legendado"] = df["group-title"].apply(lambda x: True if "legendado" in x.lower() else False)

    # Remover " leg" do nome e marcar como legendado se terminar com " leg"
    df["legendado"] = df["name"].apply(lambda x: True if x[-4:].lower() == " leg" else False)
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " leg" else x) # legendado
    df["name"] = df["name"].apply(lambda x: x[:-3] if x[-3:].lower() == " 4k" else x) # 4k
    df["name"] = df["name"].apply(lambda x: x[:-4] if x[-4:].lower() == " nac" else x) # nacionais
    
    df["name"] = df["name"].apply(lambda x: x[:-5] if x[-5:].lower() in [" 2020", " 2021", " 2022"," 2023"," 2024"] else x) # anos

    for index, row in df.iterrows():
        df.at[index, "provedor"], df.at[index, "generos"], df.at[index, "name"] = buscar_dados_tmdb(row["name"], row["tipo"])
        
    # Salvando o arquivo em CSV
    df.to_csv(output_arq, index=False)
    print("Arquivo CSV atualizado com estúdio e gêneros foi criado com sucesso!")
else:
    # Exibir mensagem de erro
    print(f"Erro na requisição: {response.status_code} - {response.text}")