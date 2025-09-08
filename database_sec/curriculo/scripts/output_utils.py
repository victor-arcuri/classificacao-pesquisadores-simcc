from rich.console import Console
from rich.table import Table

def visualizar_chunks(dados_processados):
    """
    Exibe todos os chunks de 2 pesquisadores, separados em chunks que vieram de textos em prosa (abstract e description_project)
    e em chunks que vieram de listas que tem tamanho de texto menor (todos os outros e description_project - para separá-lo em listas primeiro -)
    """
    
    if not dados_processados:
        print("\nO dicionário está vazio. Não tem chunks para mostrar.")
        return
    
    pesquisadores = list(dados_processados.items())[:2]  # Selecione de quantos pesquisadores quer ver as chunks
    
    for pesquisador_id, dados in pesquisadores:
        print(f"\n\n\n👤 Pesquisador ID: {pesquisador_id}")
        print("─" * 60)

        if dados["prose_chunks"]:
            print(f"\n\x1b[34m📝 PROSA CHUNKS ({len(dados['prose_chunks'])} no total):\x1b[0m")
            for i, chunk in enumerate(dados["prose_chunks"], 1):
                print(f"{i:2d}. {chunk}")

        print("\n\n\n")

        if dados["list_chunks"]:
            print(f"\n\x1b[32m📋 LISTA CHUNKS ({len(dados['list_chunks'])} no total):\x1b[0m")
            for i, chunk in enumerate(dados["list_chunks"], 1):
                print(f"{i:2d}. {chunk}")

    print("─" * 60)
        
def visualizar_dataframe(df):
    """Exibe a primeira linha do DataFrame com 5 vetores (8 valores cada) formatados."""
    console = Console()

    if df.empty:
        console.print("[bold red]O DataFrame está vazio. Nenhuma visualização para mostrar.[/bold red]")
        return

    console.print("\n[bold cyan]--- DataFrame Criado ---[/bold cyan]")
    console.print(f"[green]Dimensões do DataFrame:[/green] {df.shape}")

    df_amostra = df.head(1).copy()

    def formatar_varios_vetores(vetores, limite_vetores=5, limite_valores=8):
        if not vetores:
            return "Nenhum vetor"

        output = [f"{len(vetores)} vetor(es):"]
        for i, vetor in enumerate(vetores[:limite_vetores]):
            valores = ", ".join(f"{v:.4f}" for v in vetor[:limite_valores])
            output.append(f" {i+1:>2d} → [{valores}, ...]")
        return "\n".join(output)

    # Aplicar a formatação
    df_amostra["embeddings_prosa"] = df_amostra["embeddings_prosa"].apply(
        lambda v: formatar_varios_vetores(v)
    )
    df_amostra["embeddings_lista"] = df_amostra["embeddings_lista"].apply(
        lambda v: formatar_varios_vetores(v)
    )

    # Criar a tabela
    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("ID do Pesquisador", style="bold cyan", overflow="fold")
    table.add_column("Embeddings Prosa", overflow="fold")
    table.add_column("Embeddings Lista", overflow="fold")

    row = df_amostra.iloc[0]
    table.add_row(
        str(row["id_pesquisador"]),
        str(row["embeddings_prosa"]),
        str(row["embeddings_lista"]),
    )

    console.print("\n[bold yellow]--- Visualização da Primeira Linha ---[/bold yellow]")
    console.print(table)