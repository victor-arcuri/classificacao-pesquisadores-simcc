import time
from scripts.config import carregar_chave_api
from scripts.data_processor import processar_linhas_csv
from scripts.embedding_generator import gerar_embeddings_e_criar_dataframe
from scripts.output_utils import visualizar_dataframe, visualizar_chunks
from scripts.include_embeddings import criar_conexao_e_inserir_dados

# recomendação para aprimorar: pegar artigos dos últimos anos
# pegar informação do openalex

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
    CAMINHO_ARQUIVO = "./csv_information/dados_relevantes.csv"
    COLUNA_ID = 'researcher_id'
    COLUNAS_PROSA = ['abstract']
    COLUNAS_LISTA_DE_PROSAS = ['description_project']
    COLUNAS_LISTA = ['articles', 'project_name', 'great_area', 'area_specialty', 'patent', 'book_chapter', 'event_name']
    CHUNK_SIZE = 700
    CHUNK_OVERLAP = 100
    
    # Obter chave da API do arquivo .env
    carregar_chave_api()

    # CSV e processar dados em chunks
    dados_processados = processar_linhas_csv(
        CAMINHO_ARQUIVO, COLUNA_ID, COLUNAS_PROSA, COLUNAS_LISTA, COLUNAS_LISTA_DE_PROSAS, CHUNK_SIZE, CHUNK_OVERLAP
    )
    
    print(f"\nProcessamento de chunks finalizado. {len(dados_processados)} pesquisadores processados.")
    print("-" * 50)
    
    # Visualizar chunks
    visualizar_chunks(dados_processados)

    # Gerar embeddings e criar DataFrame
    tempo_inicio = time.time()
    df_final = gerar_embeddings_e_criar_dataframe(dados_processados)
    tempo_fim = time.time()
    print(f"Duração da geração de embeddings: {tempo_fim-tempo_inicio:.2f} segundos")

    # Visualizar as embeddings no dataframe
    visualizar_dataframe(df_final)
    
    print("\n\n\n\n")
    
    # Criar conexão e popular o banco
    criar_conexao_e_inserir_dados(df_final)
    
main()