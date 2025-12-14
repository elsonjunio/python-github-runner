# python-github-runner

Gerenciador de GitHub Actions self-hosted runners via API, projetado para executar múltiplos runners em um único host ou container, reutilizando uma base imutável do GitHub Runner, com foco em baixo consumo de espaço, isolamento por repositório e automação completa.

O projeto expõe uma API (FastAPI) que permite registrar, listar e gerenciar runners dinamicamente, sem necessidade de GitHub Organization — apenas repositórios individuais.

---

### ✨ Principais características

✅ Gerenciamento de runners self-hosted por repositório

✅ Reutilização de um runner base imutável

✅ Um único container Docker para múltiplos runners

✅ API REST para criação e listagem de runners

✅ Compatível com runners oficiais do GitHub

✅ Não requer permissões de root para execução dos runners

✅ Ideal para ambientes locais, servidores dedicados ou homelab

---

### 📂 Estrutura do projeto

```bash
.
├── docker
│   └── docker-compose.yml
├── Dockerfile
├── poetry.lock
├── pyproject.toml
├── python_github_action
│   ├── api
│   │   └── runners.py          # Endpoints da API
│   ├── config.py               # Configurações globais
│   ├── domain
│   │   ├── runner.py           # Entidade Runner
│   │   └── runner_create.py    # DTO de criação
│   ├── infra
│   │   └── filesystem.py       # Manipulação de diretórios e links
│   ├── services
│   │   └── runner_factory.py   # Criação e registro de runners
│   └── main.py                 # Entrada da aplicação (FastAPI)
└── README.md
```
---

### 🧠 Arquitetura (visão geral)

 - Existe um diretório base imutável do GitHub Runner
 - Para cada repositório:
  - Um novo diretório é criado
  - Arquivos imutáveis são reutilizados (linkados/copied)
  - O runner é registrado usando o token do repositório
 - Cada runner executa como um processo independente
 - O gerenciamento é feito via API HTTP

---

### 🧱 Preparando o runner base (imutável)

O diretório base contém a instalação oficial do GitHub Actions Runner e é reutilizado por todos os runners criados.

Passo a passo (adaptado da documentação oficial)


```bash
# Crie o diretório base do runner
mkdir -p ./docker/github-runner-base
cd ./docker/github-runner-base

# Baixe o runner oficial
curl -o actions-runner-linux-x64-2.329.0.tar.gz \
  -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz

# (Opcional) Validar hash
echo "194f1e1e4bd02f80b7e9633fc546084d8d4e19f3928a324d512ea53430102e1d  actions-runner-linux-x64-2.329.0.tar.gz" \
  | shasum -a 256 -c

# Extrair
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz

# Remover o tarball
rm ./actions-runner-linux-x64-2.329.0.tar.gz
```
*📌 Importante: este diretório não deve ser modificado após criado.*

🐳 Executando com Docker
Build da imagem
```bash
docker build -t python-github-runner .
```

Subindo com docker-compose
```
docker compose up -d
```

Após subir, a API estará disponível em:

```
http://127.0.0.1:8000
```

### 📖 Documentação da API (Swagger)

Acesse:

```
http://127.0.0.1:8000/docs
```

#### ➕ Criando um runner via API

**Endpoint**
```
POST /runners
```
```json
Payload de exemplo
{
  "name": "python-github-runner",
  "repo_url": "https://github.com/elsonjunio/python-github-runner",
  "token": "ANCIIX2PZINAUGAT7Q4QNN3JH3AAA"
}
```

**Onde obter o token**

1 - Vá até o repositório no GitHub

2 - Acesse Settings

3 - Vá em Actions → Runners

4 - Clique em New self-hosted runner

5 - Copie o token exibido (válido por tempo limitado)

**📋 Listando runners**
```
GET /runners
```
```json
Resposta típica:

[
  {
    "name": "python-github-runner",
    "repo_url": "https://github.com/elsonjunio/python-github-runner",
    "status": "running",
    "pid": 1234
  }
]
```
---

### 🧪 Testando no GitHub Actions

Exemplo de workflow:
```yml
name: Self-hosted runner test

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: self-hosted
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - run: |
          node -v
          npm -v
```

Se o runner estiver corretamente registrado, o job será executado nele.

---

### 🔐 Observações importantes

- O runner não executa como root

- sudo é explicitamente desabilitado

- Dependências do .NET e Node são resolvidas no container

- O uso de actions/setup-node é recomendado (comportamento padrão do GitHub)

---

### 🚀 Próximos passos (ideias)

- Labels customizados por runner

- Escalonamento automático

- Remoção automática de runners inativos

- Suporte a múltiplas versões de runner base

- Autenticação na API

---

### 📜 Licença

**MIT**