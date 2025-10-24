from database.singleton import DatabaseConnection
from psycopg2.extensions import connection, cursor
from typing import Optional, List, Tuple, Dict
import psycopg2

def relation_inserter(tags_for_researchers: Dict[str, List[Tuple[str, str]]]):
    """
    Insere todas as relações entre pesquisadores e tags.
    """
    db = DatabaseConnection()
    conn = db.get_connection()
    
    inserted_count = 0

    if conn:
        try:
            with conn.cursor() as cur:
                    for researcher_id, tags_list in tags_for_researchers.items():
                        for tag_tuple in tags_list:
                            tag_id = tag_tuple[0]
                            sql_query = """
                                INSERT INTO researcher_tags_on_researchers (researcher_id, tag_id) 
                                VALUES (%s, %s)
                                ON CONFLICT (researcher_id, tag_id) DO NOTHING;
                            """
                            cur.execute(sql_query, (researcher_id, tag_id))
                            inserted_count += cur.rowcount

            conn.commit()
            print(f"Processamento de relações finalizado. {inserted_count} novas relações inseridas.")
                
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"Erro ao inserir relações: {e}")
            if conn:
                conn.rollback()
    
    else:
        print("Não foi possível conectar ao banco de dados.")

    return