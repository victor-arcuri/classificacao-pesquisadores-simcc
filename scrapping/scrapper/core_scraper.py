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
XPATH_BOTAO_PRODUCAO_TECNICA = "//button[contains(text(), 'Produção técnica')]"
SELETOR_TODOS_TITULOS_PRODUCAO_TECNICA = "div[data-state='open'] h3.text-sm.capitalize"
XPATH_BOTAO_PROJETOS = "//button[contains(text(), 'Projetos de pesquisa')]"
XPATH_MOSTRAR_MAIS_NA_ABA_ATIVA = "//div[@data-state='open']//button[contains(text(), 'Mostrar mais')]"


# --- FUNÇÃO AUXILIAR CORRIGIDA E MAIS ROBUSTA ---
def eh_uma_patente(elemento_h3):
    """
    Verifica se um elemento <h3> pertence a um item de patente.
    Sobe até o "card" principal do item e procura pela palavra 'Patente'.
    """
    try:
        # A partir do h3, sobe na árvore até o elemento <div role="alert"> que é o "card" do item.
        # Depois, dentro desse card, procura em qualquer lugar por uma div que contenha o texto "Patente".
        elemento_h3.find_element(By.XPATH, "ancestor::div[@role='alert']//div[contains(text(), 'Patente')]")
        return True # Se o elemento foi encontrado, significa que é uma patente.
    except NoSuchElementException:
        # Se não encontrou, não é uma patente e a função retorna False.
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
        
        print("Extraindo a lista completa de produções técnicas para filtrar as patentes...")
        todos_titulos_elements = driver.find_elements(By.CSS_SELECTOR, SELETOR_TODOS_TITULOS_PRODUCAO_TECNICA)
        
        # Usando a nova função de verificação, que é muito mais robusta
        patentes_textos = [elem.text for elem in todos_titulos_elements if eh_uma_patente(elem)]
        
        print(f"Encontradas {len(patentes_textos)} patentes.")

        # --- ETAPA 4: Montar o resultado final ---
        dados_pesquisador = {
            "nome": nome_pesquisador,
            "descricao": descricao_pesquisador,
            "artigos": artigos_textos,
            "projetos": projetos_textos,
            "patentes": patentes_textos
        }
        
        return dados_pesquisador

    except Exception as e:
        print(f"\n--- ERRO INESPERADO ---")
        print(f"Ocorreu um erro: {e}")
        return None