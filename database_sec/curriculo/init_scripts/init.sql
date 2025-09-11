-- Habilita a extensão pgvector
CREATE EXTENSION IF NOT EXISTS "vector";

-- Criação da tabela curriculos para armazenar os embeddings vetoriais
CREATE TABLE IF NOT EXISTS curriculos (
    id_pesquisador UUID PRIMARY KEY,
    abstract_embeddings VECTOR(1536),
    articles_embeddings VECTOR(1536),
    project_name_embeddings VECTOR(1536),
    description_project_embeddings VECTOR(1536),
    great_area_embeddings VECTOR(1536),
    area_specialty_embeddings VECTOR(1536),
    patent_embeddings VECTOR(1536),
    book_chapter_embeddings VECTOR(1536),
    event_name_embeddings VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_in TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Função que atualiza automaticamente a coluna updated_in em updates
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_in = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger que chama a função acima antes de qualquer UPDATE
DROP TRIGGER IF EXISTS update_curriculos_timestamp ON curriculos;

CREATE TRIGGER update_curriculos_timestamp
BEFORE UPDATE ON curriculos
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();
