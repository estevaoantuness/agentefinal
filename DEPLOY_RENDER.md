# Deploy no Render - Guia Completo

## 📋 Pré-requisitos

1. Conta no [Render](https://render.com)
2. Repositório Git (GitHub, GitLab, etc.) com o código
3. OpenAI API Key com acesso ao GPT5-NANO
4. Notion Database ID (ID do banco de dados do Notion)

## 🚀 Passo a Passo

### 1. Preparar o Repositório

Certifique-se de que o código está no Git:

```bash
git add .
git commit -m "Initial commit - Pangeia Agent"
git push origin main
```

### 2. Criar Web Service no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório Git
4. Configure:
   - **Name**: `pangeia-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### 3. Configurar Variáveis de Ambiente

No Render Dashboard, vá em "Environment" e adicione:

```env
DATABASE_URL=postgresql://post_pangeia_user:yblhBhZz3n15SY6kikdYT5SbAekGky26@dpg-d44ll7q4d50c73ejkfrg-a.oregon-postgres.render.com/post_pangeia

EVOLUTION_API_URL=https://evo.escreve.ai
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=pangeia_bot

NOTION_API_KEY=[VEJA_SEU_ARQUIVO_.env]
NOTION_DATABASE_ID=2f0e465754d444c88ee493ca30b1ea36

OPENAI_API_KEY=[VEJA_SEU_ARQUIVO_.env]
OPENAI_MODEL=gpt5-nano

APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
LOG_LEVEL=INFO

TIMEZONE=America/Sao_Paulo

AGENT_TEMPERATURE=0.7
AGENT_MAX_ITERATIONS=5
```

⚠️ **IMPORTANTE**: Substitua:
- `SEU_DATABASE_ID_AQUI` → ID do seu banco de dados do Notion
- `SUA_OPENAI_API_KEY_AQUI` → Sua chave da API OpenAI

### 4. Deploy

1. Clique em "Create Web Service"
2. Aguarde o deploy (pode levar alguns minutos)
3. Após o deploy, você receberá uma URL como: `https://pangeia-agent.onrender.com`

### 5. Configurar Webhook no Evolution API

1. Acesse a Evolution API em: `https://evo.escreve.ai`
2. Configure o webhook para apontar para:
   ```
   https://pangeia-agent.onrender.com/webhook/evolution
   ```

3. Teste o webhook acessando:
   ```
   https://pangeia-agent.onrender.com/health
   ```

### 6. Inicializar o Banco de Dados

O banco de dados será inicializado automaticamente no primeiro startup da aplicação.

Para verificar, acesse:
```
https://pangeia-agent.onrender.com/
```

Você deve ver:
```json
{
  "service": "Pangeia Task Manager Agent",
  "version": "1.0.0",
  "status": "running"
}
```

## 🔧 Configuração do Notion

1. Acesse [Notion Integrations](https://www.notion.so/my-integrations)
2. Crie uma nova integração (já existe com a API Key fornecida)
3. Compartilhe o banco de dados de tarefas com a integração
4. Copie o Database ID da URL do Notion:
   ```
   https://www.notion.so/SEU_DATABASE_ID_AQUI?v=...
   ```
5. Adicione no Render como variável `NOTION_DATABASE_ID`

## 📱 Configuração do WhatsApp

1. Configure sua instância no Evolution API
2. Escaneie o QR Code para conectar o WhatsApp
3. O webhook já estará configurado automaticamente
4. Envie uma mensagem de teste: "Olá"

## ✅ Teste Completo

1. Envie uma mensagem via WhatsApp: "Cria uma tarefa de testar o sistema"
2. O agente deve responder confirmando a criação
3. Verifique no Notion se a tarefa foi sincronizada
4. Liste as tarefas: "Quais são minhas tarefas?"

## 🔄 Atualizar a Aplicação

Para fazer deploy de novas versões:

```bash
git add .
git commit -m "Sua mensagem"
git push origin main
```

O Render fará o deploy automático.

## 📊 Monitoramento

No Render Dashboard você pode:
- Ver logs em tempo real
- Monitorar uso de recursos
- Configurar alertas
- Ver métricas de performance

## 🆘 Troubleshooting

### Erro de conexão com banco de dados
- Verifique se a `DATABASE_URL` está correta
- Confirme que o banco no Render está ativo

### Webhook não recebe mensagens
- Verifique se a URL do webhook está correta no Evolution
- Teste: `curl https://seu-app.onrender.com/webhook/test`

### Agent não responde
- Verifique a `OPENAI_API_KEY`
- Confirme que tem créditos na conta OpenAI
- Veja os logs no Render Dashboard

### Notion não sincroniza
- Verifique a `NOTION_API_KEY`
- Confirme o `NOTION_DATABASE_ID`
- Verifique se compartilhou o banco com a integração

## 📞 Suporte

Para problemas, verifique:
1. Logs no Render Dashboard
2. Status da API Evolution
3. Status da API OpenAI
4. Conectividade do banco de dados
