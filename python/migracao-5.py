import pandas as pd

# Variável de controle para interrupção
interrupted = False
arquivo_01 = "./listas/3-lista-videos/videos.csv"
arquivo_02 = "./listas/4-lista-metadados/metadados.csv"
arquivo_03 = "./listas/lista-genero-provedor/grupo.csv"
arquivo_04 = "./listas/3-lista-videos/videos-2.csv"

# Carregar os arquivos CSV
df_tam  = pd.read_csv(arquivo_01)
df_meta = pd.read_csv(arquivo_02)
df_prov = pd.read_csv(arquivo_03)
df_base = pd.read_csv(arquivo_04)

# Definir os merges a serem realizados, incluindo as colunas necessárias para cada arquivo
merges = [
    (df_tam[['link', 'tamanho_GB']], 'link', 'tamanho_GB'),
    (df_meta[['link', 'largura', 'altura', 'fps', 'contagem quadros']], 'link', ['largura', 'altura', 'fps', 'contagem quadros']),
    (df_prov[['link', 'date', 'provedor', 'generos', 'titulo']], 'link', ['date', 'provedor', 'generos', 'titulo'])
]

# Iterar sobre os merges e aplicar as atualizações
for merge_df, on_col, cols_to_update in merges:
    merged_df = pd.merge(df_base, merge_df, on=on_col, how='left', suffixes=('', f'_{on_col}'))
    
    # Se as colunas para atualizar forem uma lista, atualize todas
    if isinstance(cols_to_update, list):
        for col in cols_to_update:
            col_to_update = f'{col}_{on_col}'
            # Atualiza df_base[col] apenas se ele for NaN (None)
            df_base[col] = df_base[col].where(df_base[col].notna(), merged_df[col_to_update])
    else:
        # Caso contrário, atualize a coluna única
        col_to_update = f'{cols_to_update}_{on_col}'
        # Atualiza df_base[cols_to_update] apenas se ele for NaN (None)
        df_base[cols_to_update] = df_base[cols_to_update].where(df_base[cols_to_update].notna(), merged_df[col_to_update])

# Salvar os dados finais antes de sair
df_base = df_base.sort_values(by=['validade', 'name'], ascending=True)
df_base.reset_index(drop=True, inplace=True)
df_base.to_csv(arquivo_04, index=False, encoding='utf-8')

print("Processo finalizado e dados salvos.")