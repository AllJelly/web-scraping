from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pandas as pd
import unicodedata
import requests
import signal
import re

# .avi: Arquivo de vídeo do Windows
# .mp4, .m4v, .mov: Arquivo de vídeo MP4
# .mpg ou .mpeg: Arquivo de filme
# .wmv: Arquivo Windows Media Video
# .mkv: Formato de vídeo
# .flv, .f4v e .swf: Formato de vídeo
# .avchd: Formato de vídeo
# .webm ou .html5: Formato de vídeo
extensao_videos = ['.avi', '.mp4', '.m4v', '.mov', '.mkv', '.mpg', '.mpeg', '.wmv', '.flv', '.f4v', '.swf', '.avchd', '.webm', '.html5']
input_arq = './listas/2-lista-serie_tv/filtrado.csv'
output_arq = './listas/3-lista-videos/videos-2.csv'
count = 0

# Variável de controle para interrupção
interrupted = False

def handle_interrupt(signal_received, frame):
    """
    Função para capturar o sinal de interrupção (Ctrl+C).
    """
    global interrupted
    print("\nInterrupção detectada. Finalizando após concluir threads em execução...")
    interrupted = True

def remove_temporada_episodio(nome):
    """
    Remove o padrão ' SXX EXX' do nome e retorna a temporada e o episódio extraídos.
    """
    # Expressão regular para capturar temporada e episódio
    padrao = r'\sS(\d{2})\sE(\d+)'
    match = re.search(padrao, nome, flags=re.IGNORECASE)
    
    if match:
        temporada = int(match.group(1))  # Captura o número da temporada
        episodio = int(match.group(2))  # Captura o número do episódio
        # Remove o padrão do nome
        nome_limpo = re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()
        return nome_limpo, int(temporada), int(episodio)
    return nome, None, None

def remove_ano(nome):
    # Obtém o ano atual
    ano_atual = datetime.now().year
    
    # Expressão regular para identificar e remover anos entre 1900 e o ano atual
    padrao = rf'\b(19[0-9]{{2}}|20[0-{str(ano_atual)[2]}][0-9])\b'
    
    # Substitui o ano encontrado por uma string vazia e remove espaços extras
    # Substitui o ano encontrado por uma string vazia
    nome_sem_ano = re.sub(padrao, '', nome).strip()
    
    # Se a string resultante estiver vazia, retorna o nome original
    if not nome_sem_ano:
        return nome
    
    return nome_sem_ano

def remover_acentos(texto):
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def limpaNome(name):
    # Remover o ponto final se existir
    if name.endswith('.'):
        name = name[:-1]
    
    # Substituir caracteres especiais e espaços extras
    name = re.sub(r"\*", "", name)  # Remover asteriscos
    name = re.sub(r" 14temp| 19 Temporada| Brasil Paralelo| -14temp|Mazzaropi - ", " ", name)  # Substituir essas ocorrências por espaço
    name = re.sub(r"\s{2,}", " ", name)  # Substituir múltiplos espaços consecutivos por um único espaço
    
    name = remove_ano(name)  # Remover ano
    name = name.split("  ")[0].strip()  # Remover partes após dois espaços consecutivos e fazer strip
    
    if name[-2:].lower() == " -":
        name = name[:-2]
    if name[-3:].lower() == " r5":
        name = name[:-3]
    if name[-2:].lower() == " t":
        name = name[:-2]
    
    # Legenda
    legendado = name[-4:].lower() == " leg"
    legendado = name[-4:].lower() == " [l]"
    legendado = name[-10:].lower() == " legendado"
    if name[-4:].lower() == " leg" or name[-4:].lower() == " [l]":
        name = name[:-4]
    if name[-10:].lower() == " legendado":
        name = name[:-10]
    
    # Cinema
    cam = name[-5:].lower() == " cine"
    cam = name[-4:].lower() == " cam"
    if name[-5:].lower() == " cine":
        name = name[:-5]
    if name[-4:].lower() == " cam":
        name = name[:-4]
    
    if name[-6:].lower() == " [hdr]":
        name = name[:-6]
    if name[-4:].lower() == " hd2":
        name = name[:-4]
    if name[-3:].lower() == " 4k":
        name = name[:-3]
    if name[-4:].lower() == " nac":
        name = name[:-4]
    
    # Dublado
    dublado = name[-4:].lower() == " dub"
    dublado = name[-7:].lower() == " [dual]"
    dublado = name[-5:].lower() == " dual"
    if name[-4:].lower() == " dub":
        name = name[:-4]
    if name[-7:].lower() == " [dual]":
        name = name[:-7]
    if name[-5:].lower() == " dual":
        name = name[:-5]
    
    if name[-2:].lower() == " -":
        name = name[:-2]
    
    name = remove_ano(name) # remove ano
    
    if name[-2:].lower() == " -":
        name = name[:-2]
        
    name = remover_acentos(name)
    return name, legendado, cam, dublado

