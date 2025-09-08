import os
from dotenv import load_dotenv

def carregar_chave_api():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
    else: print("Chave carregada!!!\n")
    return api_key