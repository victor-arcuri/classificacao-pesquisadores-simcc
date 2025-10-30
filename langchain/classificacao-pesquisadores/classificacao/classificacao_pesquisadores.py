from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import time
from typing import List, Tuple
from openai import RateLimitError

BATCH_SIZE = 10 # Define o tamanho do lote para as chamadas à API

class TagList(BaseModel):
    """Um modelo Pydantic para validar a saída da LLM."""
    tags: List[str] = Field(description="Lista de 1 a 3 NOMES de tags mais relevantes para a coluna fornecida a partir do banco de tags")

def criar_client() -> ChatOpenAI:
    load_dotenv()
    client = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    return client

def classificar_coluna(tags: List[Tuple[str, str]], client: ChatOpenAI, column_name: str, chunks: list[str]) -> List[Tuple[str, str]]:
    """
    Classifica uma lista de chunks de texto para uma coluna específica usando chamadas em lote (batch).
    """
    if not chunks:
        return []

    # Mapeia nomes de tags para as tuplas (id, nome) para fácil recuperação
    tag_map = {}
    for tag_tuple in tags:
        name = tag_tuple[1]
        tag_map[name] = tag_tuple
    tag_names = list(tag_map.keys())

    # Criação do prompt e chain
    classification_prompt = ChatPromptTemplate.from_template("""
    Você é um especialista em classificação. Sua tarefa é analisar um trecho de texto e associá-lo a até 3 tags de um banco de tags pré-definido.

    Texto da coluna '{column_name}':
    {chunk_text}

    Banco de Tags:
    {tag_names}

    REGRAS:
        1. Use SOMENTE tags que existem no "Banco de Tags".
        2. As tags devem ser estritamente relevantes ao conteúdo do texto.
        3. Se nenhuma tag for relevante, retorne uma lista vazia.
        4. Sua resposta DEVE ser um objeto JSON, contendo uma única chave "tags" com uma lista de nomes de tags. Não inclua nenhuma explicação ou texto adicional.

    Exemplo de resposta: {{"tags": ["Nome da Tag 1", "Nome da Tag 2"]}}
    """)

    parser = JsonOutputParser(pydantic_object=TagList)
    classification_chain = classification_prompt | client | parser

    # Montar os prompts com as informações
    prompts = [{
        "column_name": column_name,
        "chunk_text": chunk,
        "tag_names": ", ".join(tag_names)
    } for chunk in chunks]

    all_tags_for_column = set()

    # Mudança para execução em lote
    for i in range(0, len(prompts), BATCH_SIZE):
        batch = prompts[i:i + BATCH_SIZE]
        
        # Lógica de tentativa e espera (retry) para lidar com Rate Limit
        max_retries = 3
        for attempt in range(max_retries):
            try:
                responses = classification_chain.batch(batch, config={"max_concurrency": 3}) # Concorrência reduzida para 3
                for response in responses:
                    ai_tag_names = response.get("tags", [])
                    result_tuples = [tag_map[name] for name in ai_tag_names if name in tag_map]
                    all_tags_for_column.update(result_tuples)
                break # Se bem-sucedido, sai do loop de tentativas
            except RateLimitError as e:
                wait_time = 2 ** attempt # Espera exponencial (1, 2, 4 segundos...)
                print(f"Rate limit atingido na coluna '{column_name}'. Tentando novamente em {wait_time}s... (Tentativa {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Erro inesperado ao classificar lote para a coluna '{column_name}': {e}")
                break # Sai do loop de tentativas em caso de outros erros

    return list(all_tags_for_column)

def classificar_pesquisador(tags: list[str], client: ChatOpenAI, researcher_id: str, chunks_dict: dict) -> List[Tuple[str, str]]:
    all_tags_for_researcher = set()
    for column_name, chunks in chunks_dict.items():
        if column_name == "metadata":
            continue
        tempo_inicio = time.time()
        all_tags_for_column = classificar_coluna(tags, client, column_name, chunks)
        all_tags_for_researcher.update(all_tags_for_column)
        tempo_fim = time.time()
        print(f"Duração da coluna '{column_name}': {tempo_fim - tempo_inicio:.2f} seg")
        
    return list(all_tags_for_researcher)

def classificacao_pipeline(tags: list[str], client: ChatOpenAI, researchers: dict):
    tags_por_pesquisador = {}
    limite_de_pesquisadores = 0
    for researcher_id, chunks_dict in researchers.items():
        if (limite_de_pesquisadores >= 10):
            break
        print(f"\nClassificando o pesquisador de id '{researcher_id}'...\n")
        tags_por_pesquisador[researcher_id] = classificar_pesquisador(tags, client, researcher_id, chunks_dict)
        print("\nTags definidas para o pesquisador:\n")
        for tag in tags_por_pesquisador[researcher_id]:
            print(tag)
        limite_de_pesquisadores+=1
        
    return tags_por_pesquisador