import time
from curriculo_information.scripts.config import carregar_chave_api
from curriculo_information.scripts.data_processor import processar_linhas_csv
from curriculo_information.scripts.embedding_generator import gerar_embeddings_e_criar_dataframe
from curriculo_information.scripts.output_utils import visualizar_dataframe, visualizar_chunks
from curriculo_information.scripts.include_embeddings import criar_conexao_e_inserir_dados
from tags_from_curriculos.tagging import generate_tags_pipeline, visualize_tags, criar_client

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
    CAMINHO_ARQUIVO = "./curriculo_information/csv_information/dados_relevantes.csv"
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
    #visualizar_chunks(dados_processados)

    # Gerar embeddings e criar DataFrame
    #tempo_inicio = time.time()
    #listas_embeddings, df_final = gerar_embeddings_e_criar_dataframe(dados_processados)
    #tempo_fim = time.time()
    #print(f"Duração da geração de embeddings: {tempo_fim-tempo_inicio:.2f} segundos")

    # Visualizar as embeddings no dataframe
    #visualizar_dataframe(df_final)
    
    print("\n\n\n")
    
    # Criar conexão e popular o banco
    #criar_conexao_e_inserir_dados(df_final)
    
    # Gerar tags
    client = criar_client()
    tags_por_pesquisador, tags_globais = generate_tags_pipeline(client, dados_processados)
    visualize_tags(tags_por_pesquisador, tags_globais)
    quant_tags = len(tags_globais)
    print(f"Quantidade de tags globais: {quant_tags}")    
    
main()