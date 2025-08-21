import json
import os

def salvar_em_json(dados, nome_do_arquivo="dados.json"):
    """
    Salva um dicionário em um arquivo JSON dentro da pasta 'data'.
    """
    # Garante que o caminho para o arquivo inclua a pasta 'data'
    caminho_da_pasta = '../data'
    if not os.path.exists(caminho_da_pasta):
        os.makedirs(caminho_da_pasta)

    caminho_do_arquivo = os.path.join(caminho_da_pasta, nome_do_arquivo)

    print(f"Salvando dados em: {caminho_do_arquivo}")
    with open(caminho_do_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print("Arquivo JSON salvo com sucesso.")