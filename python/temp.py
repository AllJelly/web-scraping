from datetime import datetime
from itertools import count
from typing import Any
import pandas as pd
import unicodedata
import os
import re

arq   = "./listas/lista-genero-provedor/grupo-20241231.csv"

df = pd.read_csv(arq)
df = df.sort_values(by='name', ascending=True)

# Filtrando o DataFrame
# df = df[~((df["tipo"].str.lower() != "filme") & (df["temporada"].isna() | df["episodio"].isna()))]

# Remove linhas duplicadas com base na coluna 'link'
df = df.drop_duplicates(subset='link', keep='first').reset_index(drop=True)

df.reset_index(drop=True, inplace=True)

df.to_csv(arq, index=False)