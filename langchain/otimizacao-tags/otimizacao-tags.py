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
    
    def set_tags(self, tags: List[Dict[str, Any]]):
        """Define as tags do log, tratando-as como grupos para salvamento."""
        self.groups = tags
        return self

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
    removed_tags: List[str] = Field(description="Uma lista com o NOME de cada tag removida do grupo por não pertencer a ele")

class DadTagClassification(BaseModel):
    """Estrutura para a classificação de um grupo de tags em dad_tags."""
    dad_tags: List[str] = Field(description="Uma lista de dad_tags correspondentes para o grupo de tags.")

class State(TypedDict):
    """Estado passado para cada etapa do Grafo."""

    all_tags: List[Dict[str, Any]]
    all_raw_tags: List[Dict[str, Any]]
    tag_groups: List[Dict[str, Any]]
    tags_not_in_groups: List[Dict[str, Any]]
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

        return {"all_raw_tags": all_tags}

    def clean_and_group_tags(self, state: State) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa tags similares"""

        print("\n--- AGRUPAMENTO POR SIMILARIDADE DE TAGS ---")

        SIMILARITY_THRESHOLD = float(os.environ["SIMILARITY_THRESHOLD"]);

        all_tags = state["all_raw_tags"]
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

        # Coletar as tags que não foram agrupadas (isoladas)
        grouped_tag_ids = set()
        for group in groups:
            for tag in group["tags"]:
                grouped_tag_ids.add(tag["id"])

        tags_not_in_groups = []
        for tag in all_tags:
            if tag["id"] not in grouped_tag_ids:
                tags_not_in_groups.append(tag)
        
        self.logger.create_new_log(groups=groups).save_log()

        return {"tag_groups": groups, "tags_not_in_groups": tags_not_in_groups}

    def define_group_names(self, state: State):
        """Remove tags estrangeiras e escolhe um nome para cada grupo de tags."""

        print("\n--- LIMPEZA DE GRUPOS DE TAGS E NOMEAÇÃO  ---")

        groups = state["tag_groups"]

        print(f'Total de {len(groups)} grupos de tags a serem limpados e nomeados!')

        prompts = []
        for group in groups:
            # Otimização: Envia apenas os nomes das tags para economizar tokens.
            # O modelo retornará os nomes das tags a serem removidas.
            tag_names = [tag["name"] for tag in group["tags"]]
            prompt = f"""
                Você é um taxonomista acadêmico. Sua tarefa é analisar o seguinte grupo de tags de pesquisa, remover as que não pertencem e criar um nome canônico para o grupo.
                Grupo de tags (apenas nomes): {tag_names}

                O nome canônico do grupo deve ser:
                - Um nome de campo de estudo formal e específico (ex: "Engenharia de Software", não "Software").
                - Concisa, com no máximo 3 palavras obrigatoriamente.
                - Generalista o suficiente para abranger os conceitos centrais.
                - Representativa de todas as tags do grupo.

                Instruções:
                1.  Identifique o tema central do grupo.
                2.  Crie um `group_name` que siga as regras acima.
                3.  Liste em `removed_tags` os NOMES de quaisquer tags que sejam outliers e não se encaixem no tema central do grupo. Se nenhuma tag precisar ser removida, retorne uma lista vazia.

                Sua resposta DEVE ser um objeto JSON formatado.
            """
            prompts.append(prompt)

        # O método .batch() executa todas as chamadas de API em paralelo.
        # Usamos um try-except para lidar com grupos muito grandes que podem exceder o limite de tokens.
        try:
            # Tentativa inicial com um limite de tokens razoável para eficiência.
            print("Executando nomeação em lote com limite de 4096 tokens...")
            responses = self.structured_llm.with_config({"max_concurrency": 5}).batch(prompts, max_tokens=4096)
        except Exception as e:
            # Se a tentativa inicial falhar (provavelmente por limite de tokens),
            # tentamos novamente com um limite muito maior como fallback.
            print(f"Falha na primeira tentativa ({e}). Tentando novamente com limite de 8192 tokens...")
            responses = self.structured_llm.with_config({"max_concurrency": 5}).batch(prompts, max_tokens=8192)

        for tag_group, response in zip(groups, responses):
            # Mapeia os nomes das tags removidas de volta para seus IDs.
            tag_name_to_id_map = {tag["name"]: tag["id"] for tag in tag_group["tags"]}
            removed_ids = {tag_name_to_id_map[name] for name in response.removed_tags if name in tag_name_to_id_map}

            tag_group["name"] = response.group_name
            tag_group["tags"] = [tag for tag in tag_group["tags"] if tag["id"] not in removed_ids]
            print(f'Total de {len(tag_group["tags"])} tags unificadas na Tag \'{response.group_name}\'!')
        
        print("Limpeza e nomeação bem sucedidas!")

        self.logger.currentLog.set_groups(groups).save_log()

        return {"tag_groups": groups, "tags_not_in_groups": state["tags_not_in_groups"]}
        
    def classify_tags_for_dad_tags(self, state: State):
        """Classifica as tags em DAD ou não DAD"""
        print("\n--- CLASSIFICAÇÃO DE TAGS EM DAD OU NÃO DAD  ---")
        
        groups = state["tag_groups"][:] # Copia a lista para evitar modificar a original diretamente no loop
        tags_not_in_groups = state["tags_not_in_groups"][:]
        
        # Garante que todas as tags (agrupadas, isoladas e pais) tenham uma estrutura consistente.
        all_tags = groups + [
            {"name": tag["name"], "embedding": "", "created": False, "tags": [tag]} 
            for tag in tags_not_in_groups
        ]

        all_dad_tags = set()

        print(f'Total de {len(all_tags)} tags a serem classificados!')
        
        for tag in all_tags:
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

            for dad_tag in response.dad_tags:
                all_dad_tags.add(dad_tag)

            # Cria um dicionário com chaves dad_tag1, dad_tag2, etc.
            dad_tag_dict = {f"dad_tag{i+1}": tag for i, tag in enumerate(response.dad_tags)}
            tag["dad_tags"] = dad_tag_dict
            # Cada tag tem uma chave "dad_tags" que é um dicionário com as dad_tags classificadas para ela
            print(f'A tag \'{tag_name}\' foi classificada em: {dad_tag_dict if dad_tag_dict else "Nenhuma"}')

        self.logger.currentLog.set_groups(groups).save_log()

        # Adiciona as dad_tags recém-descobertas à lista de todas as tags
        # para que elas também possam ter seus embeddings gerados e serem inseridas no banco.
        for dad_tag_name in all_dad_tags:
            # Adiciona como se fosse um novo grupo/tag isolada, mantendo a estrutura.
            all_tags.append(
                {"name": dad_tag_name, "embedding": "", "created": False, "tags": []}
            )

        print(f"\nTotal de {len(all_dad_tags)} dad_tags únicas encontradas.")
        return {"all_tags": all_tags, "unique_dad_tags": list(all_dad_tags)}

    def generate_embeddings_for_tags(self, state: State):
        """Gera os embeddings para todas as tags"""

        print("\n--- GERAÇÃO DE EMBEDDINGS DAS TAGS UNIFICADAS  ---")
        
        tags = state["all_tags"]

        print(f'Total de {len(tags)} tags a gerar embeddings!')

        tag_names = [tag["name"] for tag in tags]
        tag_embeddings = self.embeddings.embed_documents(tag_names)

        for i, tag in enumerate(tags):
            tag['embedding'] = str(tag_embeddings[i])
        
        print(f'Geração de embeddings finalizada com sucesso!')

        self.logger.currentLog.set_tags(tags).save_log()

        return {"all_tags": tags}

    def remove_and_create_tags(self, state: State):
        """Remove as tags dos grupos, substituindo-as pela tag unificada de seu grupo, junto a tags dad_tags e tags isoladas."""
        print("\n--- INSERÇÃO DE NOVOS GRUPOS, REMOÇÃO DE TAGS REDUNDANTED, E TAGS ISOLADAS E DAD TAGS ---")

        print("Conectando com banco de dados...")
        tags = state["all_tags"]
        try:
            with psycopg.connect(self.db_url) as connection:
                print("Conexão bem sucedida!")
                with connection.cursor() as cursor:
                    for tag in tags:
                        print(f'Inserindo e removendo tags do grupo \'{tag["name"]}\'')
                        tag_ids = tuple([tag["id"] for tag in tag["tags"]])
                        cursor.execute('INSERT INTO "public"."researcher_tags" (name, embedding) VALUES (%s, %s)', (tag["name"], tag["embedding"]))
                        tag["created"] = True
                        if tag_ids:
                            placeholders = ', '.join(['%s'] * len(tag_ids))
                            cursor.execute(f'DELETE FROM "public"."researcher_tags" WHERE id IN ({placeholders})', tag_ids)
                            for sub_tag in tag["tags"]:
                                sub_tag["removed"] = True
        except psycopg.Error as e:
            print(f'Erro de conexão: {e}')
            self.logger.currentLog.set_tags(tags).save_log()

        self.logger.currentLog.set_tags(tags).save_log()
        print("Inserção realizada com sucesso!")

    def create_graph(self):
        """Cria o grafo LangGraph com o fluxo de otimização."""

        graph_builder = StateGraph(State)

        graph_builder.add_node("get_tags", self.get_all_tags_from_db)
        graph_builder.add_node("clean_tags", self.clean_and_group_tags)
        graph_builder.add_node("define_group_names", self.define_group_names)
        graph_builder.add_node("classify_tags", self.classify_tags_for_dad_tags)
        graph_builder.add_node("generate_embeddings", self.generate_embeddings_for_tags)
        graph_builder.add_node("remove_and_create_tags", self.remove_and_create_tags)

        graph_builder.set_entry_point("get_tags")
        graph_builder.add_edge("get_tags", "clean_tags")
        graph_builder.add_edge("clean_tags", "define_group_names")
        graph_builder.add_edge("define_group_names", "classify_tags")
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