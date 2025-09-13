import os
import time
from openai import OpenAI
from dotenv import load_dotenv

def criar_client():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client

# --- Gera tags de um chunk ---
def generate_tags_from_chunk(chunk_text, column_name):
    prompt = f"""
    Gere entre 1 e 3 tags curtas, relevantes e SIGNIFICATIVAS para o seguinte texto da coluna '{column_name}':

    {chunk_text}

    Regras importantes:
    - As tags devem ser SEMÂNTICAS: representar temas, áreas de estudo, tecnologias, métodos ou conceitos.
    - Pode incluir tanto termos específicos quanto termos mais amplos relacionados.
      Exemplos:
        - "coronavírus" → também pode gerar "biologia", "saúde pública".
        - "ensino inovador" → também pode gerar "educação", "inovação".
        - "tomada de decisões" → também pode gerar "negócios", "administração".
    - NÃO use:
      - nomes de empresas (ex: "speed informática ltda")
      - siglas soltas ou códigos (ex: "RDC 350/2020", "XXII", "TC 504 Gertec")
      - palavras vagas ou genéricas sem semântica clara (ex: "prevalência", "sistema", "marcadores")
      - termos soltos sem contexto (ex: "e-lixo")
    - Sempre use português e, quando possível, no singular.
    - Responda apenas com as tags separadas por vírgula, sem frases extras.
    """
    response = criar_client().chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return list(set([t.strip() for t in response.choices[0].message.content.strip().split(",")]))

# --- Gerar tags a partir de todas as chunks de uma coluna ---
def generate_tags_from_column(chunks, column_name):
    tags = set()
    for chunk in chunks:
        try:
            tags.update(generate_tags_from_chunk(chunk, column_name))
        except Exception as e:
            print(f"Erro ao gerar tags para chunk da coluna {column_name}: {e}")
    return list(tags)

# --- Função por pesquisador ---
def generate_tags_for_researcher(chunks_dict):
    tags = set()
    for column_name, chunks in chunks_dict.items():
        if column_name == 'metadata':
            continue
        tempo_inicio = time.time()
        tags.update(generate_tags_from_column(chunks, column_name))
        tempo_fim = time.time()
        print(f"Duração da geração de tags da coluna '{column_name}': {tempo_fim-tempo_inicio:.2f} segundos")
        print(f"Gerou tags da coluna: {column_name}")
    return list(tags)

# --- Função principal ----
def generate_tags_pipeline(pesquisadores):
    tags_por_pesquisador = {}
    i = 1
    for pesquisador, chunks_dict in pesquisadores.items():
        if i < 2:
            print(f"Gerando tags para {pesquisador}...")
            tags_por_pesquisador[pesquisador] = generate_tags_for_researcher(chunks_dict)
            i += 1
        break

    tags_globais = set()
    for tags in tags_por_pesquisador.values():
        tags_globais.update(tags)

    return tags_por_pesquisador, list(tags_globais)

# ---- Vizualização ----
def visualize_tags(tags_por_pesquisador, tags_globais):
    print("Tags por pesquisador:")
    for p, tags in tags_por_pesquisador.items():
        print(f"{p}: {tags}")

    print("\nTags globais:")
    print(tags_globais)

