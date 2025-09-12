FROM pgvector/pgvector:pg17
COPY ./curriculo_information/init_scripts/ /docker-entrypoint-initdb.d/