# MVP ROADMAP - Pangeia Bot

**Objetivo:** Deploy funcional do bot no Render em menos de 24 horas

**Data:** 05 de Novembro de 2025

---

## ANÁLISE DO PROJETO ATUAL

### ✅ O que JÁ EXISTE (Pronto para MVP)

**Backend (100% completo):**
- FastAPI app com estrutura production-ready
- Webhook handler para Evolution API (WhatsApp)
- Database models (User, Task, Category, Reminder) com SQLAlchemy
- LangChain agent integrado com OpenAI
- Notion sync integration
- APScheduler para reminders
- Settings configuráveis por env vars
- Health check endpoint `/health`
- Proper exception handling e logging

**Integrations:**
- Evolution API client (WhatsApp)
- Notion API client
- LangChain + OpenAI
- PostgreSQL database

**Build & Deploy:**
- `build.sh` script configurado
- `requirements.txt` com todas as dependências
- Ready para Render

### ❌ O que ESTÁ QUEBRADO (MVP Blockers)

**1. OPENAI_MODEL no settings.py (Line 24)**
   - Está: `gpt-4-turbo-preview`
   - Deveria ser: `gpt5-nano` (conforme env)
   - **Problema:** Model não existe, vai falhar no deploy
   - **Impacto:** 🔴 CRÍTICO - Bot não funciona

**2. Agent tools não têm implementação completa (agent/tools.py)**
   - Faltam funções para CRUD de tasks
   - Faltam funções de reminder
   - **Problema:** Agent não pode executar ações
   - **Impacto:** 🔴 CRÍTICO - Agent retorna erro

**3. Missing ConversationHistory import (database/session.py:62)**
   - Já foi corrigido no commit anterior
   - Verificar se está OK
   - **Impacto:** 🟡 MÉDIO - Memory pode falhar

**4. Database initialization pode falhar**
   - `init_db()` cria tabelas sem validar conexão prévia
   - Se PostgreSQL não tiver schemas criados, falha
   - **Impacto:** 🟡 MÉDIO - Database não inicializa

**5. Missing evolution_api.py implementation**
   - Precisa de `send_text_message()` funcionando
   - Precisa de client initialization
   - **Impacto:** 🔴 CRÍTICO - Não envia resposta ao user

---

## MVP SCOPE (Minimum Viable Product)

### Core User Flow:
```
1. Usuário envia mensagem WhatsApp
2. Webhook Evolution recebe mensagem
3. LangChain agent processa (com ou sem Notion)
4. Bot responde via WhatsApp
5. (Opcional) Tarefa salva no banco de dados
```

### MVP não precisa de:
- ❌ Notion sync (pode ser removido inicialmente)
- ❌ Reminders/scheduler (pode ser desativado)
- ❌ Categories (pode ser default)
- ❌ UI/Frontend
- ❌ Multiple users (pode funcionar com 1 user)

### MVP PRECISA de:
- ✅ WhatsApp webhook funcionando
- ✅ AI response via LangChain/OpenAI
- ✅ Message processing sem erros
- ✅ Health check `/health` retornando 200
- ✅ Environment variables configuradas

---

## IMPLEMENTATION PLAN (4 FASES)

### FASE 1: Fix Critical Issues (30 min)

#### 1.1 Fix OPENAI_MODEL na settings.py
```python
# Mudar de:
OPENAI_MODEL: str = "gpt-4-turbo-preview"

# Para:
OPENAI_MODEL: str = "gpt-3.5-turbo"  # Mais barato e rápido para MVP
```

#### 1.2 Implement Evolution API client
```python
# src/integrations/evolution_api.py
- Implementar `send_text_message(phone_number, message)`
- Validar connection com EVOLUTION_API_URL
- Handle erros de API
```

#### 1.3 Implement basic agent tools
```python
# src/agent/tools.py
- create_task(title, description, priority)
- list_tasks(user_id)
- update_task(task_id, status)
- get_task_summary(user_id)
```

### FASE 2: Database Setup (15 min)

#### 2.1 Create Render PostgreSQL
- Access Render Dashboard
- Create PostgreSQL database
- Copy CONNECTION STRING to DATABASE_URL

#### 2.2 Initialize Database
```bash
# Local test first
python -m src.database.session

# Or via Render environment setup
```

