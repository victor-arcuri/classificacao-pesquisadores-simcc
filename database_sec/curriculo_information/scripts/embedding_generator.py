import pandas as pd
import numpy as np
from langchain_openai import OpenAIEmbeddings

def gerar_embeddings_e_criar_dataframe(dados_processados):
    """
    Recebe os chunks processados, gera embeddings para cada coluna individualmente 
    e monta o DataFrame final.

    Retorna:
        pd.DataFrame: Um DataFrame com o id do pesquisador e colunas de embedding 
                      para cada campo de dados (ex: abstract_embedding, articles_embedding).
    """
    print("\n\n\nIniciando a geração de embeddings com a OpenAI...")
    try:
        embeddings_model = OpenAIEmbeddings()
        lista_para_df = []
        
        i = 1
        for id_pesquisador, chunks_data in dados_processados.items():
            if i > 5:
                print("\nLimite de 5 pesquisadores atingido para o teste.")
                break
            
            print(f"\nProcessando pesquisador {i}: {id_pesquisador}")
            
            nova_linha = {'id_pesquisador': id_pesquisador}

            # Itera sobre cada coluna de dados (abstract, articles, etc.) do pesquisador
            for nome_coluna, lista_de_chunks in chunks_data.items():
                if nome_coluna == 'metadata':
                    continue
                
                embedding_vetor = []
                if lista_de_chunks:
                    print(f"  -> Gerando embeddings para a coluna '{nome_coluna}' ({len(lista_de_chunks)} chunks)...")
                    embeddings_da_coluna = embeddings_model.embed_documents(lista_de_chunks)
                    # Calcula a média dos vetores para criar um único embedding representativo
                    embedding_vetor = np.mean(embeddings_da_coluna, axis=0).tolist()
                
                # Adiciona o vetor de embedding ao dicionário da linha
                # O nome da nova coluna será, por exemplo, 'abstract_embeddings'
                nova_linha[f'{nome_coluna}_embeddings'] = embedding_vetor

            lista_para_df.append(nova_linha)
            i += 1

        print(f"\nEmbeddings gerados com sucesso para {len(lista_para_df)} pesquisadores.")
        return lista_para_df, pd.DataFrame(lista_para_df)

    except Exception as e:
        print("\n\033[91m Ocorreu um erro ao gerar os embeddings ou criar o DataFrame.\033[0m")
        print("Verifique se a sua chave da API da OpenAI foi inserida corretamente.")
        print(f"Erro: {e}")
        return pd.DataFrame()