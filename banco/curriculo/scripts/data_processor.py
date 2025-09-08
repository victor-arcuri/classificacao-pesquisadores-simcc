import csv
from langchain_text_splitters import RecursiveCharacterTextSplitter

def processar_linhas_csv(caminho_arquivo, coluna_id, colunas_prosa, colunas_lista, colunas_lista_de_prosas, chunk_size, chunk_overlap):
    """
    Lê um arquivo CSV e processa seu conteúdo, separando os textos em chunks de prosa e de lista.

    Retorna:
        dict: Um dicionário onde cada chave é um researcher_id e o valor contém
              listas de 'prose_chunks' e 'list_chunks'.
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

        for i, linha in enumerate(leitor_csv):
            if not linha or not linha.get(coluna_id):
                print(f"Aviso: Linha {i+2} do CSV ignorada por não conter um '{coluna_id}' válido.")
                continue

            id_pesquisador = linha[coluna_id]

            if id_pesquisador not in dados_processados:
                dados_processados[id_pesquisador] = {
                    "prose_chunks": [],
                    "list_chunks": []
                }

            for nome_coluna, valor_coluna in linha.items():
                if not valor_coluna or valor_coluna.strip() == 'Sem registro':
                    continue

                if nome_coluna in colunas_lista:
                    itens_da_lista = valor_coluna.split('; ')
                    for item in itens_da_lista:
                        item_limpo = item.strip()
                        if item_limpo:
                            conteudo = f"Do registro com ID '{id_pesquisador}', um item da lista na coluna '{nome_coluna}' é: {item_limpo}"
                            dados_processados[id_pesquisador]["list_chunks"].append(conteudo)
                
                elif nome_coluna in colunas_lista_de_prosas:
                    # 1. Primeiro, divide a coluna em itens de lista
                    itens_da_lista = valor_coluna.split('; ')
                    for k, item in enumerate(itens_da_lista):
                        item_limpo = item.strip()
                        if not item_limpo: continue
                        
                        # 2. Depois, aplica o text_splitter a cada item individualmente
                        chunks_do_item = text_splitter_prosa.split_text(item_limpo)
                        
                        for j, chunk in enumerate(chunks_do_item):
                            conteudo = f"Do registro com ID '{id_pesquisador}', um trecho do item {k+1} da coluna '{nome_coluna}' é: {chunk}"
                            dados_processados[id_pesquisador]["prose_chunks"].append(conteudo)
                
                elif nome_coluna in colunas_prosa:
                    chunks_de_prosa = text_splitter_prosa.split_text(valor_coluna)
                    for chunk in chunks_de_prosa:
                        conteudo = f"Do registro com ID '{id_pesquisador}', um trecho da coluna '{nome_coluna}' é: {chunk}"
                        dados_processados[id_pesquisador]["prose_chunks"].append(conteudo)

                else:
                    if nome_coluna != coluna_id:
                        conteudo = f"Do registro com ID '{id_pesquisador}', a informação de '{nome_coluna}' é: '{valor_coluna}'"
                        dados_processados[id_pesquisador]["list_chunks"].append(conteudo)

    return dados_processados