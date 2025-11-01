from curriculo_information.scripts.config import carregar_chave_api
from curriculo_information.scripts.data_processor import processar_linhas_csv
from classificacao.classificacao_pesquisadores import classificacao_pipeline, criar_client
from curriculo_information.scripts.data_processor import processar_linhas_csv
from database.tags_retriever import tags_retrieve
from database.relation_inserter import relation_inserter

def main():
    """Função principal que orquestra todo o processo."""
    
    """
    Lembre-se de criar o ambiente virtual, ativá-lo e instalar as dependências! Além de ter o arquivo .env na sua máquina local com a chave de API.
    Em ordem:
    python3 -m venv venv
    
    source venv/bin/activate
    
    pip install -r requirements.txt
    """

    # --- Configurações do Script ---

    print(f"\n1 - CONFIGURAÇÕES INICIAIS\n")


    CAMINHO_ARQUIVO = "./curriculo_information/csv_information/dados_relevantes.csv"
    COLUNA_ID = 'researcher_id'
    COLUNAS_PROSA = ['abstract']
    COLUNAS_LISTA_DE_PROSAS = ['description_project']
    COLUNAS_LISTA = ['articles', 'project_name', 'great_area', 'area_specialty', 'patent', 'book_chapter', 'event_name']
    CHUNK_SIZE = 700
    CHUNK_OVERLAP = 100

    # Obter chave da API do arquivo .env
    carregar_chave_api()

    print("Variáveis de ambiente carregadas.")

    client = criar_client()

    print("Client do modelo da LLM carregado\n")
    
    print("-" * 50)

    print(f"\n2 - PROCESSAMENTO DE CHUNKS\n")
    
    print("Iniciando processamento de chunks...")

    # CSV e processar dados em chunks
    dados_processados = processar_linhas_csv(
        CAMINHO_ARQUIVO, COLUNA_ID, COLUNAS_PROSA, COLUNAS_LISTA, COLUNAS_LISTA_DE_PROSAS, CHUNK_SIZE, CHUNK_OVERLAP
    )
    
    print(f"\nProcessamento de chunks finalizado. {len(dados_processados)} pesquisadores processados.\n")
    print("-" * 50)
    

    print(f"\n2 - RETOMADA DE TAGS\n")

    # Retomar tags do banco
    tags = tags_retrieve();
    print(f"\nProcessamento de tags finalizado. {len(tags)} tags encontradas.\n")

    print("-" * 50)

    print(f"\n3 - CLASSIFICAÇÃO DE PESQUISADORES\n")
    
    print("Iniciando classificação de pesquisadores.")
    tags_por_pesquisador = classificacao_pipeline(tags, client, dados_processados)

    print("")

    print("-" * 50)

    print(f"\n4 - INSERÇÃO DE RELAÇÕES\n")

    relation_inserter(tags_por_pesquisador)
    
    
if __name__ == "__main__":
    main()