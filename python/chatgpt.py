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

    # Definir o prompt com o nome do filme
    prompt = f"Quais são os provedores onde pode ser assistido, gêneros, data de lançamento e titulo conhecido dos filmes '{nomes}'? Responda no formato provedores=(lista provedores) generos=(lista gêneros) data_lancamento=(yyyy-mm-dd) titulo=(titulo conhecido), separando cada filme por quebra de linha \\n, não imprima nada alem disso"
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

def processar_resposta(nomes, resposta, dados):
    """Processa a resposta do ChatGPT para extrair provedores, gêneros e data de lançamento."""
    
    linhas = resposta.split('\n')
    for nome, linha in zip(nomes, linhas):
        try:
            # Usar expressões regulares para capturar as informações
            match = re.search(r'provedores=\(([^)]+)\).*?generos=\(([^)]+)\).*?data_lancamento=\(([^)]+)\)titulo=\(([^)]+)\)', linha)
            
            # Se a resposta corresponder ao padrão
            if match:
                provedores = match.group(1)
                generos = match.group(2)
                data_lancamento = match.group(3)
                titulo = match.group(3)
                
                # Retornar os dados no formato desejado
                dados.append([nome, provedores, generos, data_lancamento, titulo])
        except Exception as e:
            print(f"Erro ao processar resposta: {nome} - {e}")

# Substitua 'sua_api_key_aqui' pela sua chave da API
api_key = "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"

# Criar uma lista para armazenar as informações dos filmes
dados_filmes = []
arquivo      = "./listas/3-lista-videos/videos-3.csv"
arquivo_out  = "./listas/3-lista-videos/videos-ajustado.csv"

df           = pd.read_csv(arquivo)
# Filtrar as linhas onde as colunas 'provedor' e 'generos' são nulas
# df_filtered = df[df['provedor'].isna() & df['generos'].isna()]
# Remover duplicatas na coluna 'name', mantendo apenas a primeira ocorrência
# df_unique = df_filtered.drop_duplicates(subset='name', keep='first')
df_unique = df.drop_duplicates(subset='name', keep='first')

midias = list(df_unique['name'])
passo = 4000
dados = []
for i in range(0, len(midias), passo):
    nomes = midias[i:i+passo]
    
    if nomes is None:
        continue
    resposta = consultar_chatgpt(nomes, api_key)
    if resposta is None:
        continue
    
    # Processar a resposta para extrair provedores, gêneros e data de lançamento
    processar_resposta(nomes, resposta, dados)

for dado in dados:
    df.loc[df['name'] == dado[0], ['provedor','generos', 'date', 'titulo']] = [dado[1], dado[2], dado[3], dado[4]]
    
 # Preenchendo o provedor baseado no título
df["provedor"]  = df.groupby("name")["provedor"].transform("first")
df["generos"]   = df.groupby("name")["generos"].transform("first")

# Salvar os dados finais antes de sair
df = df.sort_values(by=['validade', 'name'], ascending=True)
df.reset_index(drop=True, inplace=True)
df.to_csv(arquivo_out, index=False, encoding='utf-8')
        
        
        
        
        
        
        
        
        
# # Consultar o ChatGPT para cada filme e armazenar os resultados
# for filme in filmes:
#     resposta = consultar_chatgpt(filme, api_key)
#     print(f"Resposta para '{filme}':")
#     print(resposta)
#     print("="*50)  # Separador para clareza
    
#     # Processar a resposta para extrair provedores, gêneros e data de lançamento
#     provedores, generos, data_lancamento = processar_resposta(resposta)
    
#     # Adicionar as informações ao list
#     dados_filmes.append([filme, provedores, generos, data_lancamento])

# # Criar o DataFrame com os dados
# df_filmes = pd.DataFrame(dados_filmes, columns=["name", "provedores", "generos", "date"])

# # Exportar para CSV
# df_filmes.to_csv(arquivo_out, index=False, encoding='utf-8')

print(f"Dados exportados para '{arquivo_out}'")