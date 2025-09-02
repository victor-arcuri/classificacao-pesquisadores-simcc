from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.pgvector import PGVector

import numpy as np
import psycopg
import dotenv
import getpass
import os

class State(TypedDict):
    """Estado passado para cada etapa do Grafo."""
    all_tags_data: Dict[str, List[Dict[str, any]]]

class Environment:
    """Classe para carregar variáveis de ambiente de forma segura."""
    @staticmethod
    def load_llm_api_keys():
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
    
    @staticmethod
    def load_db_url():
        if not os.environ.get("DB_URL"):
            os.environ["DB_URL"] = getpass.getpass("Enter the Database connection URL: ")

class TagCleanerAgent:
    """
    Agente que lê, processa e gera uma query de inserção para tags otimizadas.
    """
    def __init__(self, db_url: str, collection_name: str):

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        self.collection_name = collection_name

        self.vector_store = PGVector(
            connection_string=db_url,
            embedding_function=embeddings,
            collection_name=collection_name,
        )

        print(f"Conectado à Vector Store '{collection_name}' com sucesso.")
        

    def get_all_tags_from_db(self, state: State) -> Dict[str, List[Dict[str, any]]] :
        """Busca todas as tags e seus embeddings no banco de dados."""
        all_tags = []
        with psycopg.connect(self.vector_store.connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT uuid FROM langchain_pg_collection WHERE name = '{self.collection_name}'")
                collection_id_result = cursor.fetchone()
                if not collection_id_result:
                    raise ValueError(f"Coleção '{self.collection_name}' não encontrada.")
                collection_id = collection_id_result[0]
                cursor.execute(f"SELECT document FROM langchain_pg_embedding WHERE collection_id = '{collection_id}'")
                for row in cursor.fetchall():
                    all_tags.append({
                        "id": row[0],
                        "name": row[1],
                        "embedding": np.array(row[2]),
                    })
        print(f"Encontradas {len(all_tags)} tags para processamento.")
        return {"all_tags_data": all_tags}
        

        
        print(f"Encontradas {len(all_names)} tags.")
        return {"all_tags": all_names}


    def clean_and_group_tags(self, state: State):
        """Agrupa tags similares e escolhe um nome canônico para cada grupo."""
        all_tags = state["all_tags"]

    def generate_embeddings_for_groups(self, state: State):
        """Gera os embeddings para os grupos de tags criados"""

    
    def generate_final_query(self, state: State):
        """Gera a query de INSERT final a partir dos nomes limpos."""

    def create_graph(self):
        """Cria o grafo LangGraph com o fluxo de otimização."""

        graph_builder = StateGraph(State)

        graph_builder.add_node("get_tags", self.get_all_tags_from_db)
        graph_builder.add_node("clean_tags", self.clean_and_cluster_tags)
        graph_builder.add_node("generate_embeddings", self.generate_embeddings_for_groups)
        graph_builder.add_node("generate_query", self.generate_final_query)

        graph_builder.set_entry_point("get_tags")
        graph_builder.add_edge("get_tags", "clean_tags")
        graph_builder.add_edge("clean_tags", "generate_embeddings")
        graph_builder.add_edge("generate_embeddings", "generate_query")
        graph_builder.add_edge("generate_query", END)

        return graph_builder.compile()

def main():
    db_url = os.environ["DB_URL"]
    collection_name="researcher_tags"
    agent = TagCleanerAgent(db_url, collection_name)
    graph = agent.create_graph()

if __name__ == "__main__":
    dotenv.load_dotenv()
    Environment.load_llm_api_keys()
    Environment.load_db_url()
    main()