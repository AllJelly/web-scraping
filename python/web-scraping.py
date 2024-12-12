from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import datetime
import os

email       = 'arthurcoelho442zip@gmail.com'
password    = 'arthur1478'
login_url   = "https://vectorplayer.com/login"
lista_url   = "https://vectorplayer.com/premium"
blacklist   = ['http://178.162.225.117:2082/', 'http://dns.painel.wtf:80/','http://p2.hostinggonemoreso1.com:2082/', 'http://srv.hostinggon.xyz:2082/', 'http://2.magmas5.com:8000/'] # Canais que possuem apenas TV

# Configurar o WebDriver (exemplo com Chrome)
driver = webdriver.Chrome()  # ou webdriver.Firefox() se estiver usando o Firefox

# Abrir a página de login
driver.get(login_url)

# Localizar os campos de email e senha e o botão de login
email_input = driver.find_element(By.ID, "campoEmail")
password_input = driver.find_element(By.ID, "campoSenha")
login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

# Inserir credenciais
email_input.send_keys(email)
password_input.send_keys(password)

# Clicar no botão de login
login_button.click()

# Esperar um tempo para a página carregar após o login (ajuste conforme necessário)
sleep(2)  # Ajuste o tempo de espera conforme a velocidade de carregamento da página

if "login" not in driver.current_url.lower():
    print("Login bem-sucedido!")
    driver.get(lista_url)
    
    # Obter o HTML da página atual após o login
    page_html = driver.page_source
    
    driver.quit()
    
    # Usar o BeautifulSoup para analisar o HTML
    soup = BeautifulSoup(page_html, "html.parser")
    
    # Função para extrair o texto depois de uma etiqueta <b> específica
    
    dados_listas = []
    listas_premium = soup.find_all('div', class_='card shadow-none bg-transparent border border-primary mb-3')
    for lista in listas_premium:
        def extrair_texto(tag_texto,):
            tag = lista.find('b', string=tag_texto)
            if tag:
                return tag.find_next('p').text.strip()
            return ''
        # Extrair os valores
        canais_brasileiros  = extrair_texto('Canais Brasileiros: ')
        if canais_brasileiros == 'Sim':
            url_servidor        = extrair_texto('Url do Servidor: ')
            
            if url_servidor in blacklist:
                continue
            nome_usuario        = extrair_texto('Nome de Usuário: ')
            senha               = extrair_texto('Senha: ')
            validade            = extrair_texto('Validade: ')
            conexoes            = extrair_texto('Conexões: ')

            button = lista.find('button', {'id': 'buttonCopy'})
            link_m3u = 'None'
            if button:
                link_m3u = button.get('lang')
            
            try:
                # Adicionando os dados à lista
                dados_listas.append({
                    'Url do Servidor': url_servidor,
                    'Nome de Usuário': nome_usuario,
                    'Senha': senha,
                    'Validade': int(validade[10:-6]),
                    'Conexões Ativas': conexoes[:-7].split("/")[0],
                    'Conexões Totais': conexoes[:-7].split("/")[1],
                    'Link M3U': link_m3u
                })
            except:
                pass
    # Converter a lista de dicionários em um DataFrame
    df = pd.DataFrame(dados_listas)
    
    # Filtros
    df = df.dropna()
    df = df.drop_duplicates()
    # df = df[df['Conexões Ativas'] <= df['Conexões Totais']]

    # Ordenação
    df = df.sort_values(by=['Url do Servidor', 'Validade'], ascending=[True, False])
    
    if not os.path.exists('./lista'):
        os.makedirs('./lista')
    
    agora = datetime.datetime.now()
    
    # Salvar o DataFrame em um arquivo CSV
    df.to_csv(f'./lista/completa-{agora.year}{agora.month}{agora.day}.csv', index=False, encoding='utf-8')

    print(f"Dados salvos em 'completa-{agora.year}{agora.month}{agora.day}.csv'")
    
else:
    driver.quit()