def get_metadados(infos, link, url_servidor, validade, df_out):
    if interrupted:
        return None, None, None
    match = re.search(r'tvg-name="([^"]*)".*?tvg-logo="([^"]*)".*?group-title="([^"]*)"', infos)
    if match:
        tvg_name = str(re.sub(r'\s*\([^)]*\)', '', match.group(1)))              
        tvg_logo = match.group(2)
        group_title = match.group(3)
        
        if (url_servidor, tvg_name) in df_out[['Url do Servidor', 'name']].itertuples(index=False, name=None):
            mask = (df_out['Url do Servidor'] == url_servidor) & (df_out['name'] == tvg_name)
            if df_out.loc[mask, 'link'].values[0] != link:
                return link, df_out.loc[mask, 'link'].values[0], None
            return None, None, None
        
        print(f"Dados encontrados - {tvg_name}")
        
        tvg_name, temporada, episodio = remove_temporada_episodio(tvg_name)
        
        tipo = "Série"
        if temporada is None and episodio is None:
            tipo = "Filme"
        
        leg1 = "legendado" in group_title.lower()
        tvg_name, leg2, cam, dublado = limpaNome(tvg_name)
        legendado = leg1 is True or leg2 is True
        return None, None, {
            'Url do Servidor': url_servidor,
            'name': f"\"{tvg_name}\"",
            'original_name': str(re.sub(r'\s*\([^)]*\)', '', match.group(1))),
            'group-title': group_title,
            'logo-link': tvg_logo,
            'link': link,
            'validade': validade,
            'tamanho_GB': None,
            "largura": None,
            "altura": None,
            "fps": None,
            "contagem quadros": None,
            "tipo": tipo,
            "legendado": legendado,
            "cam": cam,
            "dublado": dublado,
            "temporada": temporada,
            "episodio": episodio,
            "date": None,
            "provedor": None,
            "generos": None,
            "titulo": None,
            "ativo": True,
        }
        
# Registrar o manipulador de sinal para Ctrl+C
signal.signal(signal.SIGINT, handle_interrupt)

# Carregar dados de entrada
df = pd.read_csv(input_arq)
try:
    df_out = pd.read_csv(output_arq)
except FileNotFoundError:
    df_out = pd.DataFrame(columns=['Url do Servidor', 'name', 'original_name', 'group-title', 
                                   'logo-link', 'link', 'validade', 'tamanho_GB', "largura", "altura", 
                                   "fps", "contagem quadros", "tipo", "legendado", "cam", "dublado", "temporada", 
                                   "episodio", "date", "provedor", "generos", "titulo", "ativo"])

dados = []
try:
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = {}
        for _, row in df.iterrows():
            if interrupted:
                print("Interrupção detectada. Não serão lançadas novas threads.")
                break
            try:
                response = requests.get(row['Link M3U'], timeout=25)
                if response.status_code != 200:
                    continue
            except:
                continue
            print(f"Lista encontrado - {row['Link M3U']}")
            m3u_content = response.text
            lines = m3u_content.splitlines()
            for i in range(1, len(lines), 2):
                try:
                    if (i+1 > len(lines)) or interrupted:
                        break
                    elif lines[i+1] in df_out['link'].values or any(dirc.get('link') == lines[i + 1] for dirc in dados):
                        continue
                    elif lines[i].startswith("#EXTINF") and any([True for ext in extensao_videos if ext in lines[i+1]]): 
                        future = executor.submit(get_metadados, lines[i], lines[i+1], row['Url do Servidor'], row['Validade'], df_out)
                        futures[future] = lines[i+1]
                except Exception as e:
                    print(str(e))

        for future in as_completed(futures):
            try:
                link_novo, link_velho, resultado = future.result()
                if resultado:
                    dados.append(resultado)
                elif link_novo:
                    df_out.loc[df_out['link'] == link_velho, 'link'] = link_novo
                    print(f"Lista atualizado - {df_out.loc[df_out['link'] == link_velho, 'name']} novo ({link_novo}) velho ({link_velho})")
                    
                # Salvar dados intermediários em lotes de 1000
                if len(dados) >= 1000 and not interrupted:
                    print("Salvando dados intermediários...")
                    df_out = pd.concat([df_out, pd.DataFrame(dados)], ignore_index=True)
                    df_out = df_out.sort_values(by=['validade', 'name'], ascending=True)
                    df_out.reset_index(drop=True, inplace=True)
                    df_out.to_csv(output_arq, index=False, encoding='utf-8')
                    dados.clear()
            except Exception as e:
                print(f"Erro ao processar: {e}")

        print("Esperando threads em execução finalizarem...")
except KeyboardInterrupt:
    print("Interrupção manual detectada. Finalizando...")
finally:
    # Removendo duplicados e já presentes com base nas colunas 'name' e 'link'
    seen, unique_dados = set(), []
    for item in dados:
        # Criar uma chave única para comparar com o conjunto 'seen'
        chave = (item["name"], item["link"])
        if chave not in seen and not df_out[['name', 'link']].apply(lambda x: (x['name'], x['link']) == (item['name'], item['link']), axis=1).any():
            unique_dados.append(item)
            seen.add(chave)
            
    # Salvar os dados finais antes de sair
    df_out = pd.concat([df_out, pd.DataFrame(unique_dados)], ignore_index=True)
    df_out = df_out.sort_values(by=['validade', 'name'], ascending=True)
    df_out.reset_index(drop=True, inplace=True)
    df_out.to_csv(output_arq, index=False, encoding='utf-8')
    print("Processo finalizado e dados salvos.")