# 🚀 Plano de Evolução: MVP → Produção
## Pangeia WhatsApp Task Manager

---

## 📊 Diagnóstico Atual

### ✅ O que funciona (MVP)
- WhatsApp bot com Evolution API
- Groq LLM (llama-3.1-8b-instant)
- 6 funções core: view/create/mark tasks, progress, help
- PostgreSQL com modelos robustos
- Docker deploy em Render free tier

### 🔧 O que está pronto mas DESATIVADO
- **Notion Sync completo** (bidirectional, 330 linhas de código)
- **Sistema de Reminders** (APScheduler, notificações WhatsApp)
- **Categories** (modelo DB pronto, não usado)
- **ConversationHistory** (modelo DB, não persiste no DB)
- **Scheduler** (daily sync às 3 AM configurado)

---

## 🎯 Plano de Evolução em 4 Fases

### **FASE 1: Ativação de Features Prontas** (2-3 dias)
**Objetivo:** Ativar o código existente que já está implementado

#### 1.1 Notion Sync (Alta Prioridade)
- [ ] Adicionar função `sync_notion` ao function_executor
- [ ] Criar comando "sincronizar notion" no system prompt
- [ ] Adicionar endpoint `/api/sync/notion` para sync manual
- [ ] Testar sync bidirecional
- [ ] Adicionar onboarding: "vincular notion" com coleta de token

**Arquivos:**
- `src/ai/function_executor.py` - adicionar métodos
- `src/ai/function_definitions.py` - definir schemas
- `src/integrations/notion_sync.py` - já existe!

#### 1.2 Sistema de Reminders (Alta Prioridade)
- [ ] Reativar scheduler no `main.py`
- [ ] Adicionar funções: `set_reminder(task_id, time)`, `list_reminders`
- [ ] Integrar com Groq: "me lembre em 1 hora"
- [ ] Carregar pending reminders no startup
- [ ] Testar envio de lembretes via WhatsApp

**Arquivos:**
- `src/main.py` - importar e iniciar ReminderScheduler
- `src/ai/function_executor.py` - adicionar set_reminder, cancel_reminder
- `src/integrations/scheduler.py` - já existe!

#### 1.3 Categories (Média Prioridade)
- [ ] Adicionar funções: `create_category`, `assign_category`
- [ ] Integrar ao Groq: "criar categoria Trabalho"
- [ ] Filtrar tasks por categoria
- [ ] Adicionar emoji/cor às categorias

---

### **FASE 2: Qualidade & Confiabilidade** (3-4 dias)
**Objetivo:** Tornar o sistema robusto e production-ready

#### 2.1 Tratamento de Erros
- [ ] Implementar retries com backoff exponencial (Groq/Evolution)
- [ ] Circuit breaker para serviços externos
- [ ] Fallback messages quando API falha
- [ ] Validação de entrada (SQL injection, XSS)

#### 2.2 Testing Suite
- [ ] Unit tests: function_executor, conversation_manager
- [ ] Integration tests: webhook → database flow
- [ ] Mock tests: Groq/Evolution/Notion clients
- [ ] Test coverage: mínimo 70%
- [ ] GitHub Actions CI pipeline

#### 2.3 Monitoring & Observability
- [ ] Structured logging (JSON com contextual info)
- [ ] Metrics: response time, error rate, LLM usage
- [ ] Health check endpoint detalhado (`/health/detailed`)
- [ ] Sentry para error tracking
- [ ] Prometheus/Grafana dashboard (opcional)

#### 2.4 Database Optimization
- [ ] Adicionar indexes: phone_number, notion_id, scheduled_time
- [ ] Query optimization (eager loading relationships)
- [ ] Connection pooling (SQLAlchemy engine config)
- [ ] Database backup strategy (pg_dump cron job)

**Novos arquivos:**
- `tests/unit/test_function_executor.py`
- `tests/integration/test_webhook_flow.py`
- `.github/workflows/ci.yml`
- `src/utils/monitoring.py`
- `src/utils/retry.py`

---

