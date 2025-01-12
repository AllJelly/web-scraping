import os
import unidecode

# Caminho da pasta com os arquivos
pasta_provedor = "./biblioteca/provedor"
pasta_genero = "./biblioteca/genero"

provedores = ["Amazon Prime Video", "Apple TV Plus", "Belas Artes a La Carte", "Claro TV Plus", 
              "Claro video", "Crunchyroll", "Disney Plus", "FilmBox+", "Globoplay", "Google Play Movies", "Kocowa",
              "Looke", "Max", "MUBI", "Netflix", "Oldflix", "Outros", "Paramount Plus", "Reserva Imovision", "Univer Video", "Kinopop"]

generos = ["Ação", "Animação", "Aventura", "Comédia", 
           "Crime", "Documentário", "Drama", "Família", "Fantasia", "Faroeste", "Ficção científica",
           "Guerra", "História", "Mistério", "Romance", "Outros", "Suspense", "Terror"]

# Palavra base para substituição
palavra_base = "base"

def troca_nome_em_arquivos(arquivo, pasta, tipos):
    caminho_arquivo = os.path.join(pasta, arquivo)
    
    # Verifica se é um arquivo
    if os.path.isfile(caminho_arquivo):
        # Abre o arquivo para leitura
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        
        for tipo in tipos:
            # Substitui todas as ocorrências da palavra base pelo nome sem acentos
            tipo_sem_acentos = unidecode.unidecode(tipo)
            conteudo_modificado = conteudo.replace(palavra_base, tipo_sem_acentos)
            
            # Substitui a palavra base no nome do arquivo, se existir
            novo_nome_arquivo = arquivo.replace(palavra_base, tipo_sem_acentos)
            
            # Caminho de saída para o arquivo
            caminho_arquivo_out = os.path.join(f"{pasta}/{tipo}", novo_nome_arquivo)
            
            # Cria o diretório se ele não existir
            os.makedirs(os.path.dirname(caminho_arquivo_out), exist_ok=True)
            
            # Salva o conteúdo modificado no novo arquivo
            with open(caminho_arquivo_out, 'w', encoding='utf-8') as file:
                file.write(conteudo_modificado)

# Percorre todos os arquivos da provedor
for arquivo in os.listdir(pasta_provedor):
    troca_nome_em_arquivos(arquivo, pasta_provedor, provedores)

# Percorre todos os arquivos da gênero
for arquivo in os.listdir(pasta_genero):
    troca_nome_em_arquivos(arquivo, pasta_genero, generos)

print("Substituições concluídas!")