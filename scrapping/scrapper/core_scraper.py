# scraper/core_scraper.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Seletores Estáveis e Específicos ---
SELETOR_NOME = "h4.text-3xl.font-medium.px-8.text-center.mb-2"
SELETOR_DESCRICAO = "p.text-gray-400.text-sm.text-justify"

# Seletor artigos
SELETOR_CONTEUDO_ARTIGOS = "div[data-state='open'] div.text-left"

# Seletor projetos
SELETOR_CONTEUDO_PROJETOS = "div[data-state='open'] div.p-4.pb-0 p.text-sm.capitalize:first-of-type"

# Seletor para o botão "Projetos de pesquisa" baseado no texto
XPATH_BOTAO_PROJETOS = "//button[contains(text(), 'Projetos de pesquisa')]"

# Seletor para encontrar o botão "Mostrar mais" APENAS na aba ativa
XPATH_MOSTRAR_MAIS_NA_ABA_ATIVA = "//div[@data-state='open']//button[contains(text(), 'Mostrar mais')]"

def _clicar_em_todos_mostrar_mais(driver):
    """
    Função auxiliar para clicar repetidamente no botão 'Mostrar mais'
    que está DENTRO da aba atualmente aberta.
    """
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
            time.sleep(1.5) # Aumentei um pouco a pausa para dar tempo de carregar

        except TimeoutException:
            print("Botão 'Mostrar mais' não encontrado. Informações devem estar carregadas.")
            break
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao clicar no botão 'Mostrar mais': {e}")
            break

def raspar_dados_pesquisador(driver, url):
    """
    Orquestra a extração de dados de uma URL de pesquisador.
    Retorna um dicionário com os dados extraídos ou None em caso de falha.
    """
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

        # --- ETAPA 1: Raspar ARTIGOS (Aba que já vem aberta) ---
        print("\n--- INICIANDO EXTRAÇÃO DE ARTIGOS ---")
        _clicar_em_todos_mostrar_mais(driver)
        
        print("Extraindo a lista completa de artigos...")
        lista_artigos_elements = driver.find_elements(By.CSS_SELECTOR, SELETOR_CONTEUDO_ARTIGOS)
        artigos_textos = [elem.text for elem in lista_artigos_elements]
        print(f"Encontrados {len(artigos_textos)} artigos.")

        # --- ETAPA 2: Mudar para a aba PROJETOS e raspar ---
        print("\n--- INICIANDO EXTRAÇÃO DE PROJETOS DE PESQUISA ---")
        
        projetos_button = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_BOTAO_PROJETOS)))
        
        print("Rolando para encontrar o botão de 'Projetos de pesquisa'...")
        driver.execute_script("arguments[0].scrollIntoView({inline: 'center', block: 'nearest'});", projetos_button)
        time.sleep(1)

        # MUDANÇA CRÍTICA: Usando clique com JavaScript para evitar o erro de interceptação
        print("Clicando na aba 'Projetos de pesquisa' com JavaScript...")
        driver.execute_script("arguments[0].click();", projetos_button)
        time.sleep(2) 

        _clicar_em_todos_mostrar_mais(driver)
        
        # MUDANÇA CRÍTICA: Usando o novo seletor, mais específico para os projetos
        print("Extraindo a lista completa de projetos de pesquisa...")
        lista_projetos_elements = driver.find_elements(By.CSS_SELECTOR, SELETOR_CONTEUDO_PROJETOS)
        projetos_textos = [elem.text for elem in lista_projetos_elements]
        print(f"Encontrados {len(projetos_textos)} projetos.")

        # --- ETAPA 3: Montar o resultado final ---
        dados_pesquisador = {
            "nome": nome_pesquisador,
            "descricao": descricao_pesquisador,
            "artigos": artigos_textos,
            "projetos": projetos_textos
        }
        
        return dados_pesquisador

    except TimeoutException:
        print("\n--- ERRO DE TIMEOUT ---")
        print("Não foi possível encontrar um dos elementos principais na página.")
        return None
    except Exception as e:
        print(f"\n--- ERRO INESPERADO ---")
        print(f"Ocorreu um erro: {e}")
        return None