from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

chrome_options = Options()
chrome_options.add_argument("--headless")  # Executar em segundo plano
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://simcc.uesc.br/resultados?type_search=name&terms=%28Eduardo+Manuel+de+Freitas+Jorge%29&tab=researchers-home")

# Esperar o conteúdo carregar
time.sleep(3)

# Pegar o HTML depois do JavaScript executar
html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')
nome = soup.find('h4', class_='text-3xl font-medium px-8 text-center mb-2')
if nome:
    print(nome.get_text(strip=True))