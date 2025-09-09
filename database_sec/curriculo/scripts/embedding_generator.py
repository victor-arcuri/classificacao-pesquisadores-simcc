import pandas as pd
import numpy as np
from langchain_openai import OpenAIEmbeddings

def gerar_embeddings_e_criar_dataframe(dados_processados):
    """
    Recebe os chunks processados, gera embeddings e monta o DataFrame final.

    Retorna:
        pd.DataFrame: Um DataFrame com as colunas 'id_pesquisador', 'embeddings_prosa' e 'embeddings_lista'.
    """
    print("\n\n\nIniciando a geração de embeddings com a OpenAI...")
    try:
        embeddings_model = OpenAIEmbeddings()
        lista_para_df = []
        
        i = 1
        for id_pesquisador, chunks_data in dados_processados.items():
            # Condição de parada
            if i > 5:
                print("\nLimite de 5 pesquisadores atingido para o teste.")
                break
            
            print(f"\nProcessando pesquisador {i}: {id_pesquisador}")
            
            embeddings_prosa = []
            if chunks_data["prose_chunks"]:
                embeddings_prosa = embeddings_model.embed_documents(chunks_data["prose_chunks"])
                print("  -> Embeddings de prosa criados!")

            embeddings_lista = []
            if chunks_data["list_chunks"]:
                embeddings_lista = embeddings_model.embed_documents(chunks_data["list_chunks"])
                print("  -> Embeddings de lista criados!")

            prose_embeddings_vector = np.mean(embeddings_prosa, axis=0).tolist() if embeddings_prosa else []
            list_embeddings_vector = np.mean(embeddings_lista, axis=0).tolist() if embeddings_lista else []    

            lista_para_df.append({
                'id_pesquisador': id_pesquisador,
                'long_embeddings': prose_embeddings_vector,
                'short_embeddings': list_embeddings_vector
            })
            
            i += 1

        print(f" Embeddings gerados com sucesso para {len(lista_para_df)} pesquisadores.")
        return pd.DataFrame(lista_para_df)

    except Exception as e:
        print("\n\033[91m Ocorreu um erro ao gerar os embeddings ou criar o DataFrame.\033[0m")
        print("Verifique se a sua chave da API da OpenAI foi inserida corretamente.")
        print(f"Erro: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro