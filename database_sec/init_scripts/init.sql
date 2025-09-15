CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

CREATE TABLE IF NOT EXISTS researcher_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_in TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS researcher_tags_on_researchers (
    researcher_id UUID NOT NULL,
    tag_id UUID NOT NULL,
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT researcher_tags_on_researchers_pkey PRIMARY KEY (researcher_id, tag_id),
    CONSTRAINT researcher_tags_on_researchers_researcher_id_fkey 
        FOREIGN KEY (researcher_id) 
        REFERENCES curriculos(id_pesquisador) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT researcher_tags_on_researchers_tag_id_fkey 
        FOREIGN KEY (tag_id) 
        REFERENCES researcher_tags(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_in = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_curriculos_timestamp ON curriculos;
CREATE TRIGGER update_curriculos_timestamp
BEFORE UPDATE ON curriculos
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

DROP TRIGGER IF EXISTS set_timestamp ON researcher_tags;
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON researcher_tags
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();