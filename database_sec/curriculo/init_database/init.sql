CREATE TABLE IF NOT EXISTS curriculos (
    id_pesquisador VARCHAR(50) PRIMARY KEY,
    embeddings_prosa VECTOR(768),
    embeddings_lista VECTOR(768),
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);