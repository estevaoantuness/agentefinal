# 🐳 PANGEIA BOT - LOCAL DOCKER SETUP

## Início Rápido

### Pré-requisitos
- Docker instalado: https://www.docker.com/products/docker-desktop
- Git configurado
- Credenciais do .env atualizadas

### 1. Iniciar os Containers

```bash
# Navigate to project
cd /Users/estevaoantunes/agente_pangeia_final

# Build and start containers
docker-compose up --build

# Expect output like:
# - pangeia_agent started on 0.0.0.0:8000
# - pangeia_db_local running on port 5432
```

### 2. Inicializar Database

Em outro terminal:

```bash
# Initialize database tables
docker-compose exec app python -c "from src.database.session import init_db; init_db()"

# Expected output:
# Database initialized
```

### 3. Testar Health Check

```bash
# Test the API is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "service": "pangeia_agent"}
```

---

## 🧪 Teste de Funcionalidades

### Simular Webhook WhatsApp

```bash
# Create test_webhook.sh
cat > test_webhook.sh << 'EOF'
#!/bin/bash

# Test view_tasks function
curl -X POST http://localhost:8000/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false
      },
      "message": {
        "conversation": "minhas tarefas"
      },
      "pushName": "Usuário Teste"
    }
  }' | jq .

echo "---"

# Test create_task function
curl -X POST http://localhost:8000/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false
      },
      "message": {
        "conversation": "criar tarefa: reunião com cliente amanhã"
      },
      "pushName": "Usuário Teste"
    }
  }' | jq .

EOF

chmod +x test_webhook.sh
./test_webhook.sh
```

### Ver Logs em Tempo Real

```bash
# Follow app logs
docker-compose logs -f app

# Follow database logs
docker-compose logs -f db

# Follow all
docker-compose logs -f
```

### Acessar Database PostgreSQL

```bash
# Connect to database
docker-compose exec db psql -U pangeia -d pangeia_tasks

# Useful commands:
# \dt                 -- List tables
# SELECT * FROM users; -- View users
# SELECT * FROM tasks; -- View tasks
# \q                  -- Quit
```

---

## 🔧 Troubleshooting

### Container não inicia

```bash
# Check logs
docker-compose logs app

# Rebuild containers
docker-compose down
docker-compose up --build

# Check if port 8000 is in use
lsof -i :8000
```

### Database connection error

```bash
# Check database is running
docker-compose exec db pg_isready -U pangeia

# Reset database
docker-compose down -v  # Remove volumes
docker-compose up --build
docker-compose exec app python -c "from src.database.session import init_db; init_db()"
```

### OpenAI API error

```bash
# Check OPENAI_API_KEY in .env
grep OPENAI_API_KEY .env

# Verify key format starts with sk-proj-
# Check in logs for specific error

# View app logs
docker-compose logs -f app
```

### Module import errors

```bash
# Rebuild to reinstall dependencies
docker-compose down
docker-compose up --build

# Or install locally for testing
pip install -r requirements.txt
python -c "from src.ai.openai_client import OpenAIClient; print('OK')"
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│         WhatsApp (Evolution API)             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   FastAPI Webhook    │
        │  /webhook/evolution  │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    OpenAI Client     │
        │  (GPT-4o-mini)       │
        │ + Function Calling   │
        └──────────┬───────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
    ┌─────────┐          ┌──────────┐
    │ Function │          │ Response │
    │ Executor │          │ (Natural)│
    └────┬────┘          └────┬─────┘
         │                    │
         ▼                    │
    ┌─────────────────┐       │
    │  PostgreSQL     │       │
    │   Database      │       │
    │ (User, Tasks)   │       │
    └─────────────────┘       │
                              ▼
                    ┌──────────────────┐
                    │  Send via Evo    │
                    │  Back to WhatsApp│
                    └──────────────────┘
```

---

## ✅ Validation Checklist

- [ ] `docker-compose up --build` completes without errors
- [ ] Health check returns `{"status": "healthy", "service": "pangeia_agent"}`
- [ ] Database initializes successfully
- [ ] Can connect to PostgreSQL: `SELECT 1;` returns OK
- [ ] Can view app logs without import errors
- [ ] Can POST to webhook endpoint
- [ ] OpenAI API key is valid (no 401 errors)
- [ ] Functions execute without errors

---

## 🚀 Next Steps

Once local testing is complete:

1. Push to GitHub: `git push origin main`
2. Deploy to Render (see DEPLOY_AGORA.md)
3. Monitor logs in Render dashboard
4. Test with real WhatsApp messages

---

## 📞 Important Files

- `.env` - Configuration (local values)
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - App container definition
- `src/ai/` - OpenAI integration module
- `src/api/webhooks.py` - Webhook handler

---

**Happy testing!** 🎉
