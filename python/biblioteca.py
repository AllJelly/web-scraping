import os

# Caminho da pasta com os arquivos
pasta = "./biblioteca/provedor"

provedores = ["Amazon Prime Video", "Apple TV Plus", "Belas Artes a La Carte", "Claro TV Plus", 
              "Claro video", "Crunchyroll", "Disney Plus", "FilmBox+", "Globoplay", "Google Play Movies", "Kocowa",
              "Looke", "Max", "MUBI", "Netflix", "Oldflix", "Outros", "Paramount Plus", "Reserva Imovision", "Univer Video"]

generos = ["Acao", "Animacao", "Aventura", "Comedia", 
              "Crime", "Documentario", "Drama", "Familia", "Fantasia", "Faroeste", "Ficcao cientifica",
              "Guerra", "Historia", "Misterio", "Outros", "Romance", "Outros", "Suspense", "Terror"]

# Palavra base para substituição
palavra_base = "base"

# Percorre todos os arquivos da pasta
for arquivo in os.listdir(pasta):
    caminho_arquivo = os.path.join(pasta, arquivo)
    
    # Verifica se é um arquivo
    if os.path.isfile(caminho_arquivo):
        # Abre o arquivo para leitura
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        
        for provedor in provedores:
            # Substitui todas as ocorrências da palavra base pelo nome do provedor
            conteudo_modificado = conteudo.replace(palavra_base, provedor)
            
            # Caminho de saída para o arquivo
            caminho_arquivo_out = os.path.join(f"{pasta}/{provedor}", arquivo)
            
            # Cria o diretório se ele não existir
            os.makedirs(os.path.dirname(caminho_arquivo_out), exist_ok=True)
            
            # Salva o conteúdo modificado no novo arquivo
            with open(caminho_arquivo_out, 'w', encoding='utf-8') as file:
                file.write(conteudo_modificado)

print("Substituições concluídas!")