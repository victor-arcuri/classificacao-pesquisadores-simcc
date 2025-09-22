# Instala as dependências dos scripts de otimização do banco de tags
FROM python:3 AS requisitos-otimizacao-banco-tags
WORKDIR /app/otimizacao-banco-tags
COPY ./otimizacao-tags/requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -Ur requirements.txt

# Cria o ambiente geral com as dependências de cada script isoladas
FROM python:3 as ambiente
WORKDIR /app
# Copia os ambientes virtuais dos scripts para seus respectivos diretórios
COPY --from=requisitos-otimizacao-banco-tags  /opt/venv  /app/otimizacao-banco-tags/venv
# Copia os scripts de otimização
COPY ./otimizacao-tags/otimizacao-tags.py  /app/otimizacao-banco-tags/otimizacao-tags.py
CMD ["tail", "-f", "/dev/null"]