### **FASE 3: Experiência do Usuário** (2-3 dias)
**Objetivo:** Melhorar interação e onboarding

#### 3.1 Onboarding Flow
- [ ] Primeira mensagem: tour guiado interativo
- [ ] Setup wizard: nome, timezone, vincular Notion
- [ ] Tutorial de comandos com exemplos
- [ ] Link para documentação/FAQ

#### 3.2 Melhorias no Bot
- [ ] Mensagens de erro humanizadas (não expor stack traces)
- [ ] Sugestões contextuais: "Quer criar uma tarefa?"
- [ ] Confirmações com botões (se Evolution API suportar)
- [ ] Formatação rich: *negrito*, _itálico_, listas

#### 3.3 Analytics Básico
- [ ] Tracking: comandos mais usados, engagement
- [ ] Relatório semanal automático
- [ ] Insights: "Você completou 15 tarefas esta semana! 🎉"

**Novos arquivos:**
- `src/ai/onboarding.py`
- `src/analytics/tracker.py`
- `src/api/admin.py` (dashboard interno)

---

### **FASE 4: Escalabilidade & DevOps** (3-5 dias)
**Objetivo:** Preparar para crescimento e produção real

#### 4.1 Infrastructure as Code
- [ ] Docker Compose multi-stage builds
- [ ] Kubernetes manifests (deployment, service, ingress)
- [ ] Terraform para provisionar Render/AWS
- [ ] Separação: staging vs production

#### 4.2 Rate Limiting & Security
- [ ] Rate limit por usuário (prevent abuse)
- [ ] Webhook signature validation (Evolution API)
- [ ] Secrets management (Vault/AWS Secrets Manager)
- [ ] HTTPS only, CORS policies

#### 4.3 Escalabilidade
- [ ] Redis cache (conversation history, user state)
- [ ] Celery para background tasks (Notion sync assíncrono)
- [ ] Load balancer (se múltiplas instâncias)
- [ ] Database read replicas

#### 4.4 Upgrade Render Plan (se necessário)
- [ ] Render Pro: $7/mês → worker separado para scheduler
- [ ] Render Redis: $5/mês → cache
- [ ] Ou migrar para AWS EC2 + RDS

**Novos arquivos:**
- `k8s/deployment.yaml`, `k8s/service.yaml`
- `terraform/main.tf`
- `docker-compose.production.yml`
- `src/cache/redis_client.py`

---

## 📈 Métricas de Sucesso

### Após Fase 1
- ✅ Notion sync funcionando
- ✅ Reminders enviados corretamente
- ✅ 3 novas funções ativas

### Após Fase 2
- ✅ 0 crashes em 24h
- ✅ 70%+ test coverage
- ✅ Response time < 2s (p95)

### Após Fase 3
- ✅ 90% dos novos usuários completam onboarding
- ✅ Retention +30% (users ativos após 7 dias)

### Após Fase 4
- ✅ Sistema aguenta 100+ usuários concorrentes
- ✅ 99.5% uptime
- ✅ Deploy automatizado em < 5 min

---

## 💡 Decisões Técnicas

### Priorização
1. **Alta:** Notion sync, Reminders (já codificados!)
2. **Média:** Testing, Monitoring
3. **Baixa:** Kubernetes, Redis (quando escalar)

### Stack Recomendada
- **Cache:** Redis (Render $5/mês ou free Upstash)
- **Queue:** Celery + Redis
- **Monitoring:** Sentry free tier + Prometheus
- **CI/CD:** GitHub Actions (free)

### Custos Estimados (após Fase 4)
- Render Web + Worker: $14/mês
- Render PostgreSQL: $0 (free tier OK para 100 users)
- Render Redis: $5/mês
- **Total: ~$20/mês** para suportar centenas de usuários

---

## 🚀 Como Ativar Este Plano

Quando pronto para executar, role por aqui e diga:
```
"vamos começar a fase 1: ativar notion sync e reminders"
```

Ou especificamente qual tarefa:
```
"adiciona set_reminder ao bot agora"
```

Este arquivo é seu blueprint para crescer de MVP para produção! 🎯
