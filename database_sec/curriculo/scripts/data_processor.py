import csv
from langchain_text_splitters import RecursiveCharacterTextSplitter

def processar_linhas_csv(caminho_arquivo, coluna_id, colunas_prosa, colunas_lista, colunas_lista_de_prosas, chunk_size, chunk_overlap):
    """
    Lê um arquivo CSV e processa seu conteúdo, separando os textos em chunks.

    Retorna:
        dict: Um dicionário onde cada chave é um researcher_id e o valor contém
              listas de chunks para cada coluna e um dicionário de metadados.
    """
    dados_processados = {}

    text_splitter_prosa = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", ", ", " "],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )

    with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)

        # Esse for percorre todos os pesquisadores presentes no csv
        for i, linha in enumerate(leitor_csv):
            if not linha or not linha.get(coluna_id):
                print(f"Aviso: Linha {i+2} do CSV ignorada por não conter um '{coluna_id}' válido.")
                continue

            id_pesquisador = linha[coluna_id]

            # Adiciona o pesquisador ao dicionário se for a primeira vez que o encontramos
            if id_pesquisador not in dados_processados:
                dados_processados[id_pesquisador] = {
                    "abstract": [],
                    "articles": [],
                    "project_name": [],
                    "description_project": [],
                    "great_area": [],
                    "area_specialty": [],
                    "patent": [], 
                    "book_chapter": [],
                    "event_name": []
                }

            # Percorre as colunas da linha específica daquele pesquisador
            for nome_coluna, valor_coluna in linha.items():
                if not valor_coluna or valor_coluna.strip() == 'Sem registro':
                    continue

                # Caso de ser 'abstract' 
                if nome_coluna in colunas_prosa:
                    chunks_de_prosa = text_splitter_prosa.split_text(valor_coluna)
                    for chunk in chunks_de_prosa:
                        conteudo = f"Do registro com ID '{id_pesquisador}', um trecho da coluna '{nome_coluna}' é: {chunk}"
                        dados_processados[id_pesquisador][nome_coluna].append(conteudo)
                
                # Caso de ser 'description_project'
                elif nome_coluna in colunas_lista_de_prosas:
                    itens_da_lista = valor_coluna.split('; ')
                    for k, item in enumerate(itens_da_lista):
                        item_limpo = item.strip()
                        if not item_limpo: continue
                        
                        chunks_do_item = text_splitter_prosa.split_text(item_limpo)
                        
                        for j, chunk in enumerate(chunks_do_item):
                            conteudo = f"Do registro com ID '{id_pesquisador}', um trecho do item {k+1} da coluna '{nome_coluna}' é: {chunk}"
                            dados_processados[id_pesquisador][nome_coluna].append(conteudo)
                
                # --- Cada caso de colunas com listas ---
                elif nome_coluna in colunas_lista:
                    itens_da_lista = valor_coluna.split('; ')
                    for item in itens_da_lista:
                        item_limpo = item.strip()
                        if not item_limpo: continue

                        match nome_coluna:
                            case "project_name":
                                conteudo = f"Do registro com ID '{id_pesquisador}', o nome de um projeto é: {item_limpo}"
                                dados_processados[id_pesquisador]["project_name"].append(conteudo)
                            case "great_area":
                                conteudo = f"Do registro com ID '{id_pesquisador}', uma grande área de atuação é: {item_limpo}"
                                dados_processados[id_pesquisador]["great_area"].append(conteudo)
                            case "area_specialty":
                                conteudo = f"Do registro com ID '{id_pesquisador}', uma especialidade da área é: {item_limpo}"
                                dados_processados[id_pesquisador]["area_specialty"].append(conteudo)
                            case "patent":
                                conteudo = f"Do registro com ID '{id_pesquisador}', uma patente registrada é: {item_limpo}"
                                dados_processados[id_pesquisador]["patent"].append(conteudo)
                            case "book_chapter":
                                conteudo = f"Do registro com ID '{id_pesquisador}', um capítulo de livro publicado é: {item_limpo}"
                                dados_processados[id_pesquisador]["book_chapter"].append(conteudo)
                            case "event_name":
                                conteudo = f"Do registro com ID '{id_pesquisador}', o nome de um evento com participação é: {item_limpo}"
                                dados_processados[id_pesquisador]["event_name"].append(conteudo)
                            case "articles":
                                conteudo = f"Do registro com ID '{id_pesquisador}', o nome de um evento com participação é: {item_limpo}"
                                dados_processados[id_pesquisador]["articles"].append(conteudo)
                            case _:
                                print(f"--- Aviso: Coluna de lista '{nome_coluna}' não possui um 'case' definido. ---")

    # --- Criação dos Metadados ---
    for id_pesquisador, dados in dados_processados.items():
        chunk_counts = {}
        for nome_coluna, lista_chunks in dados.items():
            chunk_counts[nome_coluna] = len(lista_chunks)

        dados["metadata"] = {
            "researcher_id": id_pesquisador,
            "chunk_counts": chunk_counts
        }

    return dados_processados