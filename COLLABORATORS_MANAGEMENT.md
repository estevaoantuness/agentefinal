# 👥 Gerenciamento de Colaboradores

## Como o bot reconhece colaboradores

O bot usa um **banco de dados PostgreSQL** para armazenar e reconhecer colaboradores.

Quando uma mensagem chega:
1. O bot extrai o número de telefone do remetente
2. Busca no PostgreSQL se existe um usuário com esse telefone
3. Se encontrar, sabe quem é o colaborador
4. Processa o comando com as permissões e dados do usuário

---

## 📱 Adicionar um novo colaborador

### Via API REST

**POST** `/api/collaborators`

```bash
curl -X POST http://localhost:8000/api/collaborators \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "5584984282600",
    "name": "Luna Machado"
  }'
```

**Response:**
```json
{
  "id": 5,
  "phone_number": "5584984282600",
  "name": "Luna Machado",
  "is_active": true
}
```

### Via Script (Migração do Google Sheets)

Execute o script para sincronizar todos os colaboradores do Google Sheets:

```bash
python scripts/migrate_sheets_to_db.py
```

Isso vai:
- Ler o Google Sheets
- Adicionar novos colaboradores
- Atualizar os existentes

---

## 🔧 Editar um colaborador

**PUT** `/api/collaborators/{phone_number}`

```bash
curl -X PUT http://localhost:8000/api/collaborators/5584984282600 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Luna Machado Silva",
    "is_active": true
  }'
```

---

## ❌ Remover um colaborador

**DELETE** `/api/collaborators/{phone_number}`

```bash
curl -X DELETE http://localhost:8000/api/collaborators/5584984282600
```

**Nota:** Isso marca o colaborador como inativo (soft delete), não deleta do banco.

---

## 📋 Listar todos os colaboradores

**GET** `/api/collaborators`

```bash
curl http://localhost:8000/api/collaborators
```

**Response:**
```json
[
  {
    "id": 1,
    "phone_number": "5511991095230",
    "name": "Estevão",
    "is_active": true
  },
  {
    "id": 2,
    "phone_number": "5584984282600",
    "name": "Luna Machado",
    "is_active": true
  }
]
```

---

## 🔄 Sincronizar Google Sheets

**POST** `/api/collaborators/sync/sheets`

```bash
curl -X POST http://localhost:8000/api/collaborators/sync/sheets
```

**Response:**
```json
{
  "synced": 10,
  "message": "Sincronização concluída"
}
```

---

## 📊 Formato de Telefone

O sistema aceita múltiplos formatos e normaliza automaticamente:

- ✅ `5584984282600` (correto)
- ✅ `55 84 98428-2600` (será normalizado)
- ✅ `11 9 9109-5230` (será normalizado para 5511991095230)
- ✅ `+55 84 98428-2600` (será normalizado)

---

## 🗄️ Estrutura do Banco de Dados

**Tabela: users**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    notion_token VARCHAR(200),
    notion_database_id VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 🚀 Fluxo Completo

### 1️⃣ Migração Inicial (Do Google Sheets)

```bash
python scripts/migrate_sheets_to_db.py
```

Isso importa todos os colaboradores da planilha para o PostgreSQL.

### 2️⃣ Adicionar Novo Colaborador

```bash
curl -X POST http://agentefinal.onrender.com/api/collaborators \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "5511991095230",
    "name": "Novo Colaborador"
  }'
```

### 3️⃣ Bot Reconhece Automaticamente

Quando o colaborador enviar uma mensagem:
- WhatsApp envia webhook com o telefone
- Bot busca no PostgreSQL
- Encontra o nome e dados do colaborador
- Processa o comando

### 4️⃣ (Opcional) Remover Colaborador

```bash
curl -X DELETE http://agentefinal.onrender.com/api/collaboradores/5511991095230
```

---

## 🔐 Variáveis de Ambiente

O bot precisa da `DATABASE_URL` para funcionar:

```
DATABASE_URL=postgresql://user:password@host:5432/database
```

Você já tem:
```
postgresql://pangeia:apPljYDl5JvvRMcNbJbREURyx8MxivkM@dpg-d45sg27diees738g4chg-a/pangeia_db
```

---

## 📚 Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/collaborators` | Listar todos |
| GET | `/api/collaborators/{phone}` | Obter um específico |
| POST | `/api/collaborators` | Criar novo |
| PUT | `/api/collaborators/{phone}` | Editar |
| DELETE | `/api/collaborators/{phone}` | Desativar |
| POST | `/api/collaborators/sync/sheets` | Sincronizar Google Sheets |

---

## 💡 Dicas

- Use sempre o formato completo do telefone (com código de país 55)
- Para mudar dados de um colaborador, use o endpoint PUT
- O sistema usa "soft delete" - o colaborador fica inativo mas não é deletado
- Você pode sincronizar o Google Sheets a qualquer momento
- Todos os endpoints são acessíveis via API REST

