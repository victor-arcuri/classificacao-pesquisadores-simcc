import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import numpy as np

def criar_conexao_e_inserir_tags_dos_pesquisadores(tags_pesquisadores):
    
    # Para cada pesquisador, tem uma lista de tags
    # Colocar id_tag e id_pesquisador
    
    """
    Cria uma conexão com o banco de dados e insere ou atualiza os embeddings de currículos.
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

        sql = text("""
            INSERT INTO researcher_tags_on_researchers (
            )
            VALUES (
            )
            ON CONFLICT (id_pesquisador) DO UPDATE SET
        """)

        with engine.begin() as conn:
            for row in tags_pesquisadores.itertuples():
                parametros = {}
                
                conn.execute(sql, parametros)
        
        print("Dados de currículos inseridos/atualizados com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")