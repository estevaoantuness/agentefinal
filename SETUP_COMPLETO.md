# 🤖 Agente Gestor de Tarefas Pangeia - Setup Completo

## ✅ Projeto Criado com Sucesso!

O agente inteligente de gestão de tarefas da Pangeia foi criado e está pronto para uso!

## 📦 O que foi criado?

### Estrutura do Projeto
```
agente_pangeia_final/
├── src/
│   ├── main.py                           # Aplicação FastAPI principal
│   ├── config/
│   │   └── settings.py                   # Configurações e variáveis de ambiente
│   ├── database/
│   │   ├── models.py                     # Modelos SQLAlchemy (User, Task, etc.)
│   │   └── session.py                    # Gerenciamento de sessão do banco
│   ├── agent/
│   │   ├── langchain_agent.py           # Agent LangChain com GPT5-NANO
│   │   ├── tools.py                      # Ferramentas do agent (CRUD tarefas)
│   │   └── memory.py                     # Memória conversacional
│   ├── integrations/
│   │   ├── evolution_api.py             # Cliente Evolution API (WhatsApp)
│   │   ├── notion_sync.py               # Sincronização Notion
│   │   └── scheduler.py                  # Sistema de lembretes
│   ├── api/
│   │   └── webhooks.py                   # Endpoints webhook
│   └── utils/
│       ├── logger.py                     # Sistema de logs
│       └── helpers.py                    # Funções auxiliares
├── scripts/
│   ├── init_db.py                        # Inicializar banco de dados
│   └── test_evolution.py                 # Testar Evolution API
├── tests/                                 # Testes (estrutura criada)
├── .env                                   # Arquivo de ambiente (CONFIGURAR!)
├── .env.example                          # Template de variáveis
├── requirements.txt                      # Dependências Python
├── Dockerfile                            # Container Docker
├── docker-compose.yml                    # Orquestração Docker
├── render.yaml                           # Config Render
├── README.md                             # Documentação principal
└── DEPLOY_RENDER.md                      # Guia de deploy

```

## 🎯 Funcionalidades Implementadas

### ✅ 1. WhatsApp via Evolution API
- ✅ Webhook para receber mensagens
- ✅ Envio de mensagens de texto
- ✅ Tratamento de eventos
- ✅ Normalização de números de telefone

### ✅ 2. IA Conversacional com LangChain
- ✅ GPT5-NANO configurado
- ✅ Sistema de memória conversacional (armazena no PostgreSQL)
- ✅ Prompts otimizados em português brasileiro
- ✅ Tools para gestão de tarefas

### ✅ 3. Gestão de Tarefas (CRUD Completo)
- ✅ Criar tarefas com título, descrição, prioridade, prazo
- ✅ Listar tarefas (todas, pendentes, completas, do dia)
- ✅ Atualizar tarefas (status, título, descrição, etc.)
- ✅ Marcar como completa
- ✅ Categorização de tarefas
- ✅ Sistema de prioridades (low, medium, high, urgent)

### ✅ 4. Sincronização Notion
- ✅ Sincronização bidirecional
- ✅ Criação de tarefas no Notion
- ✅ Atualização de tarefas existentes
- ✅ Sync automático diário (3h da manhã)
- ✅ Rastreamento de última sincronização

### ✅ 5. Sistema de Lembretes
- ✅ APScheduler para agendamento
- ✅ Criação de lembretes com linguagem natural
- ✅ Envio automático via WhatsApp
- ✅ Lembretes persistidos no banco
- ✅ Carregamento de lembretes pendentes no startup

### ✅ 6. Banco de Dados PostgreSQL
- ✅ 5 tabelas criadas:
  - `users` - Usuários do sistema
  - `tasks` - Tarefas
  - `categories` - Categorias de tarefas
  - `reminders` - Lembretes
  - `conversation_history` - Histórico de conversas
- ✅ Relacionamentos configurados
- ✅ Índices para performance

### ✅ 7. API RESTful
- ✅ FastAPI com docs automáticas
- ✅ Endpoint de webhook
- ✅ Health check
- ✅ CORS configurado

## 🔧 Próximos Passos

