import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import numpy as np

def criar_conexao_e_inserir_dados(df_embeddings_curriculos):
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
            INSERT INTO curriculos (id_pesquisador, long_embeddings, short_embeddings)
            VALUES (:id, :emb_p, :emb_l)
            ON CONFLICT (id_pesquisador) DO UPDATE SET
                long_embeddings = EXCLUDED.long_embeddings,
                short_embeddings = EXCLUDED.short_embeddings;
        """)

        with engine.begin() as conn:
            for row in df_embeddings_curriculos.itertuples():
                conn.execute(sql, {
                    "id": row.id_pesquisador,
                    "emb_p": row.long_embeddings,
                    "emb_l": row.short_embeddings
                })
        
        print("Dados de currículos inseridos/atualizados com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")