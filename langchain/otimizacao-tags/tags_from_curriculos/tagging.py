import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.table import Table

# Domínios temáticos disponíveis
DOMINIOS = [
    "Ciência da Computação",
    "Tecnologia da Informação",
    "Educação e Ensino",
    "Saúde",
    "Biologia",
    "Ciências da Vida",
    "Química",
    "Farmacologia",
    "Engenharias",
    "Sustentabilidade",
    "Matemática",
    "Estatística",
    "Física",
    "Ciências Sociais",
    "Ciencias Humanas",
    "Economia e Negócios",
    "Direito",
    "Políticas Públicas",
    "Artes",
    "Cultura",
    "Ciência de Dados",
    "Inteligência Artificial",
    "Meio Ambiente",
    "Ecologia"
]

BATCH_SIZE = 50  # Define o tamanho do lote para as chamadas à API

def criar_client() -> ChatOpenAI:
    """Cria e configura o cliente ChatOpenAI."""
    load_dotenv()
    client = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    return client

def generate_tags_from_column(client: ChatOpenAI, chunks: list[str], column_name: str) -> list[str]:
    """
    Gera e filtra tags para uma lista de chunks de texto usando chamadas em lote (batch).
    """
    if not chunks:
        return []

    tag_extraction_prompt = ChatPromptTemplate.from_template("""
        Extraia de 1 a 2 tags de pesquisa do texto a seguir.

        Texto:
        ---
        {chunk_text}
        ---

        Diretrizes:
        - Tags devem ser conceitos, áreas de conhecimento ou metodologias. Em português.
        - Máximo de 3 palavras por tag.
        - Evite: nomes, instituições, siglas e termos genéricos (ex: 'artigo', 'pesquisa').
        - Bons exemplos: 'Tecnologia da Informação', 'Pesquisa Científica', 'Ciência da Computação', 'Robótica Educacional'.

        Responda APENAS com as tags separadas por vírgula.
        """)
    tag_extraction_chain = tag_extraction_prompt | client | StrOutputParser()

    all_generated_tags = set()
    prompts = [{"chunk_text": chunk} for chunk in chunks]

    for i in range(0, len(prompts), BATCH_SIZE):
        batch = prompts[i:i + BATCH_SIZE]
        responses = tag_extraction_chain.batch(batch, config={"max_concurrency": 5})
        for response in responses:
            tags = [tag.strip() for tag in response.split(',') if tag.strip()]
            all_generated_tags.update(tags)

    if not all_generated_tags:
        return []

    # --- 2. Filtragem de Tags por Domínio em Lote ---
    domain_filtering_prompt = ChatPromptTemplate.from_template("""
    Classifique a tag "{tag}" em um dos seguintes domínios: {dominios}.
    Se a tag não se encaixar em nenhum dos domínios, responda APENAS com a palavra 'DESCARTAR'.
    Caso contrário, responda APENAS com o nome do domínio correspondente.
    """)
    domain_filtering_chain = domain_filtering_prompt | client | StrOutputParser()

    unique_tags = list(all_generated_tags)
    prompts = [{"tag": tag, "dominios": ", ".join(DOMINIOS)} for tag in unique_tags]
    valid_tags = []

    for i in range(0, len(prompts), BATCH_SIZE):
        batch_prompts = prompts[i:i + BATCH_SIZE]
        batch_tags = unique_tags[i:i + BATCH_SIZE]
        responses = domain_filtering_chain.batch(batch_prompts, config={"max_concurrency": 5})
        for tag, domain in zip(batch_tags, responses):
            if "DESCARTAR" not in domain.upper():
                valid_tags.append(tag)

    return valid_tags

# Gerar tags por pesquisador
def generate_tags_for_researcher(client: ChatOpenAI, chunks_dict: dict) -> list[str]:
    tags = set()
    for column_name, chunks in chunks_dict.items():
        if column_name == "metadata":
            continue
        tempo_inicio = time.time()
        print(f"  -> Gerando tags para a coluna '{column_name}' ({len(chunks)} chunks)...")
        column_tags = generate_tags_from_column(client, chunks, column_name)
        tags.update(column_tags)
        tempo_fim = time.time()
        print(f"     Coluna '{column_name}' finalizada em {tempo_fim - tempo_inicio:.2f}s. {len(column_tags)} tags válidas encontradas.")
    return list(tags)

# Pipeline principal
def generate_tags_pipeline(client: ChatOpenAI, pesquisadores: dict) -> tuple[dict, list[str]]:
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
    console = Console()
    console.print("\n[bold cyan]--- Tags Geradas por Pesquisador ---[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("ID do Pesquisador", style="cyan", no_wrap=True)
    table.add_column("Nº de Tags", style="yellow")
    table.add_column("Tags Geradas", style="green")

    for p, tags in tags_por_pesquisador.items():
        tags_str = ", ".join(sorted(tags))
        table.add_row(str(p), str(len(tags)), tags_str)

    console.print(table)

    console.print("\n[bold cyan]--- Resumo das Tags Globais ---[/bold cyan]")
    quant_tags_globais = len(tags_globais)
    console.print(f"Total de [bold yellow]{quant_tags_globais}[/bold yellow] tags únicas encontradas.")
    
    # Mostra uma amostra das tags globais
    amostra_tags = sorted(tags_globais)[:20]
    console.print("[dim]Amostra:[/dim]", ", ".join(amostra_tags) + ("..." if quant_tags_globais > 20 else ""))