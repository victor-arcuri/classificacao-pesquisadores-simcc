from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path

import numpy as np
import psycopg
import dotenv
import getpass
import os
import ast 
import json
from datetime import datetime

class LogTag(BaseModel):
    """Interface base das tags do log"""
    id: str
    name: str

class LogGroupedTag(LogTag):
    """Interface das tags dos grupos do log"""
    removed: bool

class LogTagGroup(BaseModel):
    """Interface dos grupos do log"""
    name: str
    embedding: str
    created: bool
    tags: List[LogGroupedTag]

class LogSchema(BaseModel):
    """Interface do log"""
    groups: List[LogTagGroup] = []

class Log:
    """Representa os logs salvos no diretório de logs e suas funções"""
    def __init__(self, path=None, groups=[]):
        self.path = path
        self.groups = groups

    def set_groups(self, groups: List[LogTagGroup]):
        """Define os grupos do log"""
        self.groups = groups;
        return self;
    
    def save_log(self):
        """Atualiza os valores do log salvando em seu arquivo"""
        groups = self.groups
        formatted_groups = []
        for group in groups:
            formatted_group = {
                "name": group["name"],
                "embedding": group["embedding"],
                "created": group["created"],
                "tags": [
                    {
                        "id": str(tag["id"]),
                        "removed": tag["removed"],
                        "name": tag["name"]
                    } for tag in group["tags"]
                ]
            }
            formatted_groups.append(formatted_group)
            

        log = LogSchema(groups=formatted_groups)
        json_string = log.model_dump_json(indent=4)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(json_string)
        
class RefinedGroup(BaseModel):
    """Representa a estrutura do output da classificação da LLM"""
    group_name: str = Field(description="O nome único que melhor representa o grupo de tags próximas")
    removed_tags: List[str] = Field(description="Uma lista com o ID de cada tag removida do grupo por não pertencer a ele")

class State(TypedDict):
    """Estado passado para cada etapa do Grafo."""

    all_tags_data: List[Dict[str, Any]]
    tag_groups: List[Dict[str, Any]]


