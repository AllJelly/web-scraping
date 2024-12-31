import pandas as pd
import os

input_arq   = "./listas/lista-genero-provedor/grupo-20241231.csv"
out_folder  = "./strm"

if not os.path.exists(out_folder):
    # Criar a pasta
    os.makedirs(out_folder)
    
df = pd.read_csv(input_arq)

# for _, row in df.iterrows():
    # pass