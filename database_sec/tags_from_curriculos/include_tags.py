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

        usuario = os.getenv('CURRICULO_DB_USER')
        senha = os.getenv('CURRICULO_DB_PASSWORD')
        host = 'localhost'
        porta = os.getenv('CURRICULO_DB_PORT_HOST')
        banco = os.getenv('CURRICULO_DB_NAME')
        
        connection_string = f'postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}'
        engine = create_engine(connection_string)

        # SQL ajustado para receber apenas o nome e ignorar duplicatas
        sql = text("""
            INSERT INTO researcher_tags (name, embedding)
            VALUES (:name, :embedding)
            ON CONFLICT (name) DO NOTHING
        """)

        dados = []
        embeddings_model = OpenAIEmbeddings()
        for tag_name in tags_globais:
            try:
                vetores_embedding_tag = embeddings_model.embed_documents(tag_name)
                embedding_tag = np.mean(vetores_embedding_tag, axis=0).tolist()
                dados.append({"name": tag_name, "embedding": embedding_tag})
            except Exception as e:
                print("\n\033[91m Ocorreu um erro ao gerar os embeddings.\033[0m")
                print(f"Erro: {e}")

        with engine.begin() as conn:
            conn.execute(sql, dados)  
        
        print(f"Operação de inserção de tags concluída com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro ao inserir as tags: {e}")