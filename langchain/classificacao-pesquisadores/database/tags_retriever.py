from database.singleton import DatabaseConnection
from psycopg2.extensions import connection, cursor
from typing import Optional
import psycopg2

def tags_retrieve() -> list[(str, str)]:
    """
    Busca todas as tags do banco de dados.
    """
    db = DatabaseConnection()
    
    conn: Optional[connection] = db.get_connection()
    
    tags: list[str] = []

    if conn:
        try:
            with conn.cursor() as cur:

                cur.execute("SELECT id, name FROM researcher_tags")
                
                results = cur.fetchall()
                
                tags = [(row[0], row[1]) for row in results]
                
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"Erro ao buscar tags: {e}")
    
    else:
        print("Não foi possível conectar ao banco de dados.")

    return tags