class LogAgent():
    """Agente que regula a criação e manipulação de logs"""
    def __init__(self, logsPath=None):
        if (logsPath==None):
            logsPath = Path.cwd().joinpath("logs")
            logsPath.mkdir(parents=True, exist_ok=True)

        self.logsPath = logsPath
        self.currentLog: Log = None

    @staticmethod
    def _current_timestamp():
        """Retoma o timestamp atual formatado"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def create_new_log(self, groups=[]) -> Log:
        """Cria um novo Log com os grupos de tags passados"""
        newLogPath = self.logsPath.joinpath(self._current_timestamp()) 
        os.mkdir(newLogPath)
        file = open(newLogPath.joinpath("log.json"), 'w')
        file.close()
        log = Log(path=newLogPath.joinpath("log.json"), groups=groups)
        self.currentLog = log
        return log

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

    def __init__(self, db_url: str, logger: LogAgent):

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        self.structured_llm = self.llm.with_structured_output(RefinedGroup)
        
        self.logger = logger;
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        self.db_url = db_url

        self.embeddings = embeddings

        
    def get_all_tags_from_db(self, state: State) -> Dict[str, List[Dict[str, Any]]] :
        """Busca todas as tags e seus embeddings no banco de dados."""
        
        print("\n--- EXTRAÇÃO DE TAGS DO BANCO ---")

        print("Iniciando conexão com banco de dados...")
        all_tags = []
        try:
            with psycopg.connect(self.db_url) as connection:
                print("Conexão bem sucedida!")
                with connection.cursor() as cursor:
                    print("Extraindo tags...")
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
        except psycopg.OperationalError as e:
            print(f'Erro de conexão: {e}')
            self.logger.create_new_log()

        print("Extração bem sucedida!")
        print(f"Encontradas {len(all_tags)} tags para processamento.")

        return {"all_tags_data": all_tags}

    def clean_and_group_tags(self, state: State) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa tags similares"""

        print("\n--- AGRUPAMENTO POR SIMILARIDADE DE TAGS ---")

        SIMILARITY_THRESHOLD = float(os.environ["SIMILARITY_THRESHOLD"]);

        all_tags = state["all_tags_data"]
        groups = []
        processed_tags = set()
        print(f'Verificando {len(all_tags)} tags...')
        for i in range(len(all_tags)):
            tag_a = all_tags[i]
            tag_a["removed"] = False
            if (tag_a["id"] in processed_tags):
                continue

            current_group = {
                "name":"",
                "embedding":"",
                "created": False,
                "tags": []
            }
            current_group["tags"].append(tag_a)
            processed_tags.add(tag_a["id"])
            for j in range(i+1, len(all_tags)):
                tag_b = all_tags[j]
                tag_b["removed"] = False
                if (tag_b["id"]  in processed_tags):
                    continue

                similarity = np.dot(tag_a["embedding"], tag_b["embedding"]) / (np.linalg.norm(tag_a["embedding"]) * np.linalg.norm(tag_b["embedding"]))
                distance = 1 - similarity

                if (similarity  >= SIMILARITY_THRESHOLD):
                    current_group["tags"].append(tag_b)
                    processed_tags.add(tag_b["id"])

            if (len(current_group["tags"]) > 1):
                groups.append(current_group)
        
        print(f'Agrupamento bem sucedido!')
        print(f'Formados {len(groups)} grupos de tags!')
        
        self.logger.create_new_log(groups=groups).save_log()

        return {"tag_groups": groups}

    def define_group_names(self, state: State):
        """Remove tags estrangeiras e escolhe um nome para cada grupo de tags."""

        print("\n--- LIMPEZA DE GRUPOS DE TAGS E NOMEAÇÃO  ---")

        groups = state["tag_groups"]

        print(f'Total de {len(groups)} grupos de tags a serem limpados e nomeados!')

        for tag_group in groups:
            tags = [(tag["name"], tag["id"]) for tag in tag_group["tags"]]
            prompt = f"""
                Você é um taxonomista acadêmico. Sua tarefa é criar uma tag canônica para o seguinte grupo de tags de pesquisa: {tags}.

                A tag canônica deve ser:
                - Um nome de campo de estudo formal e específico (ex: "Engenharia de Software", não "Software").
                - Clara na relação entre áreas (ex: "Tecnologia na Educação", não "Educação e Tecnologia").
                - Concisa, mas não genérica.

                Bons exemplos: "Ontologia", "Ciência de Dados", "Inteligência Artificial", "Gestão de TI", "Matemática Aplicada".

                Responda APENAS com a tag final.
            """

            response = self.structured_llm.invoke(prompt)
            tag_group["name"] = response.group_name
            tag_group["tags"] = [tag for tag in tag_group["tags"] if tag["id"] not in response.removed_tags]
            print(f'Total de {len(tag_group["tags"])} tags unificadas na Tag \'{response.group_name}\'!')
        
        print("Limpeza e nomeação bem sucedidas!")

        self.logger.currentLog.set_groups(groups).save_log()

        return {"tag_groups": groups}
        
    def generate_embeddings_for_groups(self, state: State):
        """Gera os embeddings para os grupos de tags criados"""

        print("\n--- GERAÇÃO DE EMBEDDINGS DOS GRUPOS DE TAGS UNIFICADAS  ---")
        
        groups = state["tag_groups"]

        print(f'Total de {len(groups)} grupos de tags a gerar embeddings!')

        group_names = [group["name"] for group in groups]
        group_embeddings = self.embeddings.embed_documents(group_names)

        for i, group in enumerate(groups):
            group['embedding'] = str(group_embeddings[i])
        
        print(f'Geração de embeddings finalizada com sucesso!')

        self.logger.currentLog.set_groups(groups).save_log()

        return {"tag_groups": groups}
    
    def remove_and_create_tags(self, state: State):
        """Remove as tags dos grupos, substituindo-as pela tag unificada de seu grupo"""
        print("\n--- INSERÇÃO DE NOVOS GRUPOS E REMOÇÃO DE TAGS REDUNDANTED  ---")

        print("Conectando com banco de dados...")
        groups = state["tag_groups"]
        try:
            with psycopg.connect(self.db_url) as connection:
                print("Conexão bem sucedida!")
                with connection.cursor() as cursor:
                    for tag_group in groups:
                        print(f'Inserindo e removendo tags do grupo \'{tag_group["name"]}\'')
                        tag_ids = tuple([tag["id"] for tag in tag_group["tags"]])
                        cursor.execute('INSERT INTO "public"."researcher_tags" (name, embedding) VALUES (%s, %s)', (tag_group["name"], tag_group["embedding"]))
                        tag_group["created"] = True
                        placeholders = ', '.join(['%s'] * len(tag_ids))
                        cursor.execute(f'DELETE FROM "public"."researcher_tags" WHERE id IN ({placeholders})', tag_ids)
                        for tag in tag_group["tags"]:
                            tag["removed"] = True
        except Error as e:
            print(f'Erro de conexão: {e}')
            self.logger.currentLog.set_groups(groups).save_log()

        self.logger.currentLog.set_groups(groups).save_log()
        print("Inserção realizada com sucesso!")

            
        

    def create_graph(self):
        """Cria o grafo LangGraph com o fluxo de otimização."""

        graph_builder = StateGraph(State)

        graph_builder.add_node("get_tags", self.get_all_tags_from_db)
        graph_builder.add_node("clean_tags", self.clean_and_group_tags)
        graph_builder.add_node("define_group_names", self.define_group_names)
        graph_builder.add_node("generate_embeddings", self.generate_embeddings_for_groups)
        graph_builder.add_node("remove_and_create_tags", self.remove_and_create_tags)

        graph_builder.set_entry_point("get_tags")
        graph_builder.add_edge("get_tags", "clean_tags")
        graph_builder.add_edge("clean_tags", "define_group_names")
        graph_builder.add_edge("define_group_names", "generate_embeddings")
        graph_builder.add_edge("generate_embeddings", "remove_and_create_tags")
        graph_builder.add_edge("remove_and_create_tags", END)

        return graph_builder.compile()

def main():
    usuario = os.getenv('DB_USERNAME')
    senha = os.getenv('DB_SENHA')
    host = 'localhost'
    porta = os.getenv('DB_PORT_HOST')
    banco = os.getenv('DB_NAME')

    db_url = f"postgresql://{usuario}:{senha}@{host}:{porta}/{banco}"
    logger = LogAgent()
    agent = TagCleanerAgent(db_url, logger)
    graph = agent.create_graph()
    final_state = graph.invoke({})

if __name__ == "__main__":
    dotenv.load_dotenv()
    Environment.load_llm_api_keys()
    Environment.set_similarity_threshold() 
    main()