# Projeto: Automação de Agendamento Médico com n8n e FastAPI

Este projeto implementa um sistema completo de agendamento médico, composto por uma API back-end robusta construída com FastAPI e um chatbot inteligente para atendimento ao cliente, orquestrado pelo n8n e potencializado pelo Google Gemini.

O sistema permite que pacientes consultem horários disponíveis, agendem consultas, cancelem agendamentos e obtenham informações, tudo através de uma interface de chat. O back-end gerencia médicos, pacientes, horários (slots) e agendamentos, com uma camada de cache em Redis para otimização de performance.

## Principais Funcionalidades

* **API Back-end (FastAPI):**
    * Gerenciamento (CRUD) completo de Médicos, Pacientes, Horários (Slots) e Agendamentos.
    * Validação de regras de negócio (ex: não agendar em horários ocupados ou no passado).
    * Geração de dados fictícios (`seed`) para popular o banco de dados para testes e dashboards.
    * Documentação automática da API via Swagger UI (`/docs`) e Redoc (`/redoc`).
* **Chatbot (n8n + Gemini):**
    * Interface de chat para interação com o usuário.
    * Suporte a entrada de texto e áudio (com transcrição via Gemini).
    * Roteamento de intenção baseado em LLM (Gemini) para identificar a ação do usuário (agendar, cancelar, etc.).
    * Memória de sessão para lembrar dados do paciente (nome, email, ID) após o primeiro cadastro.
    * Notificações por e-mail (Gmail) para confirmação de agendamentos e cancelamentos.
* **Performance e BI:**
    * **Cache:** Utiliza Redis para armazenar em cache a lista de horários disponíveis, reduzindo a carga no banco de dados.
    * **Dashboards:** O `docker-compose.yml` inclui um serviço do Metabase, pré-configurado para se conectar ao banco de dados e permitir a criação de dashboards de BI.
* **Testes:**
    * Suíte de testes unitários com Pytest para validar os endpoints da API e a lógica de negócios.
    * Testes executados em um banco de dados SQLite em memória para total isolamento.
## Tecnologias Utilizadas

| Categoria | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Back-end** | **Python 3.10+** | Linguagem principal da API. |
| | **FastAPI** | Framework web moderno para construção da API. |
| | **SQLAlchemy** | ORM para interação com o banco de dados. |
| | **Pydantic** | Validação de dados de entrada/saída (schemas). |
| | **SQLite** | Banco de dados relacional (arquivo `med_agenda.db`). |
| **Automação** | **n8n** | Plataforma de automação (low-code) que orquestra o fluxo do chatbot. |
| | **Google Gemini** | LLM usado para roteamento de intenção, transcrição de áudio e formatação de respostas. |
| **Infraestrutura** | **Docker / Docker Compose** | Contenização dos serviços de n8n, Redis e Metabase. |
| **Cache** | **Redis** | Banco de dados em memória usado para cache de horários. |
| **BI** | **Metabase** | Ferramenta de Business Intelligence para visualização dos dados. |
| **Testes** | **Pytest** | Framework de testes para a API. |

## Arquitetura da Solução

O sistema é desenhado com uma arquitetura desacoplada:

1.  **Serviços em Docker:** O `docker-compose.yml` gerencia os serviços de suporte:
    * `n8n`: (Porta `5678`) Executa o workflow do chatbot.
    * `redis`: (Porta `6379`) Fornece o cache.
    * `metabase`: (Porta `3000`) Fornece a plataforma de BI.
2.  **API Local (Host):** A API FastAPI é executada diretamente na máquina host (fora do Docker) na porta `8000`.
3.  **Comunicação:** O workflow do n8n (que está em um contêiner) se comunica com a API na máquina host usando o endereço especial `http://host.docker.internal:8000`.
## Instalação e Execução (Passo a Passo)

Siga estas etapas para configurar e executar o projeto completo.

### Pré-requisitos

* Git
* Python 3.10+
* Docker
* Docker Compose

### 1. Clonar o Repositório

```bash
git clone <url-do-seu-repositorio>
cd n8n_automatization
```

## 2. Iniciar Serviços de Suporte (Docker)

Execute o Docker Compose para iniciar o n8n, Redis e Metabase em segundo plano.

```bash
docker-compose up -d --build
```

Após a execução, os serviços estarão acessíveis nos seguintes endereços:

* **n8n:** `http://localhost:5678`
* **Metabase:** `http://localhost:3000`
* **Redis:** `localhost:6379`

## 3. Configurar e Executar a API (Local)

A API FastAPI será executada localmente na sua máquina.

### 1. Crie um ambiente virtual

```bash
python -m venv venv
```

### 2. Ative o ambiente virtual

* **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```

* **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 3. Crie um arquivo `requirements.txt`

Crie um arquivo chamado `requirements.txt` na raiz do seu diretório `api` com o seguinte conteúdo:

```text
fastapi
uvicorn[standard]
sqlalchemy
pydantic
redis
python-multipart
pydantic-email
pytest
httpx
```

### 4. Instale os pacotes

Com o ambiente virtual ainda ativado, instale as dependências:

```bash
pip install -r requirements.txt
```

### 5. Popule o banco de dados (primeira execução)

Este comando irá criar o arquivo `med_agenda.db` (se não existir) e populá-lo com dados fictícios para teste.

```bash
python -m api.seed
```

### 6. Execute a API FastAPI

Inicie o servidor da API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Neste ponto, a API está rodando e acessível em `http://localhost:8000`. Você pode ver a documentação interativa da API em `http://localhost:8000/docs`.

