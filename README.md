# Projeto: Automação de Agendamento Médico com n8n e FastAPI

Este projeto implementa um sistema completo de agendamento médico, composto por uma API back-end robusta construída com FastAPI e um chatbot inteligente para atendimento ao cliente, orquestrado pelo n8n e potencializado pelo Google Gemini.

O sistema permite que pacientes consultem horários disponíveis, agendem consultas, cancelem agendamentos e obtenham informações, tudo através de uma interface de chat. O back-end gerencia médicos, pacientes, horários (slots) e agendamentos, com uma camada de cache em Redis para otimização de performance.

---

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

---

## Tecnologias Utilizadas

| Categoria | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Back-end** | **Python 3.10+** | Linguagem principal da API. |
|  | **FastAPI** | Framework web moderno para construção da API. |
|  | **SQLAlchemy** | ORM para interação com o banco de dados. |
|  | **Pydantic** | Validação de dados de entrada/saída (schemas). |
|  | **SQLite** | Banco de dados relacional (arquivo `med_agenda.db`). |
| **Automação** | **n8n** | Plataforma de automação (low-code) que orquestra o fluxo do chatbot. |
|  | **Google Gemini** | LLM usado para roteamento de intenção, transcrição de áudio e formatação de respostas. |
| **Infraestrutura** | **Docker / Docker Compose** | Contenização dos serviços de n8n, Redis e Metabase. |
| **Cache** | **Redis** | Banco de dados em memória usado para cache de horários. |
| **BI** | **Metabase** | Ferramenta de Business Intelligence para visualização dos dados. |
| **Testes** | **Pytest** | Framework de testes para a API. |

---

## Arquitetura da Solução

O sistema é desenhado com uma arquitetura desacoplada:

1. **Serviços em Docker:**  
   O `docker-compose.yml` gerencia os serviços de suporte:
   * `n8n`: (Porta `5678`) Executa o workflow do chatbot.  
   * `redis`: (Porta `6379`) Fornece o cache.  
   * `metabase`: (Porta `3000`) Fornece a plataforma de BI.

2. **API Local (Host):**  
   A API FastAPI é executada diretamente na máquina host (fora do Docker) na porta `8000`.

3. **Comunicação:**  
   O workflow do n8n (que está em um contêiner) se comunica com a API na máquina host usando o endereço especial `http://host.docker.internal:8000`.

---

## Instalação e Execução (Passo a Passo)

### Pré-requisitos

* Git  
* Python 3.10+  
* Docker  
* Docker Compose  

---

### 1. Clonar o Repositório

```bash
git clone https://github.com/patrickbatista42/n8n_automatization
cd n8n_automatization
```

---

### 2. Iniciar Serviços de Suporte (Docker)

Execute o Docker Compose para iniciar o n8n, Redis e Metabase em segundo plano:

```bash
docker-compose up -d --build
```

Após a execução, os serviços estarão acessíveis nos seguintes endereços:

* **n8n:** `http://localhost:5678`  
* **Metabase:** `http://localhost:3000`  
* **Redis:** `localhost:6379`  

---

### 3. Configurar e Executar a API (Local)

A API FastAPI será executada localmente na sua máquina.

#### 3.1 Criar ambiente virtual

```bash
python -m venv venv
```

#### 3.2 Ativar ambiente virtual

* **Windows:**
  ```bash
  .\venv\Scripts\activate
  ```
* **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

#### 3.3 Criar arquivo `requirements.txt`

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

#### 3.4 Instalar dependências

```bash
pip install -r requirements.txt
```

#### 3.5 Popular o banco de dados (primeira execução)

```bash
python -m api.seed
```

#### 3.6 Executar a API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

A API estará acessível em `http://localhost:8000` e a documentação em `/docs`.

---

### 4. Configurar o n8n

1. Acesse `http://localhost:5678`  
2. Crie um novo workflow ou importe o existente:
   * Vá em **Import > From File**
   * Selecione `export_n8n.json`
3. Configure as credenciais:
   * `"Google Gemini(PaLM) Api"`
   * `"Gmail OAuth2"`
4. Associe as credenciais nos nós do **Gemini** e **Gmail**.  
5. Ative o workflow clicando em **Active**.  
6. Copie a **URL do Webhook de chat** e acesse-a no navegador para conversar com o chatbot.

---

### 5. (Opcional) Configurar o Metabase

1. Acesse `http://localhost:3000`  
2. Faça a configuração inicial (criar conta de admin).  
3. Adicione o banco de dados SQLite:  
   ```
   /metabase-data/med_agenda.db
   ```
4. Salve e crie dashboards.

---

## Utilização

### API (FastAPI)

* `GET /` — Verifica o status da API.  
* `GET /horarios` — Retorna horários disponíveis.  
* `POST /agendar` — Agenda uma consulta.  
* `POST /cancelar/{appointment_id}` — Cancela um agendamento.  
* `GET /pagamento` — Retorna informações de pagamento.  
* `POST /pacientes/` — Cria ou obtém paciente por e-mail.  
* `GET /pacientes/meus-agendamentos/` — Lista agendamentos ativos.  

---

### Chatbot (n8n)

#### 1. Recepção
O nó **Trigger**: recebe mensagem e aguarda a mensagem do usuário.

#### 2. Verificação de Áudio
O nó **If** verifica se a mensagem é um áudio.  
Se sim, o nó **Transcreve o áudio (Gemini)** converte para texto.  
Ambas as saídas são unificadas no nó **Merge**.

#### 3. Roteamento de Intenção
A mensagem do usuário é enviada ao nó **Message a model (Gemini)** junto com as **Tools**.  
O Gemini retorna a ação (`agendar_consulta`, `cancelar_consulta_ja_marcada`, etc.).

#### 4. Verificação de Memória
Verifica se há mensagens salvas na sessão (**nó If**).

#### 5. Novo Usuário
Solicita **nome** e **e-mail**, chama `POST /pacientes`, e salva dados na memória da sessão.

#### 6. Usuário Recorrente
Recupera dados da sessão (ramificação false do If).

#### 7. Execução da Ação

##### 7.1 consultar_agenda_horarios_disponiveis
`GET /horarios` → Exibe horários disponíveis.

##### 7.2 agendar_consulta
`GET /horarios` → Exibe slots.  
Usuário escolhe ID → `POST /agendar`.

##### 7.3 cancelar_consulta_ja_marcada
`GET /pacientes/meus-agendamentos/` → Exibe agendamentos.  
Usuário escolhe ID → `POST /cancelar/{id}`.

##### 7.4 consultar_informacoes_pagamento
`GET /pagamento` → Exibe informações de pagamento.

#### 8. Notificação
Após agendamento ou cancelamento, o Gemini gera um HTML e envia e-mail de confirmação ao paciente.

---

## Sobre os Testes

Os testes unitários garantem a qualidade e a lógica da API.

* **Execução:**  
  ```bash
  pytest
  ```
* **Isolamento:**  
  Usa banco SQLite `:memory:` para evitar interferência com `med_agenda.db`.  
* **Depuração:**  
  Documentada no arquivo `api/tests/Relatório teste unitário.pdf`, com a correção do erro `TypeError` (comparação de datetimes `offset-naive` e `offset-aware`) padronizada para `datetime.utcnow()`.

---
