import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Domínios temáticos disponíveis
DOMINIOS = [
    "Ciência da Computação e Tecnologia",
    "Educação e Ensino",
    "Saúde e Medicina",
    "Biologia e Ciências da Vida",
    "Química e Farmacologia",
    "Engenharia e Indústria",
    "Energia e Sustentabilidade",
    "Matemática e Estatística",
    "Física",
    "Ciências Sociais e Humanas",
    "Economia e Negócios",
    "Direito e Políticas Públicas",
    "Artes e Cultura",
    "Ciência de Dados e Inteligência Artificial",
    "Meio Ambiente e Ecologia",
]

# Criar cliente OpenAI
def criar_client() -> OpenAI:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client

"""
    Gere entre 1 e 3 tags curtas, relevantes e SIGNIFICATIVAS para o seguinte texto da coluna '{column_name}':
    
    {chunk_text}
    
    Regras:
    - Semânticas, representando temas, áreas, métodos ou conceitos.
    - Pode incluir termos específicos ou mais amplos relacionados.
    - Ex.: "coronavírus" → também "biologia", "saúde pública".
           "ensino inovador" → também "educação", "inovação".
           "tomada de decisões" → também "negócios", "administração".
    - Não use nomes de empresas, siglas soltas, códigos ou palavras genéricas sem contexto.
    - Português, preferencialmente no singular.
    - Responda apenas com as tags separadas por vírgula.
    """

# Gerar tags de um chunk
def generate_tags_from_chunk(client: OpenAI, chunk_text: str, column_name: str) -> list[str]:
    prompt = f"""
    Gere entre 1 e 4 tags curtas, relevantes e SIGNIFICATIVAS para o seguinte texto da coluna '{column_name}':
    
    {chunk_text}
    
    Regras:
    - Semânticas, podendo ser temas, áreas, métodos ou conceitos.
    
    - Gere de forma mais diversa possível, veja o exemplo:
    - Ex de artigo.: 'A Critical Analysis Of The Covid-19 Hospitalization Network In Countries With Limited Resources' 
    Possíveis tags do artigo: "Redes de Hospitalização", "COVID-19", "Desigualdades em Saúde", "Países de Baixa Renda"
           
    - Não use nomes de empresas, siglas soltas, códigos ou palavras genéricas sem contexto.
    - Em português.
    - Responda apenas com as tags separadas por vírgula.
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content.strip()
    return list(set([t.strip() for t in content.split(",") if t.strip()]))

# Filtrar tags por domínios
def filtrar_tag_por_dominio(client: OpenAI, tag: str, dominios=DOMINIOS) -> str | None:
    prompt = f"""
    Classifique a tag abaixo em um dos domínios listados.
    Se não fizer sentido em nenhum, responda apenas 'DESCARTAR'.

    Tag: "{tag}"
    Domínios: {', '.join(dominios)}
    """
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    classificacao = resp.choices[0].message.content.strip()
    if classificacao.upper() == "DESCARTAR":
        return None
    return classificacao

# Gerar tags de uma coluna inteira
def generate_tags_from_column(client: OpenAI, chunks: list[str], column_name: str) -> list[str]:
    all_tags = set()
    for chunk in chunks:
        try:
            tags = generate_tags_from_chunk(client, chunk, column_name)
            for t in tags:
                dominio = filtrar_tag_por_dominio(client, t)
                if dominio:
                    all_tags.add(t)
        except Exception as e:
            print(f"Erro ao gerar tags para chunk da coluna '{column_name}': {e}")
    return list(all_tags)

# Gerar tags por pesquisador
def generate_tags_for_researcher(client: OpenAI, chunks_dict: dict) -> list[str]:
    tags = set()
    for column_name, chunks in chunks_dict.items():
        if column_name == "metadata":
            continue
        tempo_inicio = time.time()
        column_tags = generate_tags_from_column(client, chunks, column_name)
        tags.update(column_tags)
        tempo_fim = time.time()
        print(f"Duração da coluna '{column_name}': {tempo_fim - tempo_inicio:.2f} seg")
    return list(tags)

# Pipeline principal
def generate_tags_pipeline(client: OpenAI, pesquisadores: dict) -> tuple[dict, list[str]]:
    tags_por_pesquisador = {}
    i = 1
    for pesquisador, chunks_dict in pesquisadores.items():
        if i < 2:
            print(f"Gerando tags para {pesquisador}...")
            tags_por_pesquisador[pesquisador] = generate_tags_for_researcher(client, chunks_dict)
            i += 1
        break
    
    tags_globais = set()
    for t_list in tags_por_pesquisador.values():
        for tag in t_list:
            tags_globais.add(tag.strip())  
    tags_globais = list(tags_globais)

    return tags_por_pesquisador, list(tags_globais)


# Visualização
def visualize_tags(tags_por_pesquisador: dict, tags_globais: list[str]):
    print("Tags por pesquisador:")
    for p, tags in tags_por_pesquisador.items():
        print(f"Pesquisador de ID:{p}\n\n {tags}")
        quant_tags_pesquisador = len(tags)
        print(f"Este pesquisador tem {quant_tags_pesquisador} tags")

    print("\nTags globais:")
    quant_tags_globais = len(tags_globais)
    print(f"Existem {quant_tags_globais} tags globais")
    print(tags_globais)
