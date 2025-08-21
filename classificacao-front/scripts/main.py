# Importa as bibliotecas necessárias do Selenium
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Configurações do Chrome ---
chrome_options = Options()
# Executa o navegador em modo "headless" (sem abrir uma janela)
# Para ver a execução, comente a linha abaixo
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# --- Lógica Principal ---
driver = None # Inicializa a variável driver
try:
    # Inicializa o driver do Chrome da forma padrão
    # Isso requer que o chromedriver esteja no PATH do seu sistema ou no mesmo diretório
    print("Inicializando o WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    print("WebDriver inicializado com sucesso.")

    # URL direta para a página do pesquisador
    url_pesquisador = "https://simcc.uesc.br/researcher?researcher_name=Eduardo%20Manuel%20de%20Freitas%20Jorge&search_type=name&terms="

    print(f"Acessando a página: {url_pesquisador}")
    driver.get(url_pesquisador)
    
    # Define um tempo máximo de espera de 10 segundos
    wait = WebDriverWait(driver, 10)
    
    # seletor css para tag de nome
    seletor_nome = "h4.text-3xl.font-medium.px-8.text-center.mb-2"
    # seletor css para tag de descrição
    seletor_descricao = "p.text-gray-400.text-sm.text-justify"
    
    print("Esperando os elementos carregarem . . .")
    
    h4_nome_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, seletor_nome))
    )

    p_descricao_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, seletor_descricao))
    )
    
    # extrai os textos das tags
    nome_pesquisador = h4_nome_element.text
    descricao_pesquisador = p_descricao_element.text
    
    print("\n--- SUCESSO! ---")
    print(f"Nome encontrado: {nome_pesquisador}")
    print(f"Descrição: {descricao_pesquisador}")
    print("------------------\n")

except TimeoutException:
    # Este erro ocorre se o elemento não for encontrado no tempo definido
    print("\n--- ERRO ---")
    print(f"Não foi possível encontrar um ou mais elementos na página.")
    print("O site pode ter mudado sua estrutura ou os elementos não carregaram a tempo.")
    
    # Salva o HTML da página para depuração
    if driver:
        with open('pagina_erro.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("O HTML da página foi salvo em 'pagina_erro.html' para análise.")

except Exception as e:
    # Captura outros erros inesperados
    print(f"\n--- ERRO INESPERADO ---")
    print(f"Ocorreu um erro: {e}")

finally:
    # Garante que o navegador será fechado ao final da execução
    if driver:
        print("Fechando o navegador.")
        driver.quit()
        
        
dados_pesquisador = {
    "nome_pesquisador": nome_pesquisador,
    "descricao": descricao_pesquisador,
    # "publicacoes": []  # Comece com uma lista vazia
}
        
with open('dados_pesquisador.json', 'w', encoding='utf-8') as f:
    json.dump(dados_pesquisador, f, ensure_ascii=False, indent=4)

print("Arquivo JSON salvo com sucesso!")