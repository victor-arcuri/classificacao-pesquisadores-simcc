# Importa as bibliotecas necessárias do Selenium
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# --- Configurações do Chrome ---
chrome_options = Options()
# executa o navegador em modo "headless" pra não abrir janela
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# --- Lógica Principal ---
driver = None # inicializa o driver
try:
    # Inicializa o driver do Chrome da forma padrão
    print("Inicializando o WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    print("WebDriver inicializado com sucesso.")

    url_pesquisador = "https://simcc.uesc.br/researcher?researcher_name=Eduardo%20Manuel%20de%20Freitas%20Jorge&search_type=name&terms="

    print(f"Acessando a página: {url_pesquisador}")
    driver.get(url_pesquisador)
    
    # define tempo máximo de espera como 20 seg para ser usado depois
    wait = WebDriverWait(driver, 20)
    
    # --- Seletores CSS e XPath ---
    seletor_nome = "h4.text-3xl.font-medium.px-8.text-center.mb-2"
    seletor_descricao = "p.text-gray-400.text-sm.text-justify"
    # Seletor de artigos modificado para ser mais específico (antes estava coletando mais do que devia)
    seletor_artigos = "div[data-state='open'] div.text-left"
    # Seletor XPath para o botão "Mostrar mais"
    seletor_mostrar_mais = "//button[contains(text(), 'Mostrar mais')]"
    
    print("Aguardando os elementos carregarem...")
    
    # --- Extração dos Dados Iniciais ---
    
    # espera com o tempo estabelecido antes de 20 seg
    # buscando com seletor de nome e atribuindo a string nome_pesquisador
    h4_nome_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, seletor_nome))
    )
    nome_pesquisador = h4_nome_element.text
    
    # buscando com seletor de descrição e atribuindo a string descricao_pesquisador
    p_descricao_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, seletor_descricao))
    )
    descricao_pesquisador = p_descricao_element.text

    # --- Lógica para Clicar em "Mostrar mais" dos artigos---
    print("Procurando o botão 'Mostrar mais' para carregar todos os artigos...")
    while True:
        try:
            # espera o botão de mostrar mais ficar disponível
            mostrar_mais_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, seletor_mostrar_mais))
            )
            
            # rola a tela
            driver.execute_script("arguments[0].scrollIntoView(true);", mostrar_mais_button)
            time.sleep(1) # tempo pra executar
            mostrar_mais_button.click()
            print("Clicou em 'Mostrar mais'...")
            time.sleep(1) 
        except TimeoutException:
            # não encontrou o botão passou do tempo ou já apertou em todos 'mostrar mais'
            print("Botão 'Mostrar mais' não encontrado. Todos os artigos devem estar carregados.")
            break
        except ElementClickInterceptedException:
            # se outro elemento estiver na frente, tenta clicar com JavaScript
            # por enquanto está caindo aqui porque não tratei as aba de informações que aparece na frente
            print("Click normal interceptado, tentando com JavaScript...")
            driver.execute_script("arguments[0].click();", mostrar_mais_button)
            time.sleep(1)
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao clicar no botão: {e}")
            break

    # --- Extração Final dos Artigos ---
    
    print("Extraindo a lista completa de artigos...")
    # espera o tempo e extrai todos os artigos (todos os mostrar mais foram abertos e estão todos disponíveis)
    lista_artigos_elements = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_artigos))
    )
    
    # cria uma lista com os artigos
    artigos_textos = [elem.text for elem in lista_artigos_elements]
    
    # --- Exibição dos Resultados ---
    print("\n--- SUCESSO! DADOS EXTRAÍDOS ---")
    print(f"Nome encontrado: {nome_pesquisador}")
    print(f"\nDescrição: {descricao_pesquisador}")
    
    print(f"\nEncontrados {len(artigos_textos)} artigos no total.")
    for i, artigo in enumerate(artigos_textos, 1):
        print(f"\n--- Publicação {i} ---")
        print(artigo)
    print("\n------------------\n")

except TimeoutException:
    # se demorou demais e não encontrou algum elemento na página
    print("\n--- ERRO ---")
    print("Não foi possível encontrar um dos elementos principais (nome ou descrição) na página.")

except Exception as e:
    # qualquer outro erro que tiver dado
    print(f"\n--- ERRO INESPERADO ---")
    print(f"Ocorreu um erro: {e}")

finally:
    if driver:
        print("Fechando o navegador.")
        driver.quit()
