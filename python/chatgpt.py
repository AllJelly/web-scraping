from time import sleep
import requests
import pandas as pd
import re  # Para usar expressões regulares

def consultar_chatgpt(nomes, api_key):
    """Consulta o ChatGPT sobre um filme e retorna a resposta."""
    url = "https://api.openai.com/v1/chat/completions"  # Endpoint para o modelo GPT-3.5 ou GPT-4
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("Executando requisição")
    # Definir o prompt com o nome do filme
    prompt = f"Quais são os provedores onde pode ser assistido, gêneros, data de lançamento e titulo conhecido das midias: {nomes}? Responda no formato n=(midia passada na pesquisa mantendo - antes e depois e entre parenteses) provedores=(lista provedores max 2 entre ()) gêneros=(lista gêneros entre ()) data_lancamento=(yyyy-mm-dd entre ()) titulo=(titulo conhecido, entre () e em português ou como é mais facil encontrado na internet ), separando cada filme por *, não imprima nada alem disso, não esqueça os ()"
    
    # Corpo da requisição
    data = {
        "model": "gpt-4o-mini",  # Substitua pelo modelo desejado
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150  # Ajuste conforme necessário
    }

    # Enviar a requisição POST para a API
    response = requests.post(url, headers=headers, json=data)
    
    # Verificar o status da resposta
    if response.status_code == 200:
        resposta = response.json()
        return resposta['choices'][0]['message']['content']
    else:
        print(response.content)
        return None

def processar_resposta(resposta, dados):
    """Processa a resposta do ChatGPT para extrair provedores, gêneros e data de lançamento."""
    print("Processando os dados")
    
    linhas = resposta.split('*')
    for linha in linhas:
        try:
            # Usar expressões regulares para capturar as informações
            match = re.search(
                r'n=\((.*?)\)\s*provedores=\((.*?)\)\s*gêneros=\((.*?)\)\s*data_lancamento=\((.*?)\)\s*titulo=\((.*?)\)',
                linha
            )
            # Se a resposta corresponder ao padrão
            if match:
                nome = match.group(1)
                provedores = match.group(2)
                generos = match.group(3)
                data_lancamento = match.group(4)
                titulo = match.group(5)
                
                dado = [nome, provedores, generos, data_lancamento, titulo]
                print(dado)
                # Retornar os dados no formato desejado
                dados.append(dado)
            else:
                print(f"ERRO: {linha}")
        except Exception as e:
            print(f"Erro ao processar resposta: {linha} - {e}")

    # Substitua 'sua_api_key_aqui' pela sua chave da API
keys = [
    # gtvzin.n7
    "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",
    # matuedamata123
    "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",
    # agnesurssula
    "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",
    # alljelly
    "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",
    # arthurcoelhoestevao442
    "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",
    # arthurcoelho442zip
    "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",
    # mocic14718@eluxeer.com
    "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",
    # lelabas955@eluxeer.com
    "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",
]

# Criar uma lista para armazenar as informações dos filmes
dados_filmes = []
arquivo = arquivo_out  = "./listas/3-lista-videos/videos-ajustado.csv"

df          = pd.read_csv(arquivo)
# Filtrar as linhas onde as colunas 'provedor' e 'generos' são nulas
df_filtered = df[df['provedor'].isna() & df['generos'].isna()]
# Remover duplicatas na coluna 'name', mantendo apenas a primeira ocorrência
df_unique   = df_filtered.drop_duplicates(subset='name', keep='first')

midias = list(df_unique['name'])

passo = 2
init  = 0
dados = []
try:
    while (True):
        dados.clear()
        for api_key in keys:
            for i in range(init, len(midias), passo):
                nomes = midias[i:i+passo]
                init = i
                
                if nomes is None:
                    continue
                resposta = consultar_chatgpt(nomes, api_key)
                if resposta is None:
                    break
                
                # Processar a resposta para extrair provedores, gêneros e data de lançamento
                processar_resposta(resposta, dados)
                if len(dados) > 500:
                    break
                else:
                    sleep(20)
        print(dados)
        for dado in dados:
            df.loc[df['name'] == dado[0], ['provedor','generos', 'date', 'titulo']] = [dado[1], dado[2], dado[3], dado[4]]
            
        # Preenchendo o provedor baseado no título
        df["provedor"]  = df.groupby("name")["provedor"].transform("first")
        df["generos"]   = df.groupby("name")["generos"].transform("first")
        
        # Salvar os dados finais antes de sair
        df = df.sort_values(by=['validade', 'name'], ascending=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(arquivo_out, index=False, encoding='utf-8')

        print(f"Dados exportados para '{arquivo_out}'")
        
        if init >= len(midias):
            print("Todos os dados foram alocados, finalizando")
            break
        print("Dormindo ...")
        print(f"Quantidade de dados que faltam {len(midias)-init}")     
        sleep(60*2)
except KeyboardInterrupt:
    print("interrompido")

print(dados)
for dado in dados:
    df.loc[df['name'] == dado[0], ['provedor','generos', 'date', 'titulo']] = [dado[1], dado[2], dado[3], dado[4]]
# Preenchendo o provedor baseado no título
df["provedor"]  = df.groupby("name")["provedor"].transform("first")
df["generos"]   = df.groupby("name")["generos"].transform("first")

# Salvar os dados finais antes de sair
df = df.sort_values(by=['validade', 'name'], ascending=True)
df.reset_index(drop=True, inplace=True)
df.to_csv(arquivo_out, index=False, encoding='utf-8')

print(f"Dados exportados para '{arquivo_out}'")
print(f"Quantidade de dados que faltam {len(midias)-init}")     
# 'não disponível'