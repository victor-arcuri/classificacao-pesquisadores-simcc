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

''' 
- inserir todas as tags (sem considerar hierarquia nenhuma também) depois de otimizado para todos os pesquisadores
- incluir relação de todas as tags para todos os pesquisadores (sem considerar hierarquia nenhuma, antes ou depois da otimização? como quando vou para otimização
não tenho mais o ID do pesquisador, então poderia ser antes e limpar os ids de tags que não estivessem mais lá?)
- incluir tags que não foram agrupadas (isoladas) na tabela de tags
- criar condição para tags pais e filhas iguais
- criar dicionários com chaves (tags_pais) com valores (tags_filhas) para facilitar inserção no banco
'''

DAD_TAGS = [
    # Ciências e Conhecimento
    "Filosofia", "Sociologia", "Antropologia", "Psicologia", "História", "Geografia",
    "Educação", "Ciência Política", "Religião", "Ética",

    # Ciências Exatas e Naturais
    "Matemática", "Física", "Química", "Biologia", "Astronomia", "Geologia",
    "Ecologia", "Meteorologia", "Oceanografia",

    # Tecnologia e Computação
    "Tecnologia", "Inteligência Artificial", "Computação", "Programação",
    "Ciência de Dados", "Machine Learning", "Cibersegurança", "Robótica",
    "Internet das Coisas", "Blockchain", "Realidade Virtual", "Engenharia de Software",
    "Redes de Computadores",

    # Negócios e Gestão
    "Administração", "Gestão", "Empreendedorismo", "Marketing", "Finanças",
    "Contabilidade", "Recursos Humanos", "Economia", "Logística",
    "Inovação", "Planejamento Estratégico",

    # Meio Ambiente e Sustentabilidade
    "Sustentabilidade", "Energia Renovável", "Mudanças Climáticas",
    "Conservação Ambiental", "Economia Verde", "Agricultura Sustentável",
    "Gestão Ambiental", "ESG",

    # Direito e Sociedade
    "Direito", "Justiça", "Legislação", "Direitos Humanos",
    "Políticas Públicas", "Cidadania", "Segurança Pública",

    # Saúde e Bem-Estar
    "Saúde", "Medicina", "Enfermagem", "Nutrição", "Psicologia da Saúde",
    "Esportes", "Qualidade de Vida",

    # Artes e Cultura
    "Arte", "Música", "Teatro", "Cinema", "Fotografia", "Literatura",
    "Cultura", "Design", "Moda", "Arquitetura",

    # Comunicação e Mídia
    "Comunicação", "Jornalismo", "Publicidade", "Relações Públicas",
    "Mídias Digitais", "Redes Sociais", "Produção de Conteúdo", "Linguística",

    # Engenharia e Indústria
    "Engenharia", "Engenharia Civil", "Engenharia Elétrica", "Engenharia Mecânica",
    "Engenharia de Produção", "Engenharia Química", "Indústria 4.0",
    "Construção", "Manufatura",

    # Ciência e Inovação Aplicada
    "Pesquisa", "Inovação Tecnológica", "Desenvolvimento Científico",
    "Startups", "Propriedade Intelectual",

    # Global e Internacional
    "Relações Internacionais", "Comércio Exterior", "Geopolítica",
    "Cooperação Internacional",

    # Sociedade e Cultura Contemporânea
    "Diversidade", "Inclusão", "Gênero", "Juventude",
    "Cultura Digital", "Comportamento",

    # Educação e Formação
    "Ensino", "Pedagogia", "Didática", "Educação a Distância",
    "Formação Profissional", "Aprendizagem",

]


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
            if "dad_tags" in group:
                formatted_group["dad_tags"] = group["dad_tags"]
            formatted_groups.append(formatted_group)
            

        log = LogSchema(groups=formatted_groups)
        json_string = log.model_dump_json(indent=4)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(json_string)
        
