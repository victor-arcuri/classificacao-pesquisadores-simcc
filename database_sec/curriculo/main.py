import time
from scripts.config import carregar_chave_api
from scripts.data_processor import processar_linhas_csv
from scripts.embedding_generator import gerar_embeddings_e_criar_dataframe
from scripts.output_utils import visualizar_dataframe, visualizar_chunks

# pegar artigos dos últimos anos

def main():
    """Função principal que orquestra todo o processo."""

    # --- Configurações do Script ---
    CAMINHO_ARQUIVO = "./dados_relevantes.csv"
    COLUNA_ID = 'researcher_id'
    COLUNAS_PROSA = ['abstract']
    COLUNAS_LISTA_DE_PROSAS = ['description_project']
    COLUNAS_LISTA = ['articles', 'project_name', 'great_area', 'area_specialty', 'patent', 'book_chapter', 'event_name']
    # openalex
    CHUNK_SIZE = 700
    CHUNK_OVERLAP = 100
    
    # Obter chave da API
    carregar_chave_api()

    # CSV e processar os chunks
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
    print(f"Duração da geração de embeddings: {tempo_fim-tempo_inicio}.2f segundos")

    # Visualizar os resultados
    visualizar_dataframe(df_final)
    
main()