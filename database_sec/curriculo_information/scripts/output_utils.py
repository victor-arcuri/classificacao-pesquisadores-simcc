from rich.console import Console
from rich.table import Table
from rich.text import Text

CORES = ["\x1b[34m", "\x1b[32m", "\x1b[36m", "\x1b[35m", "\x1b[33m"]

def visualizar_chunks(dados_processados):
    """
    Visualiza os chunks de texto para os primeiros pesquisadores no dicionário.
    """
    if not dados_processados:
        print("\nO dicionário está vazio. Não há chunks para mostrar.")
        return
    
    # Pega os 2 primeiros pesquisadores para a amostragem
    pesquisadores = list(dados_processados.items())[:2]
    
    for pesquisador_id, dados in pesquisadores:
        print(f"\n\n\n👤 Pesquisador ID: {pesquisador_id}")
        print("─" * 80)

        # Itera sobre todas as chaves (abstract, articles, etc.) do dicionário de dados
        for i, (chave, chunks) in enumerate(dados.items()):
            # Pula a chave de metadados e listas de chunks vazias
            if chave == 'metadata' or not chunks:
                continue
            
            titulo = chave.replace('_', ' ').upper()
            cor = CORES[i % len(CORES)] 
            
            print(f"\n{cor}📝 {titulo} ({len(chunks)} chunk(s) no total):\x1b[0m")
            for j, chunk in enumerate(chunks, 1):
                print(f"  {j:2d}. {chunk}")

    print("\n" + "─" * 80)

def visualizar_dataframe(df):
    """
    Visualiza uma amostra do DataFrame de embeddings usando a biblioteca Rich.
    """
    console = Console()

    if df.empty:
        console.print("[bold red]O DataFrame está vazio. Nenhuma visualização para mostrar.[/bold red]")
        return

    console.print("\n[bold cyan]--- DataFrame de Embeddings Criado ---[/bold cyan]")
    console.print(f"[green]Dimensões do DataFrame:[/green] {df.shape}")

    row_amostra = df.iloc[0]

    def formatar_vetor(vetor, limite_valores=8):
        if vetor is None or not hasattr(vetor, '__iter__') or not vetor:
            return Text("Vazio", style="bold red")
        
        valores_str = ", ".join([f"{v:.4f}" for v in vetor[:limite_valores]])
        
        texto = Text("[", style="bold white")
        texto.append(valores_str, style="cyan")
        texto.append(", ...]", style="dim")
        texto.append(f" (dim={len(vetor)})", style="green")
        return texto

    # Cria a tabela
    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    table.add_column("ID do Pesquisador", style="bold cyan", no_wrap=True)
    
    colunas_embedding = [col for col in df.columns if col.endswith('_embeddings')]
    
    # Adiciona uma coluna na tabela para cada tipo de embedding
    for col_name in colunas_embedding:
        header = col_name.replace('_embeddings', '').replace('_', ' ').title()
        table.add_column(f"Embeddings {header}", no_wrap=True)

    dados_linha = [str(row_amostra["id_pesquisador"])]
    for col_name in colunas_embedding:
        vetor_formatado = formatar_vetor(row_amostra[col_name])
        dados_linha.append(vetor_formatado)
        
    table.add_row(*dados_linha)

    console.print("\n[bold yellow]--- Amostra da Primeira Linha do DataFrame ---[/bold yellow]")
    console.print(table)