class RefinedGroup(BaseModel):
    """Representa a estrutura do output da classificação da LLM"""
    group_name: str = Field(description="O nome único que melhor representa o grupo de tags próximas")
    removed_tags: List[str] = Field(description="Uma lista com o ID de cada tag removida do grupo por não pertencer a ele")

class DadTagClassification(BaseModel):
    """Estrutura para a classificação de um grupo de tags em dad_tags."""
    dad_tags: List[str] = Field(description="Uma lista de dad_tags correspondentes para o grupo de tags.")

class State(TypedDict):
    """Estado passado para cada etapa do Grafo."""

    all_tags_data: List[Dict[str, Any]]
    tag_groups: List[Dict[str, Any]]
    unique_dad_tags: List[str]


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
        self.dad_tag_classifier_llm = self.llm.with_structured_output(DadTagClassification)
        
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

        # Coletar as tags que ficaram de fora dos grupos
        tags_not_in_groups = []
        for tag in all_tags:
            if tag["name"] not in groups["tags"]:
                tags_not_in_groups.append(tag)
        
        self.logger.create_new_log(groups=groups).save_log()

        return {"tag_groups": groups, "tags_not_in_groups": tags_not_in_groups}

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
                - Concisa, com no máximo 3 palavras obrigatoriamente.
                - Não misturem assuntos (ex: "Ciência de Dados" é aceitável, "Ciência de Dados e Análise Estatística" não é).
                - SEJA GENERALISTA.
                - Representativa de todas as tags do grupo.

                EXEMPLOS DE TAGS CANÔNICAS:
                - "Ciência de Dados", "Inteligência Artificial", "Gestão de TI", "Matemática", "Epidemiologia", "Pesquisa Científica", "Saúde Pública".

                Responda APENAS com a tag final.
            """

            response = self.structured_llm.invoke(prompt)
            tag_group["name"] = response.group_name
            tag_group["tags"] = [tag for tag in tag_group["tags"] if tag["id"] not in response.removed_tags]
            print(f'Total de {len(tag_group["tags"])} tags unificadas na Tag \'{response.group_name}\'!')
        
        print("Limpeza e nomeação bem sucedidas!")

        self.logger.currentLog.set_groups(groups).save_log()

        return {"tag_groups": groups}
        
    def classify_tags_for_dad_tags(self, state: State):
        """Classifica as tags em DAD ou não DAD"""
        print("\n--- CLASSIFICAÇÃO DE TAGS EM DAD OU NÃO DAD  ---")
        
        groups = state["tag_groups"][:] # Copia a lista para evitar modificar a original diretamente no loop
        tags_not_in_groups = state["tags_not_in_groups"][:]
        all_tags = groups + [{"name": tag["name"], "tags": [tag]} for tag in tags_not_in_groups]

        all_dad_tags = set()

        print(f'Total de {len(all_tags)} tags a serem classificados!')
        
        for tag in all_tags:
            # O nome do grupo já representa bem o grupo de tags
            # Não se restringir ao nome do grupo apenas
            # Ajeitar toda função aqui
            tag_name = tag["name"]
            prompt = f"""
                Você é um taxonomista sênior e especialista em categorização de áreas de pesquisa. Sua tarefa é classificar a tag de pesquisa '{tag_name}' dentro da lista de campos de conhecimento pré-definidos: {DAD_TAGS}.

                **Instruções Rigorosas:**
                1.  **Foco no Essencial:** Selecione APENAS os campos que representam a ÁREA CENTRAL e FUNDAMENTAL da tag. Evite campos que são apenas aplicações, ferramentas ou áreas relacionadas de forma indireta.
                2.  **Hierarquia:** Pense na relação hierárquica. A tag '{tag_name}' é um subcampo direto de qual campo da lista?

                **Exemplos de Classificação Correta:**
                - 'Energia Renovável' -> DEVE ser classificada em ['Sustentabilidade', 'Energia Renovável']. NÃO inclua 'Tecnologia' apenas porque usa tecnologia.
                - 'Saúde Pública' -> DEVE ser classificada em ['Saúde', 'Saúde Pública', 'Políticas Públicas']. NÃO inclua 'Sociologia', pois é um campo relacionado, mas não a disciplina central.
                - 'Modelagem Matemática' -> DEVE ser classificada em ['Matemática', 'Ciência de Dados']. NÃO inclua 'Tecnologia'.

                Responda APENAS com os campos correspondentes da lista, com no máximo 3 campos.
            """

            response = self.dad_tag_classifier_llm.invoke(prompt)

            for tag in response.dad_tags:
                all_dad_tags.add(tag)

            if len(response.dad_tags) > 1:
                # Cria um dicionário com chaves dad_tag1, dad_tag2, etc.
                dad_tag_dict = {f"dad_tag{i+1}": tag for i, tag in enumerate(response.dad_tags)}
                tag["dad_tags"] = dad_tag_dict
                print(f'A tag \'{tag_name}\' foi classificado em: {dad_tag_dict}')
            else:
                print("ERROOOO")
                # Mantém como lista se tiver 0 ou 1 elemento
                #tag["dad_tags"] = response.dad_tags 
                #print(f'O grupo \'{group_name}\' foi classificado em: {response.dad_tags}')

        self.logger.currentLog.set_groups(groups).save_log()

        # Adiciona as dad_tags recém-descobertas à lista de todas as tags
        # para que elas também possam ter seus embeddings gerados e serem inseridas no banco.
        for dad_tag_name in all_dad_tags:
            all_tags.append({"name": dad_tag_name, "tags": []}) # Adiciona como se fosse um novo grupo/tag isolada

        print(f"\nTotal de {len(all_dad_tags)} dad_tags únicas encontradas.")
        return {"tag_groups": all_tags, "unique_dad_tags": list(all_dad_tags)}

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

    def insert_dad_tags(self, state: State):
        """Insere as DAD tags que ainda não existem no banco de dados."""
        print("\n--- INSERÇÃO DE DAD TAGS NO BANCO ---")
        dad_tags = state["unique_dad_tags"]
        if not dad_tags:
            print("Nenhuma DAD tag para inserir.")
            return

        print(f"Tentando inserir {len(dad_tags)} DAD tags únicas...")
        
        dad_tags_embeddings = self.embeddings.embed_documents(dad_tags)

        try:
            with psycopg.connect(self.db_url) as connection:
                print("Conexão bem sucedida!")
                with connection.cursor() as cursor:
                    sql = 'INSERT INTO "public"."researcher_tags" (name, embedding) VALUES (%s, %s) ON CONFLICT(name) DO NOTHING'
                    args_list = [(name, str(embedding)) for name, embedding in zip(dad_tags, dad_tags_embeddings)]
                    cursor.executemany(sql, args_list)
                    print(f"{cursor.rowcount} novas DAD tags foram inseridas.")
        except psycopg.Error as e:
            print(f'Erro de conexão ou inserção: {e}')
    
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
        except psycopg.Error as e:
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
        graph_builder.add_node("classify_tags", self.classify_tags_for_dad_tags)
        graph_builder.add_node("insert_dad_tags", self.insert_dad_tags)
        graph_builder.add_node("generate_embeddings", self.generate_embeddings_for_groups)
        graph_builder.add_node("remove_and_create_tags", self.remove_and_create_tags)

        graph_builder.set_entry_point("get_tags")
        graph_builder.add_edge("get_tags", "clean_tags")
        graph_builder.add_edge("clean_tags", "define_group_names")
        graph_builder.add_edge("define_group_names", "classify_tags")
        graph_builder.add_edge("classify_tags", "insert_dad_tags")
        graph_builder.add_edge("classify_tags", "generate_embeddings")
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