import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Seletores ---
SELETOR_NOME = "h4.text-3xl.font-medium.px-8.text-center.mb-2"
SELETOR_DESCRICAO = "p.text-gray-400.text-sm.text-justify"
SELETOR_CONTEUDO_ARTIGOS = "div[data-state='open'] div.text-left"
SELETOR_CONTEUDO_PROJETOS = "div[data-state='open'] div.p-4.pb-0 p.text-sm.capitalize:first-of-type"
XPATH_BOTAO_PROJETOS = "//button[contains(text(), 'Projetos de pesquisa')]"
XPATH_BOTAO_PRODUCAO_TECNICA = "//button[contains(text(), 'Produção técnica')]"
SELETOR_TODOS_TITULOS_PRODUCAO_TECNICA = "div[data-state='open'] h3.text-sm.capitalize"
XPATH_BOTAO_CAPITULOS = "//button[contains(text(), 'Livros e capítulos')]"
SELETOR_TODOS_TITULOS_LIVROS_CAPITULOS = "div[data-state='open'] [role='alert'] p.text-sm.capitalize"
XPATH_MOSTRAR_MAIS_NA_ABA_ATIVA = "//div[@data-state='open']//button[contains(text(), 'Mostrar mais')]"

def eh_uma_patente(elemento_h3):
    """Verifica se um elemento <h3> pertence a um item de patente."""
    try:
        elemento_h3.find_element(By.XPATH, "ancestor::div[@role='alert']//div[contains(text(), 'Patente')]")
        return True
    except NoSuchElementException:
        return False

def eh_um_capitulo(elemento_titulo_p):
    """
    Verifica se um elemento de título <p> pertence a um capítulo de livro
    verificando a classe da barra lateral colorida do card.
    Capítulos têm uma barra rosa clara (bg-pink-300).
    """
    try:
        # Navega do parágrafo do título para o card pai principal
        card_principal = elemento_titulo_p.find_element(By.XPATH, "ancestor::div[@class='flex group w-full']")
        
        # Dentro do card, procura pela barra lateral com a cor específica de capítulos
        card_principal.find_element(By.CSS_SELECTOR, "div.bg-pink-300")
        
        # Se encontrou, significa que é um capítulo
        return True
    except NoSuchElementException:
        # Se não encontrou o elemento com a classe de capítulo, não é um capítulo.
        return False

def _clicar_em_todos_mostrar_mais(driver):
    print("Procurando o botão 'Mostrar mais' na aba ativa...")
    while True:
        try:
            mostrar_mais_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, XPATH_MOSTRAR_MAIS_NA_ABA_ATIVA))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", mostrar_mais_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", mostrar_mais_button)
            print("Clicou em 'Mostrar mais'...")
            time.sleep(1.5)
        except TimeoutException:
            print("Botão 'Mostrar mais' não encontrado. Informações devem estar carregadas.")
            break
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao clicar no botão 'Mostrar mais': {e}")
            break

def raspar_dados_pesquisador(driver, url):
    print(f"Acessando a página: {url}")
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    dados_pesquisador = {} # Inicializa o dicionário

    try:
        # --- DADOS GERAIS ---
        print("Aguardando os elementos carregarem...")
        h4_nome_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELETOR_NOME)))
        nome_pesquisador = h4_nome_element.text
        p_descricao_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELETOR_DESCRICAO)))
        descricao_pesquisador = p_descricao_element.text

        # --- ETAPA 1: Raspar ARTIGOS ---
        print("\n--- INICIANDO EXTRAÇÃO DE ARTIGOS ---")
        _clicar_em_todos_mostrar_mais(driver)
        lista_artigos_elements = driver.find_elements(By.CSS_SELECTOR, SELETOR_CONTEUDO_ARTIGOS)
        artigos_textos = [elem.text for elem in lista_artigos_elements]
        print(f"Encontrados {len(artigos_textos)} artigos.")

        # --- ETAPA 2: Mudar para a aba PROJETOS e raspar ---
        print("\n--- INICIANDO EXTRAÇÃO DE PROJETOS DE PESQUISA ---")
        projetos_button = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_BOTAO_PROJETOS)))
        driver.execute_script("arguments[0].scrollIntoView({inline: 'center', block: 'nearest'});", projetos_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", projetos_button)
        time.sleep(2)
        _clicar_em_todos_mostrar_mais(driver)
        lista_projetos_elements = driver.find_elements(By.CSS_SELECTOR, SELETOR_CONTEUDO_PROJETOS)
        projetos_textos = [elem.text for elem in lista_projetos_elements]
        print(f"Encontrados {len(projetos_textos)} projetos.")

        # --- ETAPA 3: Mudar para a aba PRODUÇÃO TÉCNICA e raspar PATENTES ---
        print("\n--- INICIANDO EXTRAÇÃO DE PATENTES ---")
        producao_tecnica_button = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_BOTAO_PRODUCAO_TECNICA)))
        driver.execute_script("arguments[0].scrollIntoView({inline: 'center', block: 'nearest'});", producao_tecnica_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", producao_tecnica_button)
        time.sleep(2)
        _clicar_em_todos_mostrar_mais(driver)
        todos_titulos_prod_tecnica = driver.find_elements(By.CSS_SELECTOR, SELETOR_TODOS_TITULOS_PRODUCAO_TECNICA)
        patentes_textos = [elem.text for elem in todos_titulos_prod_tecnica if eh_uma_patente(elem)]
        print(f"Encontradas {len(patentes_textos)} patentes.")
        
        # --- ETAPA 4: Mudar para aba LIVROS E CAPÍTULOS e raspar CAPÍTULOS ---
        print("\n--- INICIANDO EXTRAÇÃO DE CAPÍTULOS DE LIVROS ---")
        livros_e_capitulos_button = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_BOTAO_CAPITULOS)))
        driver.execute_script("arguments[0].scrollIntoView({inline: 'center', block: 'nearest'});", livros_e_capitulos_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", livros_e_capitulos_button)
        time.sleep(2)
        _clicar_em_todos_mostrar_mais(driver)
        
        print("Extraindo todos os títulos de Livros e Capítulos...")
        todos_titulos_livros_capitulos = driver.find_elements(By.CSS_SELECTOR, SELETOR_TODOS_TITULOS_LIVROS_CAPITULOS)
        
        print("Filtrando para manter apenas os capítulos...")
        capitulos_textos = [elem.text for elem in todos_titulos_livros_capitulos if eh_um_capitulo(elem)]
        
        print(f"Encontrados {len(capitulos_textos)} capítulos de livros.")
        
        # --- ETAPA 5: Montar o resultado final ---
        dados_pesquisador = {
            "nome": nome_pesquisador,
            "descricao": descricao_pesquisador,
            "artigos": artigos_textos,
            "projetos": projetos_textos,
            "patentes": patentes_textos,
            "capitulos": capitulos_textos
        }
        
        return dados_pesquisador

    except Exception as e:
        print(f"\n--- ERRO INESPERADO ---")
        print(f"Ocorreu um erro: {e}")