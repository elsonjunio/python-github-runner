FROM python:3.12-slim

# -----------------------------
# Variáveis de ambiente
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretórios padrão (batem com seu .env)
ENV BASE_IMMUTABLE_DIR=/opt/github-runner-base
ENV BASE_RUNNER_DIR=/opt/github-runners

# -----------------------------
# Dependências de sistema
# -----------------------------
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    git \
    procps \
    ca-certificates \
    rsync \
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Diretório da aplicação
# -----------------------------
WORKDIR /app

# -----------------------------
# Instala Poetry
# -----------------------------
RUN pip install --no-cache-dir poetry

# -----------------------------
# Copia arquivos de dependência
# -----------------------------
COPY pyproject.toml poetry.lock* /app/

# -----------------------------
# Instala dependências (sem venv)
# -----------------------------
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --only main

# -----------------------------
# Copia código da aplicação
# -----------------------------
COPY python_github_action /app/python_github_action

# -----------------------------
# Cria diretórios base (serão montados)
# -----------------------------
RUN mkdir -p \
    ${BASE_IMMUTABLE_DIR} \
    ${BASE_RUNNER_DIR}

# -----------------------------
# Porta da API
# -----------------------------
EXPOSE 8000

# -----------------------------
# Comando de inicialização
# -----------------------------
CMD ["uvicorn", "python_github_action.main:app", "--host", "0.0.0.0", "--port", "8000"]
