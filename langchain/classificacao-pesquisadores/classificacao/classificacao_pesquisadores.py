from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import json
from typing import List, Tuple

def criar_client() -> OpenAI:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client

def classificar_chunk(
    tags: List[Tuple[str, str]],
    client: OpenAI,
    chunk_text: str,
    column_name: str
) -> List[Tuple[str, str]]:

    tag_names = []
    tag_map = {}
    for tag_tuple in tags:
        name = tag_tuple[1]
        tag_names.append(name)
        tag_map[name] = tag_tuple 

    prompt = f"""
    Classifique o texto da coluna '{column_name}' com um número entre 0 e 3 tags mais relevantes e significativas do banco de tags fornecido.

    Coluna '{column_name}':

    {chunk_text}

    Banco de Tags:

    {tag_names}

    REGRAS:
        1. Classifique apenas com as tags que existirem no banco de tags
        2. Apenas classifique com tags que façam sentido com o conteúdo da coluna
        3. Caso não hajam tags coerentes, retorne uma lista vazia
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "tag_list",
                "schema": {
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de 1 a 3 NOMES de tags mais relevantes para a coluna fornecida a partir do banco de tags"
                        }
                    },
                    "required": ["tags"],
                    "additionalProperties": False
                },
            },
        },
    )

    json_string = response.choices[0].message.content
    parsed_json = json.loads(json_string)

    ai_tag_names = parsed_json["tags"]
    
    result_tuples = [tag_map[name] for name in ai_tag_names if name in tag_map]

    return result_tuples

def classificar_coluna(tags: list[str], client: OpenAI, column_name: str, chunks: list[str]) -> List[Tuple[str, str]]:
    all_tags_for_column = set()
    for chunk in chunks:
        try:
            tags_for_chunk = classificar_chunk(tags, client, chunk, column_name)
            all_tags_for_column.update(tags_for_chunk)
        except Exception as e:
            print(f"Erro ao classificar tags para chunk da coluna '{column_name}': {e}")
    return list(all_tags_for_column);        

def classificar_pesquisador(tags: list[str], client: OpenAI, researcher_id: str, chunks_dict: dict) -> List[Tuple[str, str]]:
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

def classificacao_pipeline(tags: list[str], client: OpenAI, researchers: dict):
    tags_por_pesquisador = {}
    limite_de_pesquisadores = 0
    for researcher_id, chunks_dict in researchers.items():
        if (limite_de_pesquisadores >= 2):
            break
        print(f"\nClassificando o pesquisador de id '{researcher_id}'...\n")
        tags_por_pesquisador[researcher_id] = classificar_pesquisador(tags, client, researcher_id, chunks_dict)
        print("\nTags definidas para o pesquisador:\n")
        for tag in tags_por_pesquisador[researcher_id]:
            print(tag)
        limite_de_pesquisadores+=1
        
    return tags_por_pesquisador