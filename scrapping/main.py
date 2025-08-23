from scrapper.driver_config import configurar_chrome_driver
from scrapper.core_scraper import raspar_dados_pesquisador

# Coloque aqui url da página do pesquisador desejado
URL_PESQUISADOR = "https://simcc.uesc.br/researcher?researcher_name=Eduardo%20Manuel%20de%20Freitas%20Jorge&search_type=name&terms="

def exibir_resultados(dados):
    """Função para formatar e exibir os dados extraídos no console."""
    if not dados:
        print("Nenhum dado foi extraído para exibir.")
        return
        
    print("\n--- SUCESSO! DADOS EXTRAÍDOS ---")
    print(f"Nome encontrado: {dados['nome']}")
    print(f"\nDescrição: {dados['descricao']}")
    
    total_artigos = len(dados['artigos'])
    print(f"\nEncontrados {total_artigos} artigos no total.")
    
    for i, artigo in enumerate(dados['artigos'], 1):
        print(f"\n--- Publicação {i} ---")
        print(artigo)
    print("\n------------------\n")
    
    for i, projeto in enumerate(dados['projetos'], 1):
        print(f"\n--- Projeto {i} ---")
        print(projeto)
    print("\n------------------\n")
    
    for i, patente in enumerate(dados['patentes'], 1):
        print(f"\n--- Patente {i} ---")
        print(patente)
    print("\n------------------\n")

def main():
    """Função principal que executa o scraper."""
    driver = None
    try:
        driver = configurar_chrome_driver()
        if driver:
            dados_extraidos = raspar_dados_pesquisador(driver, URL_PESQUISADOR)
            exibir_resultados(dados_extraidos)

    except Exception as e:
        print(f"\n--- ERRO INESPERADO NA EXECUÇÃO PRINCIPAL ---")
        print(f"Ocorreu um erro: {e}")

    finally:
        if driver:
            print("Fechando o navegador.")
            driver.quit()

if __name__ == "__main__":
    main()