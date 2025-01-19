#!/bin/bash

cd /mnt/c/Users/Arthur/Documents/GitHub/web-scraping/python/

# Busca e atualiza links
echo "Execução link-1.py"
python link-1.py

# Migra dados já existentes
# echo "Execução migracao-5.py"
# python migracao-5.py

# Loop para executar o código Python 10 vezes
for i in {1..5}
do
    echo "Execução $i de grupos-2.py"
    python grupos-2.py
done

# Cria pastas
# echo "Execução 6-pastas.py"
# python 6-pastas.py


# # Buscando resoluções
# echo "Execução resolucao-3.py"
# python resolucao-3.py

# # Verifica se os links estão funcionando
# echo "Execução ativo-4.py"
# python ativo-4.py

# Aguarda a interação do usuário antes de fechar
read -p "Pressione qualquer tecla para sair..."