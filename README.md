# Agente Gestor de Tarefas Pangeia

Agente inteligente de gestão de tarefas integrado ao WhatsApp via Evolution API, com sincronização bidirecional com Notion e lembretes automáticos.

## 🚀 Funcionalidades

- ✅ **CRUD de Tarefas**: Criar, listar, atualizar e completar tarefas via WhatsApp
- 🤖 **IA Conversacional**: Processamento de linguagem natural com LangChain
- 📱 **WhatsApp Integration**: Via Evolution API
- 📊 **Notion Sync**: Sincronização bidirecional com banco de dados Notion
- ⏰ **Lembretes Automáticos**: Sistema de agendamento inteligente
- 💾 **PostgreSQL**: Persistência robusta de dados

## 🛠️ Stack Técnica

- **Python 3.11+**
- **FastAPI** - Framework web assíncrono
- **LangChain** - Framework de IA
- **SQLAlchemy** - ORM
- **PostgreSQL** - Banco de dados
- **Evolution API** - WhatsApp
- **Notion API** - Sincronização
- **APScheduler** - Agendamento de tarefas
- **Docker** - Containerização

## 📦 Instalação

### Opção 1: Deploy no Render (Recomendado)

O projeto já está 100% configurado! Veja o arquivo **`DEPLOY_AGORA.md`** para instruções passo a passo.

Resumo rápido:
```bash
# 1. Push para GitHub
git init
git add .
git commit -m "Deploy Agente Pangeia"
git push origin main

# 2. Criar Web Service no Render
# 3. Adicionar variáveis de ambiente (ver CREDENCIAIS_RENDER.txt)
# 4. Deploy!
```

### Opção 2: Com Docker (Local)

```bash
# Clone o repositório
git clone https://github.com/estevaoantuness/agentefinal.git
cd agente_pangeia_final

# As variáveis já estão configuradas no .env!

# Inicie os containers
docker-compose up -d
```

### Instalação Local

```bash
# Crie um ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env

# Inicialize o banco de dados
python scripts/init_db.py

# Inicie a aplicação
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Configuração

### Evolution API

1. Acesse o Evolution API Manager:
   ```
   https://evo.pictorial.cloud/manager/
   ```

2. Configure o webhook apontando para:
   ```
   https://seu-app-render.onrender.com/webhook/evolution
   ```

3. As credenciais já estão configuradas no `.env`!

### Notion

O database já está configurado! Apenas certifique-se de que está compartilhado com a integração.

**URL do Database:**
```
https://www.notion.so/2f0e465754d444c88ee493ca30b1ea36
```

**Database ID:** `2f0e465754d444c88ee493ca30b1ea36` (já no `.env`)

## 📝 Uso

### Comandos via WhatsApp

```
# Criar tarefa
"Cria uma tarefa de revisar relatório para amanhã"

# Listar tarefas
"Quais são minhas tarefas pendentes?"
"Me mostra as tarefas de hoje"

# Atualizar tarefa
"Marca a tarefa de revisar relatório como completa"
"Atualiza o prazo da tarefa X para sexta-feira"

# Lembretes
"Me lembra de ligar pro cliente em 2 horas"
```

## 🏗️ Estrutura do Projeto

```
agente_pangeia_final/
├── src/
│   ├── main.py                    # FastAPI app
│   ├── config/                    # Configurações
│   ├── database/                  # Modelos SQLAlchemy
│   ├── agent/                     # LangChain agent
│   ├── integrations/              # Evolution + Notion
│   ├── api/                       # Webhooks
│   └── utils/                     # Utilidades
├── tests/                         # Testes
├── scripts/                       # Scripts utilitários
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🧪 Testes

```bash
pytest tests/ -v --cov=src
```

## 📄 Licença

MIT

## 👥 Equipe Pangeia

Desenvolvido para otimizar a gestão de tarefas da equipe Pangeia.
