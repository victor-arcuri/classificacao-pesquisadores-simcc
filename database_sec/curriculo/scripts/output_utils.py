from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

def visualizar_chunks(dados_processados):
    if not dados_processados:
        print("\nO dicionário está vazio. Não tem chunks para mostrar.")
        return
    
    pesquisadores = list(dados_processados.items())[:2]
    
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
    console = Console()

    if df.empty:
        console.print("[bold red]O DataFrame está vazio. Nenhuma visualização para mostrar.[/bold red]")
        return

    console.print("\n[bold cyan]--- DataFrame Criado ---[/bold cyan]")
    console.print(f"[green]Dimensões do DataFrame:[/green] {df.shape}")

    df_amostra = df.head(1).copy()

    def formatar_vetor_unico(vetor, limite_valores=8):
        if vetor is None or not isinstance(vetor, (list, tuple)) or len(vetor) == 0:
            return Text("Nenhum vetor", style="bold red")
        
        valores = []
        for v in vetor[:limite_valores]:
            valores.append(f"{v:.4f}")
        texto_valores = ", ".join(valores)

        texto = Text("[", style="bold white")
        texto.append(texto_valores, style="cyan")
        texto.append(", ...", style="dim")
        texto.append("]", style="bold white")
        texto.append(f" (dim={len(vetor)})", style="green")

        return texto

    df_amostra["long_embeddings"] = df_amostra["long_embeddings"].apply(formatar_vetor_unico)
    df_amostra["short_embeddings"] = df_amostra["short_embeddings"].apply(formatar_vetor_unico)

    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("ID do Pesquisador", style="bold cyan", overflow="fold")
    table.add_column("Embeddings Prosa", overflow="fold")
    table.add_column("Embeddings Lista", overflow="fold")

    row = df_amostra.iloc[0]
    table.add_row(
        str(row["id_pesquisador"]),
        row["long_embeddings"],
        row["short_embeddings"],
    )

    console.print("\n[bold yellow]--- Visualização da Primeira Linha ---[/bold yellow]")
    console.print(table)
