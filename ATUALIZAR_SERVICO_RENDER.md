# 🔄 ATUALIZAR SERVIÇO EXISTENTE NO RENDER

## Se você JÁ criou o serviço "agente final" no Render:

---

## ⚡ MÉTODO RÁPIDO (3 passos):

### 1️⃣ Atualizar Build Command

No Dashboard do Render:
1. Vá no serviço **"agente final"**
2. Settings → **Build Command**
3. Mude de:
   ```
   pip install -r requirements.txt
   ```
   Para:
   ```
   ./build.sh
   ```
4. **Save Changes**

---

### 2️⃣ Forçar Redeploy

1. Na página do serviço
2. Click em **"Manual Deploy"**
3. Selecione: **"Clear build cache & deploy"**
4. **Deploy**

---

### 3️⃣ Acompanhar Logs

Vá na aba **"Logs"** e veja:

```
✅ ==> Updating pip...
✅ ==> Installing dependencies...
✅ ==> Build completed successfully!
✅ ==> Starting app...
✅ ==> Deploy successful!
```

---

## 📊 TEMPO ESTIMADO:

- Atualizar comando: 30 segundos
- Build: 3-5 minutos
- Total: **~5 minutos**

---

## ✅ VERIFICAÇÃO APÓS DEPLOY:

### 1. Health Check
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

### 2. Logs devem mostrar:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

---

## 🔄 SE AUTO-DEPLOY ESTIVER ATIVO:

O Render pode já estar fazendo deploy automaticamente!

Verifique:
1. Dashboard → Seu serviço
2. Se há um deploy em andamento
3. Acompanhe os logs

---

## ❌ SE AINDA FALHAR:

### Opção A: Recriar do Zero

1. **Delete** o serviço antigo
2. **New +** → **Web Service**
3. Configure tudo novamente
4. Use as instruções do `DEPLOY_CLI.md`

### Opção B: Me envie os logs

Copie as últimas 50 linhas dos logs e me envie!

---

## 📝 ARQUIVOS NECESSÁRIOS (já no GitHub):

✅ `build.sh` - Script de build otimizado
✅ `runtime.txt` - Python 3.11.7
✅ `requirements.txt` - Versões corrigidas

Tudo já foi enviado para:
```
https://github.com/estevaoantuness/agentefinal
```

O Render vai puxar automaticamente quando você fizer o deploy!

---

## 🎯 RESUMO:

1. **Mude o Build Command** para `./build.sh`
2. **Clear cache & deploy**
3. **Aguarde 5 minutos**
4. **Teste o health check**
5. **Configure o webhook**
6. **Pronto!** 🎉

---

**O código está corrigido e pronto! Só precisa fazer o redeploy! 🚀**