## 4. Configurar o n8n

1.  **Acesse o n8n:** Abra `http://localhost:5678` no seu navegador.
2.  Crie um novo workflow ou vá para a lista de workflows existentes.
3.  **Importe o workflow:**
    * Vá em **Import > From File**.
    * Selecione o arquivo `export_n8n.json` do projeto.
4.  **Configurar Credenciais:** O workflow importado precisa de credenciais para funcionar.
    * No painel esquerdo do n8n, vá em **Credentials**.
    * Crie novas credenciais para `"Google Gemini(PaLM) Api"` e `"Gmail OAuth2"`, seguindo as instruções de cada uma.
    * Após criar as credenciais, volte ao workflow e associe as credenciais corretas nos nós do **Gemini** e **Gmail**.
5.  **Ative o Workflow:** Salve as alterações e ative o workflow clicando no toggle **"Active"** no canto superior esquerdo.
6.  **Acesse o Chat:**
    * Clique no nó `"When chat message received"`.
    * Copie a **URL do Webhook de chat** (ex: `http://localhost:5678/chat/webhook/35a54de6...`).
    * Abra essa URL em um novo navegador para interagir com o chatbot.

    ## 5. (Opcional) Configurar o Metabase

1.  **Acesse o Metabase:** Abra `http://localhost:3000` no seu navegador.
2.  Faça a configuração inicial (criar conta de administrador, etc.).
3.  Na tela principal, clique em **Adicionar seu banco de dados**.
4.  Selecione o tipo de banco de dados: **SQLite**.
5.  No campo "Caminho do arquivo", use o caminho *interno do contêiner* do Metabase, que foi mapeado no `docker-compose.yml`:
    ```
    /metabase-data/med_agenda.db
    ```
6.  Salve a configuração. Agora você pode explorar os dados e criar dashboards.

## Utilização

### API (FastAPI)

A API é o cérebro do sistema. Ela expõe os seguintes endpoints:

* `GET /`: Verifica o status da API.
* `GET /horarios`: Retorna uma lista de todos os horários futuros disponíveis (cacheado pelo Redis).
* `POST /agendar`: Agenda uma consulta. Requer `slot_id` e `patient_id`.
* `POST /cancelar/{appointment_id}`: Cancela um agendamento existente.
* `GET /pagamento`: Retorna informações estáticas sobre valores e métodos de pagamento.
* `POST /pacientes/`: Cria um novo paciente ou retorna um existente se o e-mail já estiver cadastrado.
* `GET /pacientes/meus-agendamentos/`: Retorna os agendamentos ativos (não cancelados e futuros) de um paciente, buscando por e-mail.

Você pode testar esses endpoints via `http://localhost:8000/docs` ou importando o arquivo `postman.json` no seu Postman.

### n8n (Chatbot)

O workflow do n8n (`export_n8n.json`) define o fluxo de conversação:

1.  **Recepção:** O nó `When chat message received` aguarda a mensagem do usuário.
2.  **Verificação de Áudio:** Um `If` verifica se a mensagem é um áudio. Se sim, o nó `Transcribe a recording` (Gemini) a transforma em texto.
3.  **Memória:** O sistema verifica se é a primeira interação do usuário (`If2`).
    * **Novo Usuário:** Pede nome e e-mail (`Respond to Chat1`, `Respond to Chat2`), chama o endpoint `POST /pacientes/` para criar/obter o ID do paciente, e salva `email`, `nome` e `id` na memória da sessão (`Chat Memory Manager`).
    * **Usuário Recorrente:** Recupera os dados da sessão (`Chat Memory Manager2`).
4.  **Roteamento de Intenção:** A mensagem do usuário (texto ou áudio transcrito) é enviada ao nó `Message a model` (Gemini) junto com uma lista de "Tools" (ferramentas). O Gemini decide qual ferramenta chamar, retornando o nome da ação (ex: `agendar_consulta`, `cancelar_consulta_ja_marcada`).
5.  **Execução da Ação:** Um nó `Switch` direciona o fluxo com base na resposta do Gemini:
    * **Consultar Horários:** Chama `GET /horarios`, formata o JSON com o Gemini e exibe ao usuário.
    * **Agendar:** Inicia o fluxo de agendamento (que pede o ID do slot) e chama `POST /agendar`.
    * **Cancelar:** Chama `GET /pacientes/meus-agendamentos/`, mostra os agendamentos, pede o ID para cancelamento e chama `POST /cancelar/{id}`.
    * **Pagamento:** Chama `GET /pagamento` e exibe as informações.
6.  **Notificação:** Para agendamentos e cancelamentos, o workflow envia um e-mail de confirmação formatado em HTML (também gerado pelo Gemini) para o e-mail do paciente armazenado na memória.

## Sobre os Testes

Os testes unitários garantem a qualidade e a lógica da API.

* **Execução:** Para rodar os testes, use o comando `pytest` na raiz do projeto.
* **Isolamento:** Os testes usam um banco de dados SQLite `:memory:` (em memória), garantindo que não haja interferência com o banco `med_agenda.db` de desenvolvimento.
* **Relatório de Depuração:** O arquivo `api/tests/Relatório teste unitário.pdf` documenta um importante processo de depuração relacionado a um erro de `TypeError` (comparação de datetimes `offset-naive` e `offset-aware` entre o Python e o SQLite). A solução adotada foi padronizar toda a aplicação para usar o padrão "Naive-UTC", utilizando `datetime.utcnow()`.