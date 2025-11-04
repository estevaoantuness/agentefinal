# 🚀 Deploy via Render Dashboard (Método Mais Simples)

Sua API Key: `8ELA-NFLQ-5K8Z-QAV0`

---

## ✨ MÉTODO RECOMENDADO: Deploy via Dashboard

### Passo 1: Acesse o Dashboard
```
https://dashboard.render.com
```

### Passo 2: Criar Novo Web Service

1. Click em **"New +"** → **"Web Service"**

2. Conecte seu repositório GitHub:
   ```
   https://github.com/estevaoantuness/agentefinal
   ```

3. Configure o serviço:

**Name:**
```
pangeia-agent
```

**Runtime:**
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

**Health Check Path:**
```
/health
```

---

### Passo 3: Adicionar Environment Variables

Cole cada linha abaixo em "Add Environment Variable":

```
DATABASE_URL=postgresql://post_pangeia_user:yblhBhZz3n15SY6kikdYT5SbAekGky26@dpg-d44ll7q4d50c73ejkfrg-a.oregon-postgres.render.com/post_pangeia
```

```
EVOLUTION_API_URL=https://evo.pictorial.cloud
```

```
EVOLUTION_API_KEY=7LjVQc6PJJFFgzy14pzH90QffOOus0z2
```

```
EVOLUTION_INSTANCE_NAME=pangeia_bot
```

```
NOTION_API_KEY=your_notion_api_key_here
```

```
NOTION_DATABASE_ID=2f0e465754d444c88ee493ca30b1ea36
```

```
OPENAI_API_KEY=your_openai_api_key_here
```

```
OPENAI_MODEL=gpt5-nano
```

```
APP_HOST=0.0.0.0
```

```
DEBUG=False
```

```
LOG_LEVEL=INFO
```

```
TIMEZONE=America/Sao_Paulo
```

```
AGENT_TEMPERATURE=0.7
```

```
AGENT_MAX_ITERATIONS=5
```

---

### Passo 4: Deploy!

1. Click em **"Create Web Service"**
2. Aguarde 3-5 minutos para o build
3. Anote a URL do serviço (algo como `https://pangeia-agent.onrender.com`)

---

## ✅ Após o Deploy

### 1. Teste o Health Check

Abra no navegador:
```
https://SEU-APP.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "pangeia_agent"
}
```

### 2. Configure o Webhook

Acesse:
```
https://evo.pictorial.cloud/manager/
```

Configure o webhook para:
```
https://SEU-APP.onrender.com/webhook/evolution
```

### 3. Teste via WhatsApp

Envie uma mensagem para o número conectado na Evolution:
```
Olá!
```

O agente deve responder! 🎉

---

## 🔄 MÉTODO ALTERNATIVO: Via Blueprint (render.yaml)

Se preferir usar o arquivo YAML:

1. No Dashboard Render → **"New +"** → **"Blueprint"**

2. Conecte o repositório

3. O Render vai detectar automaticamente o arquivo `render-complete.yaml`

4. Confirme e faça o deploy!

⚠️ **Nota:** O arquivo `render-complete.yaml` já tem TODAS as env vars configuradas!

---

## 📊 Monitoramento

Após o deploy, você pode:

- **Ver logs:** Dashboard → Logs tab
- **Reiniciar:** Dashboard → Manual Deploy → "Clear build cache & deploy"
- **Métricas:** Dashboard → Metrics tab

---

## 🆘 Troubleshooting

### Build falhou?
- Verifique os logs no Dashboard
- Confirme que o repositório está atualizado

### App não inicia?
- Verifique se TODAS as env vars foram adicionadas
- Veja os logs de runtime

### Webhook não funciona?
- Teste: `https://seu-app.onrender.com/webhook/test`
- Verifique se configurou corretamente no Evolution Manager

---

## 📝 Resumo

✅ Deploy via Dashboard é o mais simples
✅ 15 variáveis de ambiente para adicionar
✅ Build: `pip install -r requirements.txt`
✅ Start: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
✅ Tempo estimado: 5-7 minutos

**Boa sorte! 🚀**
