# 🚀 Início Rápido - 5 Minutos

## Passo 1: Configure as Credenciais (2 min)

Edite o arquivo `.env` e adicione:

```env
# SUA OpenAI API Key
OPENAI_API_KEY=sk-proj-...

# SEU Notion Database ID
NOTION_DATABASE_ID=abc123...
```

## Passo 2: Deploy no Render (3 min)

### A. Crie o repositório no GitHub

```bash
git init
git add .
git commit -m "Agente Pangeia - Initial commit"
git branch -M main
git remote add origin https://github.com/estevaoantuness/agentefinal.git
git push -u origin main
```

### B. Deploy no Render

1. Acesse [render.com](https://render.com)
2. New + → Web Service
3. Conecte seu repositório
4. Configure:
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Adicione as variáveis do `.env` no Render
6. Deploy!

## Passo 3: Configure o Webhook

Após deploy, pegue a URL (ex: `https://pangeia-agent.onrender.com`)

Configure no Evolution API:
```
Webhook URL: https://pangeia-agent.onrender.com/webhook/evolution
```

## Passo 4: Teste!

Envie uma mensagem no WhatsApp:
```
Olá! Cria uma tarefa de testar o sistema
```

## ✅ Pronto!

Seu agente está funcionando! 🎉

---

## 📋 Comandos Úteis

### Criar Tarefas
- "Cria uma tarefa de [descrição] para [quando]"
- "Nova tarefa: [título]"

### Listar Tarefas
- "Minhas tarefas"
- "Tarefas pendentes"
- "Tarefas de hoje"

### Atualizar
- "Marca tarefa [número] como completa"
- "Atualiza tarefa [número]..."

### Lembretes
- "Me lembra de [fazer algo] em [tempo]"

---

**Dúvidas?** Veja `SETUP_COMPLETO.md` ou `DEPLOY_RENDER.md`
