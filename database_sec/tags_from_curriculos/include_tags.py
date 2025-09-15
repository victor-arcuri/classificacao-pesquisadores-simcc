import pandas as pd
from sqlalchemy import create_engine, text
import os
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
            INSERT INTO researcher_tags (name)
            VALUES (:name)
            ON CONFLICT (name) DO NOTHING
        """)

        with engine.begin() as conn:
            for tag_name in tags_globais:
                parametros = {"name": tag_name}
                conn.execute(sql, parametros)
        
        print(f"Operação de inserção de tags concluída com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro ao inserir as tags: {e}")