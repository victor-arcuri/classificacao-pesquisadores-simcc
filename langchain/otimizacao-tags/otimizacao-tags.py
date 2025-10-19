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
- inserir todas as tags (sem considerar hierarquia nenhuma também) depois de otimizado para todos os pesquisadores - OK
- incluir tags que não foram agrupadas (isoladas) na tabela de tags - OK
- modificar o schema para nova tabela de hierarquia e criar nova migration
- inserir hierarquia de tags - OK
- criar condição para tags pais e filhas iguais
- criar dicionários com chaves (tags_pais) com valores (tags_filhas) para facilitar inserção no banco - OK
- biblioteca logging para logs mais robustos 
'''

# Lista "Pura" de Nível 1 (Disciplinas-Raiz)

DAD_TAGS = [
    # Ciências Humanas e Sociais
    "Filosofia", 
    "Sociologia", 
    "Antropologia", 
    "Psicologia", 
    "História", 
    "Geografia",
    "Educação", 
    "Ciência Política", 
    "Direito",
    "Políticas Públicas",
    "Economia",
    "Administração", 
    "Relações Internacionais",

    # Ciências Exatas e Naturais
    "Matemática",
    "Física", 
    "Química", 
    "Biologia", 
    "Geologia", 
    "Ecologia", 
    "Sustentabilidade", 
    
    # Saúde
    "Saúde",
    "Medicina", 
    "Enfermagem",
    "Nutrição",

    # Tecnologia e Engenharia
    "Computação", 
    "Engenharia", 
    "Tecnologia",

    # Artes e Comunicação
    "Arte",
    "Cultura", 
    "Design", 
    "Moda",
    "Arquitetura",
    "Literatura",
    "Comunicação", 
    "Linguística"
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
                "embedding": group.get("embedding", ""),
                "created": group.get("created", False),
            }
            if "tags" in group:
                formatted_group["tags"] = [
                        {
                            "id": str(tag["id"]),
                            "removed": tag.get("removed", False),
                            "name": tag["name"]
                        } for tag in group["tags"]
                    ]
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
    tag_name_to_id_map: Dict[str, str]

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
        
        # Usando Agglomerative Clustering para um agrupamento mais robusto.
        from sklearn.cluster import AgglomerativeClustering

        # Garante que os embeddings sejam um array 2D
        embeddings = np.array([tag['embedding'] for tag in all_tags])

        # Configura o clustering. 'distance_threshold' é o inverso da similaridade.
        # 'n_clusters=None' garante que o threshold seja o critério de parada.
        # 'linkage='average'' usa a média das distâncias, similar ao nosso centroide.
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=1 - SIMILARITY_THRESHOLD,
            metric='cosine',
            linkage='average'
        ).fit(embeddings)

        # 'clustering.labels_' contém o ID do cluster para cada tag.
        num_clusters = clustering.n_clusters_
        cluster_labels = clustering.labels_

        # Organiza as tags em seus respectivos clusters.
        clusters = {i: [] for i in range(num_clusters)}
        for i, tag in enumerate(all_tags):
            clusters[cluster_labels[i]].append(tag)

        # Converte os clusters em grupos, ignorando "grupos" de uma única tag.
        for cluster_id, tags_in_cluster in clusters.items():
            if len(tags_in_cluster) > 1:
                for tag in tags_in_cluster:
                    tag["removed"] = False
                groups.append({
                    "name": "",
                    "embedding": "",
                    "created": False,
                    "tags": tags_in_cluster
                })
        
        print(f'Agrupamento bem sucedido!')
        print(f'Formados {len(groups)} grupos de tags!')

        # Salva no log apenas os grupos reais que foram formados.
        # As tags isoladas serão tratadas nas etapas seguintes.
        self.logger.create_new_log(groups=groups).save_log()

        # Passa adiante a lista original de tags para que as isoladas possam ser identificadas depois.
        return {"tag_groups": groups, "all_raw_tags": all_tags}

    def define_group_names(self, state: State):
        """Remove tags estrangeiras e escolhe um nome para cada grupo de tags."""

        print("\n--- LIMPEZA DE GRUPOS DE TAGS E NOMEAÇÃO  ---")

        groups = state["tag_groups"]
        
        if not groups:
            print("Nenhum grupo para nomear. Pulando etapa.")
            return {"tag_groups": [], "tags_not_in_groups": []}
            
        print(f'Total de {len(groups)} grupos de tags a serem limpados e nomeados!')

        BATCH_SIZE = 10 # Define o número de grupos a serem processados por lote

        prompts = []
        for group in groups:
            # Otimização: Envia apenas os nomes das tags para economizar tokens.
            # O modelo retornará os nomes das tags a serem removidas.
            tag_names = [tag["name"] for tag in group["tags"]]
            prompt = f"""
                Você é um taxonomista acadêmico sênior. Sua tarefa é analisar o seguinte grupo de tags de pesquisa e criar um nome canônico e abrangente para ele. O agrupamento já foi feito por similaridade semântica, então sua função é encontrar o melhor nome que represente o conjunto.
                Grupo de tags: {tag_names}

                O nome canônico do grupo deve ser OBRIGATORIAMENTE:
                - Um nome de campo de estudo formal e específico (ex: "Engenharia de Software", não "Software").
                - Concisa, com NO MÁXIMO 4 palavras.
                - Generalista o suficiente para englobar a maioria dos conceitos no grupo.
                - Não misture assuntos (ex: "Política e Cidadania" é inválido, ou só "Política" ou "Cidadania").

                Instruções:
                1.  Identifique o tema central ou a interseção dos temas no grupo e crie um `group_name` que o represente.
                2.  Seja tolerante com a diversidade de tags. Apenas liste em `removed_tags` os NOMES de tags que são EXTREMAMENTE discrepantes e claramente um erro de agrupamento (ex: 'Culinária Francesa' em um grupo sobre 'Inteligência Artificial').
                3.  Priorize manter as tags no grupo. Se uma tag for apenas um pouco diferente, mantenha-a. Remova no máximo 10% das tags. Se nenhuma tag precisar ser removida, retorne uma lista vazia.

                Sua resposta DEVE ser um objeto JSON formatado.

                **Exemplo de Resposta:**
                - **Exemplo 1 (Grupo Coeso):**
                  - Tags de Entrada: `['Desenvolvimento de Software', 'Engenharia de Software Ágil', 'Testes de Software', 'Arquitetura de Microserviços']`
                  - Resposta Esperada: `{{ "group_name": "Engenharia de Software", "removed_tags": [] }}`
                - **Exemplo 2 (Grupo Diverso mas Coerente):**
                  - Tags de Entrada: `['Educação a Distância', 'Desenvolvimento de Software', 'Informática na Educação', 'Gestão de Projetos de TI']`
                  - Resposta Esperada: `{{ "group_name": "Tecnologia na Educação e Gestão", "removed_tags": [] }}`
            """
            prompts.append(prompt)

        responses = []
        # Processa os prompts em lotes menores para evitar erros de limite de token.
        for i in range(0, len(prompts), BATCH_SIZE):
            batch_prompts = prompts[i:i + BATCH_SIZE]
            print(f"Processando lote de nomeação de grupos {i//BATCH_SIZE + 1}/{(len(prompts) + BATCH_SIZE - 1)//BATCH_SIZE}...")
            try:
                batch_responses = self.structured_llm.with_config({"max_concurrency": 5}).batch(batch_prompts, max_tokens=4096)
                responses.extend(batch_responses)
            except Exception as e:
                print(f"  -> Erro no lote: {e}. As tags deste lote não serão nomeadas.")
                # Adiciona respostas vazias para manter o alinhamento com os grupos
                responses.extend([RefinedGroup(group_name="ERRO_NO_PROCESSAMENTO", removed_tags=[]) for _ in batch_prompts])
        
        removed_tags_globally = []
        
        for tag_group, response in zip(groups, responses):
            if response.group_name == "ERRO_NO_PROCESSAMENTO":
                # Pula grupos que falharam para evitar quebrar o fluxo
                removed_tags_globally.extend(tag_group["tags"])
                tag_group["tags"] = [] 
                continue

            # Mapeia os nomes das tags removidas de volta para seus IDs.
            tag_name_to_id_map = {tag["name"]: tag["id"] for tag in tag_group["tags"]}
            removed_ids = {tag_name_to_id_map[name] for name in response.removed_tags if name in tag_name_to_id_map}

            # Captura as tags que foram removidas para tratá-las como isoladas
            removed_tags_objects = [tag for tag in tag_group["tags"] if tag["id"] in removed_ids]
            for removed_tag in removed_tags_objects:
                print(f'  -> Tag removida do grupo: {removed_tag["name"]}')

            if removed_tags_objects:
                print(f'  -> {len(removed_tags_objects)} tags foram removidas do grupo e serão tratadas como isoladas.')
                removed_tags_globally.extend(removed_tags_objects)

            # Atualiza o grupo com o novo nome e a lista de tags limpa
            tag_group["name"] = response.group_name
            tag_group["tags"] = [tag for tag in tag_group["tags"] if tag["id"] not in removed_ids]
            if tag_group["tags"]:
                print(f'Total de {len(tag_group["tags"])} tags unificadas na Tag \'{response.group_name}\'!')
        
        # Filtra grupos que podem ter ficado vazios após a remoção ou erro
        groups = [g for g in groups if g["tags"]]
        
        print("Limpeza e nomeação bem sucedidas!")

        self.logger.currentLog.set_groups(groups).save_log() # O log reflete os grupos após a limpeza

        return {"tag_groups": groups, "tags_not_in_groups": removed_tags_globally}
        
    def classify_tags_for_dad_tags(self, state: State):
        """Classifica as tags em DAD ou não DAD"""
        print("\n--- CLASSIFICAÇÃO DE TAGS EM DAD OU NÃO DAD  ---")
        
        groups = state["tag_groups"][:] # Copia a lista para evitar modificar a original diretamente no loop
        all_raw_tags = state["all_raw_tags"]

        # Identifica todas as tags que estão dentro de grupos já processados.
        grouped_tag_ids = set()
        for group in groups:
            for tag in group["tags"]:
                grouped_tag_ids.add(tag["id"])

        # As tags isoladas são todas as tags originais que NÃO estão nos grupos finais.
        isolated_tags = [
            tag for tag in all_raw_tags if tag["id"] not in grouped_tag_ids
        ]

        # Estrutura as tags isoladas como "grupos de um" para processamento unificado.
        isolated_tags_as_groups = [{
            "name": tag["name"], "embedding": "", "created": False, "tags": [tag]
        } for tag in isolated_tags]

        # A lista final de trabalho contém os grupos reais + as tags isoladas.
        all_tags = groups + isolated_tags_as_groups
        all_dad_tags = set()

        print(f'Total de {len(all_tags)} tags a serem classificados!')
        
        for tag in all_tags:
            tag_name = tag["name"]
            prompt = f"""
                Você é um taxonomista sênior e especialista em categorização de áreas de pesquisa. Sua tarefa é identificar a **disciplina-raiz** da tag de pesquisa '{tag_name}' dentre essas tags pré-definidas: {DAD_TAGS}.

                **Instruções Extremamente Rigorosas:**
                1.  **Identifique a Origem:** Sua principal tarefa é encontrar a **área-mãe** mais fundamental da qual a tag deriva. Se a tag é uma aplicação de uma ciência, priorize a ciência, não a aplicação.
                2.  **Hierarquia Estrita:** Pense como um bibliotecário: em qual prateleira principal este livro pertence? A tag '{tag_name}' é um subcampo direto de qual campo da lista?
                3.  **Seja Minimalista:** Retorne no máximo 2 campos. O primeiro deve ser a área-mãe. O segundo, opcional, só deve ser usado se a tag for intrinsecamente uma fusão de duas áreas fundamentais.
                
                **Exemplos de Classificação Correta:**
                - Para a tag 'Teoria dos Jogos', a resposta DEVE ser apenas ['Matemática'], pois é sua disciplina de origem, mesmo que seja aplicada em 'Economia' e 'Ciência Política'.
                - Para a tag 'Energia Renovável', a resposta DEVE ser ['Sustentabilidade', 'Engenharia'], pois combina conceitos de ambas as áreas de forma central. NÃO inclua 'Tecnologia' ou 'Ecologia' como campos separados.
                - Para a tag 'Saúde Pública', a resposta DEVE ser ['Saúde', 'Políticas Públicas'], pois é a interseção direta desses dois campos.
                - Para a tag 'Modelagem Matemática', a resposta DEVE ser ['Matemática']. 'Ciência de Dados' é uma aplicação, não a origem.
                
                Responda APENAS com os campos que estão **EXATAMENTE** como na lista fornecida. Não invente, modifique ou adicione nenhuma outra tag.
            """

            response = self.dad_tag_classifier_llm.invoke(prompt)

            # Filtra a resposta para garantir que apenas tags da lista DAD_TAGS sejam usadas.
            valid_dad_tags = [tag for tag in response.dad_tags if tag in DAD_TAGS]

            for dad_tag in valid_dad_tags:
                all_dad_tags.add(dad_tag)

            # Cria um dicionário com chaves dad_tag1, dad_tag2, etc.
            dad_tag_dict = {f"dad_tag{i+1}": tag for i, tag in enumerate(valid_dad_tags)}
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
        all_tags = state["all_tags"]
        tag_name_to_id_map = {}
        try:
            with psycopg.connect(self.db_url) as connection:
                print("Conexão bem sucedida!")
                # Processa cada tag/grupo em sua própria transação para maior resiliência.
                for tag in all_tags:
                    try:
                        # Inicia uma transação para esta unidade de trabalho.
                        with connection.transaction():
                            with connection.cursor() as cursor:
                                print(f'Processando e inserindo a tag: \'{tag["name"]}\'')
                                # Insere a nova tag e retorna seu ID
                                cursor.execute('INSERT INTO "public"."researcher_tags" (name, embedding) VALUES (%s, %s) RETURNING id', (tag["name"], tag["embedding"]))
                                tag["created"] = True
                                new_tag_id = cursor.fetchone()[0]
                                tag_name_to_id_map[tag["name"]] = new_tag_id
                                
                                # Se a tag for um grupo, remove as tags antigas que o compunham.
                                tag_ids_to_remove = tuple([t.get("id") for t in tag.get("tags", []) if t.get("id")])
                                if tag_ids_to_remove:
                                    placeholders = ', '.join(['%s'] * len(tag_ids_to_remove))
                                    cursor.execute(f'DELETE FROM "public"."researcher_tags" WHERE id IN ({placeholders})', tag_ids_to_remove)
                                    print(f'  -> Removidas {len(tag_ids_to_remove)} tags antigas.')
                                    for sub_tag in tag["tags"]:
                                        sub_tag["removed"] = True
                    except psycopg.Error as e:
                        print(f'Erro ao processar a tag \'{tag["name"]}\': {e}. Pulando para a próxima.')
                        tag["created"] = False # Marca como falha no log
                        # A transação para este item será revertida automaticamente.

        except psycopg.Error as e:
            print(f'Erro de conexão: {e}')
            self.logger.currentLog.set_tags(all_tags).save_log()

        self.logger.currentLog.set_tags(all_tags).save_log()
        print("Processamento de inserção e remoção no banco de dados finalizado!")
        return {"all_tags": all_tags, "tag_name_to_id_map": tag_name_to_id_map}

    def insert_hierarchy(self, state: State):
        """Insere as relações de hierarquia na nova tabela."""
        print("\n--- INSERÇÃO DA HIERARQUIA DE TAGS ---")
        
        all_tags = state["all_tags"]
        tag_name_to_id_map = state.get("tag_name_to_id_map", {})
        
        if not tag_name_to_id_map:
            print("Nenhum mapa de IDs de tag encontrado. Pulando inserção de hierarquia.")
            return

        hierarchy_relations = []
        for tag in all_tags:
            if "dad_tags" in tag and tag.get("name") in tag_name_to_id_map:
                child_id = tag_name_to_id_map[tag["name"]]
                for parent_name in tag["dad_tags"].values():
                    if parent_name in tag_name_to_id_map:
                        parent_id = tag_name_to_id_map[parent_name]
                        if child_id != parent_id:
                            hierarchy_relations.append((child_id, parent_id))

        if not hierarchy_relations:
            print("Nenhuma relação de hierarquia para inserir.")
            return

        print(f"Inserindo {len(hierarchy_relations)} relações de hierarquia...")
        with psycopg.connect(self.db_url) as connection:
            with connection.cursor() as cursor:
                # Usa ON CONFLICT DO NOTHING para evitar erros de chave duplicada
                cursor.executemany('INSERT INTO "public"."tags_hierarchy" (tag_id, parent_tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', hierarchy_relations)
        print("Inserção de hierarquia finalizada com sucesso!")

    def create_graph(self):
        """Cria o grafo LangGraph com o fluxo de otimização."""

        graph_builder = StateGraph(State)

        graph_builder.add_node("get_tags", self.get_all_tags_from_db)
        graph_builder.add_node("clean_tags", self.clean_and_group_tags)
        graph_builder.add_node("define_group_names", self.define_group_names)
        graph_builder.add_node("classify_tags", self.classify_tags_for_dad_tags)
        graph_builder.add_node("generate_embeddings", self.generate_embeddings_for_tags)
        graph_builder.add_node("remove_and_create_tags", self.remove_and_create_tags)
        graph_builder.add_node("insert_hierarchy", self.insert_hierarchy)

        graph_builder.set_entry_point("get_tags")
        graph_builder.add_edge("get_tags", "clean_tags")
        graph_builder.add_edge("clean_tags", "define_group_names")
        graph_builder.add_edge("define_group_names", "classify_tags")
        graph_builder.add_edge("classify_tags", "generate_embeddings")
        graph_builder.add_edge("generate_embeddings", "remove_and_create_tags")
        graph_builder.add_edge("remove_and_create_tags", "insert_hierarchy")
        graph_builder.add_edge("insert_hierarchy", END)

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