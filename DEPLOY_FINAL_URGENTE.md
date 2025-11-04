# 🚨 DEPLOY FINAL - SERVIÇO ENCONTRADO COM ERRO 502

## ✅ STATUS ATUAL

**Serviço encontrado:** `https://agentefinal.onrender.com`
**Status:** 502 Bad Gateway (serviço existe mas está falhando)
**Ação necessária:** Verificar logs e corrigir configurações

---

## 🎯 PASSOS PARA CORRIGIR AGORA

### 1. Acesse o Dashboard do Render
```
https://dashboard.render.com
```

### 2. Encontre o serviço "agentefinal"
- Deve aparecer na lista de serviços
- Status provavelmente: "Deploy failed" ou "Build failed"

### 3. Veja os LOGS
- Click no serviço
- Vá na aba **"Logs"**
- Procure por erros em vermelho

---

## 🔧 CORREÇÕES MAIS PROVÁVEIS

### ❌ Problema 1: Build Command Incorreto
**Solução:** Vá em **Settings** → **Build & Deploy**

**Build Command atual pode estar:**
```
pip install -r requirements.txt
```

**Deve ser:**
```
./build.sh
```

OU (alternativa):
```
chmod +x build.sh && ./build.sh
```

---

### ❌ Problema 2: Start Command Incorreto
**Solução:** Vá em **Settings** → **Build & Deploy**

**Start Command deve ser:**
```
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

---

### ❌ Problema 3: Variáveis de Ambiente Faltando

**Solução:** Vá em **Environment** → Verifique se TODAS essas variáveis existem:

**IMPORTANTE:** Para as chaves `NOTION_API_KEY` e `OPENAI_API_KEY`, consulte o arquivo `.env` local em seu computador para pegar os valores reais.

```env
DATABASE_URL=postgresql://post_pangeia_user:yblhBhZz3n15SY6kikdYT5SbAekGky26@dpg-d44ll7q4d50c73ejkfrg-a.oregon-postgres.render.com/post_pangeia

EVOLUTION_API_URL=https://evo.pictorial.cloud

EVOLUTION_API_KEY=7LjVQc6PJJFFgzy14pzH90QffOOus0z2

EVOLUTION_INSTANCE_NAME=pangeia_bot

NOTION_API_KEY=your_notion_api_key_here

NOTION_DATABASE_ID=2f0e465754d444c88ee493ca30b1ea36

OPENAI_API_KEY=your_openai_api_key_here

OPENAI_MODEL=gpt5-nano

APP_HOST=0.0.0.0

DEBUG=False

LOG_LEVEL=INFO

TIMEZONE=America/Sao_Paulo

AGENT_TEMPERATURE=0.7

AGENT_MAX_ITERATIONS=5
```

---

### ❌ Problema 4: Runtime (Python Version)

**Solução:** Vá em **Settings** → **Environment**

**Adicione (se não existir):**
```
PYTHON_VERSION=3.11.7
```

---

## 🚀 DEPOIS DE CORRIGIR

### 1. Manual Deploy
- Click em **"Manual Deploy"**
- Selecione **"Clear build cache & deploy"**
- Aguarde 5-7 minutos

### 2. Acompanhe os Logs
- Vá na aba **"Logs"**
- Veja o progresso em tempo real
- Procure por:
  - ✅ `Build completed successfully`
  - ✅ `Starting server...`
  - ✅ `Application startup complete`

### 3. Teste o Health Check
Quando o deploy terminar, teste:
```
https://agentefinal.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "pangeia_agent"
}
```

---

## 📊 ERROS COMUNS NOS LOGS E SOLUÇÕES

### Erro: "ModuleNotFoundError: No module named 'src'"
**Solução:** Start command incorreto. Use:
```
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### Erro: "Failed building wheel for pydantic-core"
**Solução:** Build command incorreto. Use:
```
./build.sh
```

### Erro: "KeyError: 'DATABASE_URL'"
**Solução:** Variáveis de ambiente faltando. Adicione todas as env vars acima.

### Erro: "Connection to database failed"
**Solução:** DATABASE_URL incorreta. Verifique se está exatamente como acima.

### Erro: "Permission denied: ./build.sh"
**Solução:** Build command deve ter:
```
chmod +x build.sh && ./build.sh
```

---

## 🔍 VERIFICAÇÃO FINAL

Depois que o serviço estiver rodando (status "Live"):

### 1. Teste Health Check
```bash
curl https://agentefinal.onrender.com/health
```

### 2. Teste Root Endpoint
```bash
curl https://agentefinal.onrender.com/
```

### 3. Configure Webhook Evolution API
```
URL Manager: https://evo.pictorial.cloud/manager/
Webhook URL: https://agentefinal.onrender.com/webhook/evolution
```

### 4. Teste via WhatsApp
Envie: `Olá!`

---

## 📝 CHECKLIST COMPLETO

- [ ] Acessei https://dashboard.render.com
- [ ] Encontrei o serviço "agentefinal"
- [ ] Vi os logs de erro
- [ ] Corrigi Build Command para `./build.sh`
- [ ] Corrigi Start Command para `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- [ ] Adicionei todas as 15 variáveis de ambiente
- [ ] Fiz Manual Deploy com "Clear build cache"
- [ ] Aguardei o deploy completar (5-7 min)
- [ ] Testei /health (retornou sucesso)
- [ ] Configurei webhook no Evolution API
- [ ] Testei via WhatsApp

---

## 🆘 SE AINDA NÃO FUNCIONAR

Me envie:
1. **Screenshot dos logs** (últimas 50 linhas)
2. **Screenshot das configurações** (Build & Deploy settings)
3. **Lista de env vars** (sem os valores, só os nomes)

---

## 📌 INFORMAÇÕES IMPORTANTES

**Repositório GitHub:**
```
https://github.com/estevaoantuness/agentefinal
```

**Branch:**
```
main
```

**URL do Serviço:**
```
https://agentefinal.onrender.com
```

**Health Check Path:**
```
/health
```

---

**⏱️ Tempo estimado para correção: 5-10 minutos**

**Último commit:** `f9d22a8` ✅

---

🚀 **Bora corrigir esse deploy!**
