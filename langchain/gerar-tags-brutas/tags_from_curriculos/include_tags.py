import numpy as np
import os
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def criar_conexao_e_inserir_tags_globais(tags_globais: list[str]):
    """
    Cria uma conexão com o banco de dados e insere as tags da lista,
    ignorando as que já existem.
    """
    try:
        load_dotenv()

        usuario = os.getenv('DB_USERNAME')
        senha = os.getenv('DB_SENHA')
        host = 'localhost'
        porta = os.getenv('DB_PORT')
        banco = os.getenv('DB_NAME')
        
        connection_string = f'postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}'
        engine = create_engine(connection_string)

        # SQL ajustado para receber apenas o nome e ignorar duplicatas
        sql = text("""
            INSERT INTO researcher_tags (name, embedding)
            VALUES (:name, :embedding)
        """)

        dados = []
        embeddings_model = OpenAIEmbeddings()
        
        try:
            # gera embeddings em batch
            vetores = embeddings_model.embed_documents(tags_globais)  # retorna lista de vetores
            for tag_name, vetor in zip(tags_globais, vetores):
                try:
                    dados.append({"name": tag_name, "embedding": np.array(vetor, dtype=float).tolist()})
                except Exception as e:
                    print(f"Erro ao processar embedding da tag '{tag_name}': {e}")

            # insere os dados no banco
            try:
                with engine.begin() as conn:
                    conn.execute(sql, dados)
                print("Inserção das tags concluída com sucesso!")
            except Exception as e:
                print(f"Erro ao inserir os dados no banco: {e}")

        except Exception as e:
            print(f"Erro ao gerar embeddings: {e}")


    except Exception as e:
        print(f"Ocorreu um erro ao inserir as tags: {e}")