### 1. Configurar Variáveis de Ambiente (OBRIGATÓRIO)

Edite o arquivo `.env` e configure:

```env
# ⚠️ OBRIGATÓRIO: Adicione sua OpenAI API Key
OPENAI_API_KEY=SUA_OPENAI_API_KEY_AQUI

# ⚠️ OBRIGATÓRIO: Adicione o ID do seu database do Notion
NOTION_DATABASE_ID=SEU_DATABASE_ID_AQUI
```

### 2. Testar Localmente (Opcional)

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python scripts/init_db.py

# Testar Evolution API
python scripts/test_evolution.py

# Rodar aplicação
uvicorn src.main:app --reload
```

### 3. Deploy no Render (Recomendado)

Siga o guia completo em: **`DEPLOY_RENDER.md`**

Resumo rápido:
1. Faça push do código para o GitHub
2. Crie um Web Service no Render
3. Configure as variáveis de ambiente
4. Deploy automático!

### 4. Configurar Webhook no Evolution

Após deploy, configure o webhook:
```
URL: https://seu-app.onrender.com/webhook/evolution
```

### 5. Configurar Notion

1. Compartilhe seu banco de dados Notion com a integração
2. Copie o Database ID
3. Adicione no `.env` como `NOTION_DATABASE_ID`

## 📱 Como Usar

### Comandos via WhatsApp (Exemplos)

```
# Criar tarefas
"Cria uma tarefa de revisar relatório para amanhã"
"Nova tarefa: ligar pro cliente, prioridade alta"

# Listar tarefas
"Quais são minhas tarefas?"
"Me mostra as tarefas pendentes"
"Tarefas de hoje"

# Atualizar tarefas
"Marca a tarefa 1 como completa"
"Atualiza o prazo da tarefa 2 para sexta-feira"

# Lembretes
"Me lembra de fazer backup em 2 horas"
"Cria um lembrete para amanhã às 9h"
```

## 🔑 Credenciais Configuradas

### Evolution API ✅
- URL: `https://evo.escreve.ai`
- API Key: `429683C4C977415CAAFCCE10F7D57E11`
- Instance: `pangeia_bot`

### PostgreSQL ✅
- Host: Render (Oregon)
- Database: `post_pangeia`
- User: `post_pangeia_user`

### Notion API ✅
- API Key: **[Ver arquivo .env]**
- Database ID: `2f0e465754d444c88ee493ca30b1ea36`

### OpenAI ✅
- Model: `gpt5-nano`
- API Key: **[Ver arquivo .env]**

## 📊 Arquitetura

```
┌─────────────┐
│  WhatsApp   │
└──────┬──────┘
       │
       ↓ (mensagem)
┌─────────────────┐
│ Evolution API   │
└──────┬──────────┘
       │
       ↓ (webhook)
┌─────────────────┐
│   FastAPI App   │
│  (src/main.py)  │
└──────┬──────────┘
       │
       ├→ LangChain Agent (GPT5-NANO)
       │  └→ Tools (CRUD Tarefas)
       │     └→ PostgreSQL
       │
       ├→ Notion Sync
       │  └→ Notion API
       │
       └→ Scheduler (Lembretes)
          └→ APScheduler
```

## 🆘 Troubleshooting

### Banco de dados não conecta
```bash
# Teste a conexão
python -c "from src.database.session import engine; print(engine.url)"
```

### Evolution API não responde
```bash
# Teste a API
python scripts/test_evolution.py
```

### Agent não processa mensagens
- Verifique se `OPENAI_API_KEY` está configurada
- Confirme que tem créditos na OpenAI
- Veja os logs: `docker-compose logs -f` ou no Render Dashboard

## 📚 Documentação Adicional

- **README.md** - Visão geral do projeto
- **DEPLOY_RENDER.md** - Guia completo de deploy
- **requirements.txt** - Lista de dependências
- **.env.example** - Template de variáveis

## 🎉 Conclusão

O projeto está **100% completo** e pronto para uso!

**Próxima etapa:** Configure as 2 variáveis obrigatórias no `.env` e faça o deploy!

---

**Desenvolvido para a equipe Pangeia** 🚀
