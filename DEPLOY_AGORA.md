# 🚀 Deploy AGORA - Passo a Passo Final

## ✅ Status: TUDO CONFIGURADO!

Todas as credenciais já estão no arquivo `.env`:
- ✅ Evolution API (pictorial.cloud)
- ✅ PostgreSQL (Render)
- ✅ Notion API + Database ID
- ✅ OpenAI API Key (GPT5-NANO)

## 📋 Checklist Rápido

- [x] Código criado
- [x] Credenciais configuradas
- [x] .env completo
- [ ] Git push
- [ ] Deploy no Render
- [ ] Configurar webhook

---

## 1️⃣ Git Push (2 minutos)

```bash
# Inicializar Git
git init

# Adicionar arquivos
git add .

# Commit
git commit -m "Agente Pangeia - Versão completa com todas as credenciais"

# Configurar remote
git branch -M main
git remote add origin https://github.com/estevaoantuness/agentefinal.git

# Push
git push -u origin main
```

---

## 2️⃣ Deploy no Render (3 minutos)

### A. Criar Web Service

1. Acesse: https://dashboard.render.com
2. Clique: **New +** → **Web Service**
3. Conecte o repositório: `estevaoantuness/agentefinal`

### B. Configurar Service

**Name:**
```
pangeia-agent
```

**Environment:**
```
Python 3
```

**Region:**
```
Oregon (US West)
```

**Branch:**
```
main
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### C. Adicionar Environment Variables

Cole estas variáveis (arquivo `CREDENCIAIS_RENDER.txt` tem todas):

```env
DATABASE_URL=postgresql://post_pangeia_user:yblhBhZz3n15SY6kikdYT5SbAekGky26@dpg-d44ll7q4d50c73ejkfrg-a.oregon-postgres.render.com/post_pangeia

EVOLUTION_API_URL=https://evo.pictorial.cloud

EVOLUTION_API_KEY=7LjVQc6PJJFFgzy14pzH90QffOOus0z2

EVOLUTION_INSTANCE_NAME=pangeia_bot

NOTION_API_KEY=[VEJA_SEU_ARQUIVO_.env]

NOTION_DATABASE_ID=2f0e465754d444c88ee493ca30b1ea36

OPENAI_API_KEY=[VEJA_SEU_ARQUIVO_.env]

OPENAI_MODEL=gpt5-nano

APP_HOST=0.0.0.0

DEBUG=False

LOG_LEVEL=INFO

TIMEZONE=America/Sao_Paulo
```

### D. Deploy

1. Clique em **Create Web Service**
2. Aguarde o build (3-5 minutos)
3. Anote a URL: `https://pangeia-agent.onrender.com` (ou similar)

---

## 3️⃣ Configurar Webhook Evolution (1 minuto)

### A. Acessar Manager
```
https://evo.pictorial.cloud/manager/
```

### B. Configurar Webhook

No painel do Evolution, configure:

**Webhook URL:**
```
https://SUA-URL-DO-RENDER.onrender.com/webhook/evolution
```

**Webhook Events:** Selecione
- ✅ MESSAGES_UPSERT
- ✅ MESSAGES_UPDATE
- ✅ SEND_MESSAGE

---

## 4️⃣ Testar (1 minuto)

### A. Health Check

Abra no navegador:
```
https://SUA-URL-DO-RENDER.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "pangeia_agent"
}
```

### B. Teste WhatsApp

Envie uma mensagem para o número conectado na Evolution:
```
Olá!
```

O agente deve responder!

### C. Teste de Tarefa

```
Cria uma tarefa de testar o sistema para hoje
```

O agente deve:
1. Criar a tarefa
2. Salvar no PostgreSQL
3. Sincronizar com Notion
4. Responder com confirmação

---

## 🎉 PRONTO!

Seu agente está no ar!

### Comandos para testar:

```
# Criar tarefas
"Cria uma tarefa de revisar relatório para amanhã"
"Nova tarefa: ligar para o cliente"

# Listar
"Minhas tarefas"
"Tarefas pendentes"

# Atualizar
"Marca tarefa 1 como completa"

# Lembretes
"Me lembra de fazer backup em 2 horas"
```

---

## 🆘 Troubleshooting

### Deploy falhou?
- Verifique os logs no Render Dashboard
- Confirme que todas as env vars estão configuradas

### Webhook não funciona?
- Teste: `https://sua-url.onrender.com/webhook/test`
- Verifique se configurou corretamente no Evolution Manager

### Agent não responde?
- Verifique logs no Render
- Teste OpenAI API Key: pode ter expirado

### Notion não sincroniza?
- Confirme que compartilhou o database com a integração
- Verifique o Database ID

---

## 📞 Links Úteis

- **Render Dashboard:** https://dashboard.render.com
- **Evolution Manager:** https://evo.pictorial.cloud/manager/
- **Notion Database:** https://www.notion.so/2f0e465754d444c88ee493ca30b1ea36
- **Logs do Render:** Dashboard → Logs tab

---

**Boa sorte! 🚀**
