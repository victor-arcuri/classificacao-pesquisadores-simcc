import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import numpy as np

def criar_conexao_e_inserir_dados(df_embeddings_curriculos):
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

        # Query SQL corrigida para todas as colunas
        sql = text("""
            INSERT INTO curriculos (
                id_pesquisador, abstract_embeddings, articles_embeddings, 
                project_name_embeddings, description_project_embeddings, 
                great_area_embeddings, area_specialty_embeddings, 
                patent_embeddings, book_chapter_embeddings, event_name_embeddings
            )
            VALUES (
                :id_pesquisador, :abstract_embeddings, :articles_embeddings, 
                :project_name_embeddings, :description_project_embeddings, 
                :great_area_embeddings, :area_specialty_embeddings, 
                :patent_embeddings, :book_chapter_embeddings, :event_name_embeddings
            )
            ON CONFLICT (id_pesquisador) DO UPDATE SET
                abstract_embeddings = EXCLUDED.abstract_embeddings,
                articles_embeddings = EXCLUDED.articles_embeddings,
                project_name_embeddings = EXCLUDED.project_name_embeddings,
                description_project_embeddings = EXCLUDED.description_project_embeddings,
                great_area_embeddings = EXCLUDED.great_area_embeddings,
                area_specialty_embeddings = EXCLUDED.area_specialty_embeddings,
                patent_embeddings = EXCLUDED.patent_embeddings,
                book_chapter_embeddings = EXCLUDED.book_chapter_embeddings,
                event_name_embeddings = EXCLUDED.event_name_embeddings;
        """)

        with engine.begin() as conn:
            for row in df_embeddings_curriculos.itertuples():
                parametros = {
                    "id_pesquisador": row.id_pesquisador,
                    "abstract_embeddings": row.abstract_embeddings,
                    "articles_embeddings": row.articles_embeddings,
                    "project_name_embeddings": row.project_name_embeddings,
                    "description_project_embeddings": row.description_project_embeddings,
                    "great_area_embeddings": row.great_area_embeddings,
                    "area_specialty_embeddings": row.area_specialty_embeddings,
                    "patent_embeddings": row.patent_embeddings,
                    "book_chapter_embeddings": row.book_chapter_embeddings,
                    "event_name_embeddings": row.event_name_embeddings
                }
                conn.execute(sql, parametros)
        
        print("Dados de currículos inseridos/atualizados com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")