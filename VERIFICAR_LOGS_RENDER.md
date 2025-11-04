# 🔍 Como Verificar Logs do Build no Render

## ⚠️ Nota sobre a CLI

A chave `8ELA-NFLQ-5K8Z-QAV0` parece não estar configurada corretamente para a API do Render.

Para acessar via CLI, você precisa fazer login primeiro:

```bash
render login
```

Isso abrirá o navegador para você fazer login via OAuth.

---

## 🎯 MÉTODO MAIS RÁPIDO: Via Dashboard

### 1. Acesse o Dashboard
```
https://dashboard.render.com
```

### 2. Encontre o Serviço "agente final"

Na lista de serviços, procure por:
- `agente-final`
- `agentefinal`
- `pangeia-agent`

### 3. Ver Logs do Build

1. Click no serviço
2. Vá na aba **"Logs"**
3. Filtre por **"Build"** ou **"Deploy"**

---

## 🔍 O Que Verificar nos Logs

### Erros Comuns:

#### ❌ **1. Erro de Dependências**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solução:** Verifique o `requirements.txt`

---

#### ❌ **2. Erro de Python Version**
```
Error: Python version not supported
```

**Solução:** Adicione no Render:
```
PYTHON_VERSION=3.11.0
```

---

#### ❌ **3. Erro de Variáveis de Ambiente**
```
KeyError: 'DATABASE_URL'
```

**Solução:** Verifique se todas as 15 env vars foram adicionadas

---

#### ❌ **4. Erro de Build Command**
```
Command 'pip install -r requirements.txt' failed
```

**Possíveis causas:**
- `requirements.txt` não existe
- Pacotes incompatíveis
- Memória insuficiente (Free plan tem limites)

---

#### ❌ **5. Erro no Start Command**
```
Module 'src.main' not found
```

**Solução:** Verifique o start command:
```
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

---

## 📋 Checklist de Verificação

- [ ] Build Command está correto?
  ```
  pip install -r requirements.txt
  ```

- [ ] Start Command está correto?
  ```
  uvicorn src.main:app --host 0.0.0.0 --port $PORT
  ```

- [ ] Todas as 15 env vars foram adicionadas?
  - DATABASE_URL
  - EVOLUTION_API_URL
  - EVOLUTION_API_KEY
  - EVOLUTION_INSTANCE_NAME
  - NOTION_API_KEY
  - NOTION_DATABASE_ID
  - OPENAI_API_KEY
  - OPENAI_MODEL
  - APP_HOST
  - DEBUG
  - LOG_LEVEL
  - TIMEZONE
  - AGENT_TEMPERATURE
  - AGENT_MAX_ITERATIONS

- [ ] Repositório está conectado?
  ```
  https://github.com/estevaoantuness/agentefinal
  ```

- [ ] Branch está correto?
  ```
  main
  ```

---

## 🛠️ Soluções Rápidas

### Se o build falhar por falta de memória:

Reduza as dependências ou considere o plano pago.

### Se houver erro em algum pacote:

Verifique compatibilidade:
```bash
# Localmente
pip install -r requirements.txt
```

### Se o app não iniciar:

Teste localmente:
```bash
uvicorn src.main:app --reload
```

---

## 📞 Como Me Enviar os Logs

Se precisar de ajuda, copie:

1. **Build Logs** - Últimas 50 linhas
2. **Runtime Logs** - Erro específico
3. **Deploy Status** - Success/Failed

E me envie!

---

## 🔄 Tentar Novamente

Após corrigir o problema:

1. **Dashboard** → Seu serviço
2. **Manual Deploy** → **"Clear build cache & deploy"**
3. Aguarde o novo build

---

## 💡 Dica: Verificar Localmente Antes

Antes de deployar, teste localmente:

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env
# Edite o .env com suas credenciais

# 3. Rodar aplicação
uvicorn src.main:app --reload

# 4. Testar health check
curl http://localhost:8000/health
```

Se funcionar localmente, deve funcionar no Render!

---

## 📊 Acesso Direto aos Logs

Se você já sabe o nome exato do serviço, acesse diretamente:

```
https://dashboard.render.com/web/[SERVICE-ID]/logs
```

---

**Me envie os logs que eu te ajudo a resolver! 🚀**