### FASE 3: Render Deployment (20 min)

#### 3.1 Configure Render Web Service
- Name: `pangeia-bot-final`
- Repository: `agente_pangeia_final`
- Build Command: `chmod +x build.sh && ./build.sh`
- Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- Plan: Starter (free)

#### 3.2 Add Environment Variables
```
DATABASE_URL = [Render PostgreSQL Connection String]
EVOLUTION_API_URL = https://evo.pictorial.cloud
EVOLUTION_API_KEY = [Seu API Key]
EVOLUTION_INSTANCE_NAME = Pangeia Bot
NOTION_API_KEY = [Seu API Key]
NOTION_DATABASE_ID = [Seu Database ID]
OPENAI_API_KEY = [Seu API Key]
OPENAI_MODEL = gpt-3.5-turbo
APP_HOST = 0.0.0.0
DEBUG = False
LOG_LEVEL = INFO
TIMEZONE = America/Sao_Paulo
```

### FASE 4: Testing & Validation (15 min)

#### 4.1 Health Check
```bash
curl https://seu-servico.onrender.com/health

# Esperado:
# {"status": "healthy", "service": "pangeia_agent"}
```

#### 4.2 WhatsApp Test
- Send message via WhatsApp
- Wait for response
- Check Render logs for errors

#### 4.3 Validate Logs
- No 500 errors
- No import errors
- Clean startup messages

---

## QUICK CHECKLIST

### Before Deploy:
- [ ] OPENAI_MODEL changed to gpt-3.5-turbo
- [ ] Evolution API client implemented
- [ ] Agent tools implemented (minimal CRUD)
- [ ] All env vars in settings.py
- [ ] build.sh is executable
- [ ] requirements.txt reviewed
- [ ] No import errors (test locally)

### During Deploy:
- [ ] Service created on Render
- [ ] All 12 environment variables set
- [ ] Build completes without errors
- [ ] App starts successfully (check logs)
- [ ] Health check returns 200

### After Deploy:
- [ ] /health endpoint works
- [ ] WhatsApp messages are received
- [ ] Bot responds with AI message
- [ ] No errors in Render logs
- [ ] Database queries work (if testing tasks)

---

## FILES TO MODIFY

1. **src/config/settings.py** (line 24)
   - Fix OPENAI_MODEL default value

2. **src/integrations/evolution_api.py**
   - Implement `send_text_message()` method
   - Implement client initialization

3. **src/agent/tools.py**
   - Implement create_task tool
   - Implement list_tasks tool
   - Implement update_task tool

4. **src/database/session.py**
   - Verify ConversationHistory import (should be OK)
   - Add error handling to init_db()

5. **src/agent/langchain_agent.py**
   - Verify imports and tool binding

---

## TIMELINE

```
00:00 - START
05:00 - Fix settings.py OPENAI_MODEL
10:00 - Implement Evolution API send_text_message
20:00 - Implement agent tools (basic CRUD)
30:00 - Create Render PostgreSQL
45:00 - Setup Render Web Service
50:00 - Add environment variables
55:00 - First build attempt
60:00 - Fix build errors if any
70:00 - Health check test
75:00 - WhatsApp test
80:00 - Validate final MVP
```

---

## SUCCESS CRITERIA

✅ **MVP is ready when:**
1. Service deployed on Render without errors
2. `/health` returns 200 status
3. WhatsApp message received by webhook
4. LangChain agent processes message
5. Response sent back via Evolution API
6. No critical errors in Render logs

✅ **MVP is NOT ready if:**
1. 502 Bad Gateway errors
2. Import errors in logs
3. Environment variable errors
4. API connection failures
5. Database initialization fails

---

## NEXT STEPS AFTER MVP

Once MVP is live (Phase 1-4 complete):
1. Add Notion sync back
2. Enable reminder scheduler
3. Add task persistence
4. Improve agent prompts
5. Add error handling
6. Monitor performance

---

## REFERENCE LINKS

- Render Dashboard: https://dashboard.render.com
- Evolution API Docs: https://evo.pictorial.cloud
- OpenAI Models: https://platform.openai.com/docs/models
- Notion API: https://developers.notion.com/

---

**Status:** Ready to implement
**Priority:** 🔴 CRÍTICA
**Estimated Time:** 80 minutes total
