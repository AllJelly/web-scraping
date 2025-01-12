#!/bin/bash

cd /mnt/c/Users/Arthur/Documents/GitHub/web-scraping/python/

# Loop para executar o código Python 5 vezes
for i in {1..50}
do
    echo "Execução $i de 5-grupo.py"
    python 5-grupo.py
done

# Aguarda a interação do usuário antes de fechar
read -p "Pressione qualquer tecla para sair..."