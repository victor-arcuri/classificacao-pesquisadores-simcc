FROM pgvector/pgvector:pg17
COPY ./init_scripts/ /docker-entrypoint-initdb.d/