from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def configurar_chrome_driver():
    """
    Configura e inicializa o WebDriver do Chrome com as opções desejadas.
    Retorna uma instância do driver.
    """
    print("Configurando as opções do Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    print("Inicializando o WebDriver...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver inicializado com sucesso.")
        return driver
    except Exception as e:
        print(f"--- ERRO AO INICIALIZAR O DRIVER ---")
        print(f"Ocorreu um erro: {e}")
        return None