from tabulate import tabulate

def visualizar_chunks(dados_processados):
    """Exibe 5 primeiros chunks."""
    if not dados_processados:
        print("\nO dicionário está vazio. Não tem chunks para mostrar.")
        return
    
    pesquisadores = list(dados_processados.items())[:2]  # Selecione de quantos pesquisadores quer ver as chunks
    
    for pesquisador_id, dados in pesquisadores:
        print(f"\n👤 Pesquisador ID: {pesquisador_id}")
        print("─" * 60)

        if dados["prose_chunks"]:
            print(f"\n\x1b[34m📝 PROSA CHUNKS ({len(dados['prose_chunks'])} no total):\x1b[0m")
            for i, chunk in enumerate(dados["prose_chunks"], 1):
                print(f"{i:2d}. {chunk}")

        if dados["list_chunks"]:
            print(f"\n\x1b[32m📋 LISTA CHUNKS ({len(dados['list_chunks'])} no total):\x1b[0m")
            for i, chunk in enumerate(dados["list_chunks"], 1):
                print(f"{i:2d}. {chunk}")

    print("─" * 60)
        
def visualizar_dataframe(df):
    """Exibe dimensões do Dataframe e primeira linha."""
    if df.empty:
        print("\nO DataFrame está vazio. Nenhuma visualização para mostrar.")
        return

    print("\n--- DataFrame Criado ---")
    print(f"\nDimensões do DataFrame: {df.shape}")

    print("\n--- Visualização da Primeira Linha em Formato de Tabela ---")
    df_amostra = df.head(1).copy()

    # Função para formatar as listas de embeddings para visualização
    def formatar_lista_embeddings(lista_de_vetores):
        if not lista_de_vetores:
            return "Nenhum"
        num_vetores = len(lista_de_vetores)
        primeiro_vetor_amostra = f"[{', '.join(map(str, lista_de_vetores[0][:3]))}, ...]"
        return f"{num_vetores} vetor(es) | 1º: {primeiro_vetor_amostra}"

    df_amostra['embeddings_prosa'] = df_amostra['embeddings_prosa'].apply(formatar_lista_embeddings)
    df_amostra['embeddings_lista'] = df_amostra['embeddings_lista'].apply(formatar_lista_embeddings)
    
    tabela_formatada = tabulate(df_amostra, headers='keys', tablefmt='psql', showindex=False)
    print(tabela_formatada)