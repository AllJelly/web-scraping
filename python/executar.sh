#!/bin/bash

cd /mnt/c/Users/Arthur/Documents/GitHub/web-scraping/python/

# Loop para executar o código Python 5 vezes
for i in {1..50}
do
    echo "Execução $i de grupos-2.py"
    python grupos-2.py
done

# Aguarda a interação do usuário antes de fechar
read -p "Pressione qualquer tecla para sair..."