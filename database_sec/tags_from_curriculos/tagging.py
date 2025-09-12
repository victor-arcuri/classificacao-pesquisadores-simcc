from typing import List, Set
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable

class TagOutput(BaseModel):
    tags: List[str] = Field(..., description="Lista extensa de termos que representam temas desse embedding")

def configurar_chain_de_tags() -> Runnable:
    prompt = ChatPromptTemplate.from_template(
        """
        Você é um especialista em analisar conteúdo acadêmico.
        O vetor de embedding a seguir representa o conteúdo da seção '{nome_da_secao}'.

        Vetor:
        {embedding}

        Com base neste vetor, gere o máximo possível de tags que capturem temas, áreas de conhecimento,
        disciplinas, métodos, objetos de estudo ou aplicações relacionadas.

        Retorne uma estrutura com a chave "tags", contendo uma lista de strings variadas (mínimo de 30 tags).
        """
    )
    llm = ChatOpenAI(model="gpt-4", temperature=0.5).with_structured_output(TagOutput)
    return prompt | llm

def obter_tags_para_embedding(chain: Runnable, nome_da_secao: str, embedding_vetor: List[float]) -> List[str]:
    try:
        print(f"  -> Gerando tags para a seção: '{nome_da_secao}'...")
        embedding_str = str(embedding_vetor)
        
        result = chain.invoke({
            "embedding": embedding_str,
            "nome_da_secao": nome_da_secao
        })

        if result and result.tags:
            print(f"    - Adicionadas {len(result.tags)} tags.")
            return result.tags
            
    except Exception as e:
        print(f"    - Ocorreu um erro ao processar a seção '{nome_da_secao}': {e}")
    
    return []

def gerar_tags_das_embeddings(listas_com_embeddings: List[dict]):
    chain = configurar_chain_de_tags()
    conjunto_geral_de_tags: Set[str] = set()

    print("Iniciando a geração de tags para os 20 primeiros pesquisadores...")

    for dicionario_pesquisador in listas_com_embeddings[:20]:
        pesquisador_id = dicionario_pesquisador.get('id_pesquisador', 'ID não encontrado')
        print(f"\nProcessando pesquisador: {pesquisador_id}")
        
        for nome_coluna, valor_coluna in dicionario_pesquisador.items():
            if nome_coluna.endswith('_embeddings') and valor_coluna:
                nome_da_secao = nome_coluna.replace('_embeddings', '')
                
                novas_tags = obter_tags_para_embedding(chain, nome_da_secao, valor_coluna)
                
                if novas_tags:
                    conjunto_geral_de_tags.update(novas_tags)

    print("\n" + "="*50)
    print("PROCESSAMENTO FINALIZADO")
    print(f"Total de tags únicas geradas: {len(conjunto_geral_de_tags)}")
    print("="*50)

    lista_tags_finais = sorted(list(conjunto_geral_de_tags))

    print("\nAmostra de até 100 tags geradas (em ordem alfabética):")
    print(lista_tags_finais[:100])