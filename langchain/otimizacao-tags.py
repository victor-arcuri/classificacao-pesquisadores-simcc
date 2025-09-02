from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field

import numpy as np
import psycopg
import dotenv
import getpass
import os
import ast 

class RefinedGroup(BaseModel):
    group_name: str = Field(description="O nome único que melhor representa o grupo de tags próximas")
    removed_tags: List[str] = Field(description="Uma lista com o ID de cada tag removida do grupo por não pertencer a ele")

class State(TypedDict):
    """Estado passado para cada etapa do Grafo."""

    all_tags_data: Dict[str, List[Dict[str, Any]]]
    tag_groups: Dict[str, List[Dict[str, Any]]]

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

    @staticmethod
    def set_similarity_threshold():
        if not os.environ.get("SIMILARITY_THRESHOLD"):
            os.environ["SIMILARITY_THRESHOLD"] = getpass.getpass("Enter the Similarity Threshold value: ")


class TagCleanerAgent:
    """
    Agente que lê, processa e gera uma query de inserção para tags otimizadas.
    """

    def __init__(self, db_url: str):

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.structured_llm = self.llm.with_structured_output(RefinedGroup)

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        

        self.db_url = db_url

        self.embeddings = embeddings
        
    def get_all_tags_from_db(self, state: State) -> Dict[str, List[Dict[str, Any]]] :
        """Busca todas as tags e seus embeddings no banco de dados."""

        all_tags = []
        with psycopg.connect(self.db_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT id, name, embedding FROM "public"."researcher_tags"')
                for row in cursor.fetchall():
                    if row[2] is not None:
                        all_tags.append({
                            "id": row[0],
                            "name": row[1],
                            "embedding": np.array(ast.literal_eval(row[2]), dtype=np.float32),
                        })
                    else:
                        print(f"Aviso: Tag '{row[1]}' (ID: {row[0]}) foi ignorada por não possuir embedding.")
        print(f"Encontradas {len(all_tags)} tags para processamento.")
        return {"all_tags_data": all_tags}

    def clean_and_group_tags(self, state: State) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa tags similares"""

        SIMILARITY_THRESHOLD = float(os.environ["SIMILARITY_THRESHOLD"]);

        all_tags = state["all_tags_data"]
        groups = []
        processed_tags = set()
        for i in range(len(all_tags)):
            tag_a = all_tags[i]
            if (tag_a["id"] in processed_tags):
                continue

            current_group = {
                "name":"",
                "embedding":"",
                "tags": []
            }
            current_group["tags"].append(tag_a)

            processed_tags.add(tag_a["id"])
            for j in range(i+1, len(all_tags)):
                tag_b = all_tags[j]
                if (tag_b["id"]  in processed_tags):
                    continue

                similarity = np.dot(tag_a["embedding"], tag_b["embedding"]) / (np.linalg.norm(tag_a["embedding"]) * np.linalg.norm(tag_b["embedding"]))
                distance = 1 - similarity

                if (similarity  >= SIMILARITY_THRESHOLD):
                    current_group["tags"].append(tag_b)
                    processed_tags.add(tag_b["id"])

            if (len(current_group["tags"]) > 1):
                groups.append(current_group)

        return {"tag_groups": groups}

    def define_group_names(self, state: State):
        """Remove tags estrangeiras e escolhe um nome para cada grupo de tags."""

        groups = state["tag_groups"]

        for tag_group in groups:
            tags = [(tag["name"], tag["id"]) for tag in tag_group["tags"]]
            prompt = f"""
                Você é um especialista em curadoria de dados. Sua tarefa é analisar um grupo de tags que representam áreas de estudo de pesquisadores, 
                as quais foram agrupadas por similaridade matemática, e refinar este grupo.

                1.  Primeiro, analise a seguinte lista de tags no formato (nome da tag, id): {tags}
                2.  Remova qualquer tag que seja um outlier ou que não se encaixe perfeitamente com o tema central do grupo.
                3.  A partir da lista de tags refinada, escolha o nome mais claro, comum e representativo para servir como substitutivo para cada tag 
                individualmente do grupo. O nome não deve ser longo e não muito abrangente nem genérico.
            """
            response = self.structured_llm.invoke(prompt)
            tag_group["name"] = response.group_name;
            for tag in tag_group["tags"]:
                if (tag["id"] in response.removed_tags):
                    tag_group.remove(tag)

        return {"tag_groups": groups}
        
    def generate_embeddings_for_groups(self, state: State):
        """Gera os embeddings para os grupos de tags criados"""
        groups = state["tag_groups"]
        for tag_group in groups:
            tag_group["embedding"] = self.embeddings.embed_query(tag_group["name"])
        
        return {"tag_groups": groups}
    
    def generate_final_query(self, state: State):
        """Gera a query de INSERT final a partir dos nomes limpos."""

    def create_graph(self):
        """Cria o grafo LangGraph com o fluxo de otimização."""

        graph_builder = StateGraph(State)

        graph_builder.add_node("get_tags", self.get_all_tags_from_db)
        graph_builder.add_node("clean_tags", self.clean_and_group_tags)
        graph_builder.add_node("define_group_names", self.define_group_names)
        graph_builder.add_node("generate_embeddings", self.generate_embeddings_for_groups)
        graph_builder.add_node("generate_query", self.generate_final_query)

        graph_builder.set_entry_point("get_tags")
        graph_builder.add_edge("get_tags", "clean_tags")
        graph_builder.add_edge("clean_tags", "define_group_names")
        graph_builder.add_edge("define_group_names", "generate_embeddings")
        graph_builder.add_edge("generate_embeddings", "generate_query")
        graph_builder.add_edge("generate_query", END)

        return graph_builder.compile()

def main():
    db_url = os.environ["DB_URL"]
    agent = TagCleanerAgent(db_url)
    graph = agent.create_graph()
    final_state = graph.invoke({})

if __name__ == "__main__":
    dotenv.load_dotenv()
    Environment.load_llm_api_keys()
    Environment.load_db_url()
    main()