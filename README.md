# Pangeia Bot - Personal Productivity Assistant

> WhatsApp-integrated AI assistant that syncs tasks with Notion and helps you stay productive through natural conversations

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/estevaoantuness/agentefinal)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.1-orange.svg)](https://console.groq.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Deploy Status](https://img.shields.io/badge/deployment-Render-blueviolet)](https://agentefinal.onrender.com)

---

## 📋 Quick Navigation

- [About](#about) - What is Pangeia Bot?
- [MVP Features](#mvp-features) - Current capabilities
- [Getting Started](#getting-started) - Installation & setup
- [Usage](#usage) - How to use
- [Architecture](#architecture) - System design
- [Roadmap](#roadmap) - Future features
- [Contributing](#contributing) - How to contribute

---

## About

**Pangeia Bot** is a WhatsApp-integrated personal productivity assistant powered by AI. Manage your tasks naturally through WhatsApp while automatically syncing everything with Notion.

### Why Pangeia Bot?

- **WhatsApp Native**: Use the platform you already have - no new app needed
- **AI-Powered**: Natural language understanding, not command-based
- **Notion Integration**: Seamless sync with your existing workflow
- **Fast & Free**: Powered by Groq's free LLM with sub-second responses
- **Privacy First**: Can be self-hosted, you control your data
- **Open Source**: MIT licensed, contribute and customize

### Current MVP Status

✅ **Version 1.0 - Production Ready**
- Fully functional WhatsApp integration
- All core task management features
- Deployed on Render cloud
- Thoroughly tested and documented

---

## MVP Features

### Core Functionality (v1.0)

| Feature | Status | Description |
|---------|--------|-------------|
| **View Tasks** | ✅ | List all tasks filtered by status (pending, in progress, completed) |
| **Create Tasks** | ✅ | Add new tasks with natural language descriptions |
| **Mark Progress** | ✅ | Update task status to "in progress" |
| **Mark Complete** | ✅ | Mark tasks as completed |
| **Check Progress** | ✅ | Get productivity metrics and task summary |
| **Get Help** | ✅ | Context-aware help and command suggestions |

### Technical Features

✅ WhatsApp webhook integration (Evolution API)
✅ PostgreSQL database persistence
✅ Notion API synchronization
✅ Groq LLM with function calling
✅ Docker containerization
✅ Render cloud deployment with auto-scaling

---

## Tech Stack

### Backend & Framework
- **Framework**: FastAPI 0.109 (modern async Python)
- **Server**: Uvicorn (ASGI server)
- **Database**: PostgreSQL 14+ (relational data)
- **ORM**: SQLAlchemy 2.0 (database abstraction)

### AI & Language Model
- **LLM**: Groq Llama 3.1 8B Instant (free, fast)
- **Function Calling**: Structured task operations
- **Language**: Portuguese support

### Integrations
- **WhatsApp**: Evolution API
- **Notion**: Official Notion Python SDK
- **HTTP**: Requests library

### DevOps
- **Containers**: Docker & Docker Compose
- **Cloud**: Render (auto-deploy on push)
- **Logging**: Python JSON Logger (structured)

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or Docker)
- Git
- Groq API key (free from https://console.groq.com)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/estevaoantuness/agentefinal.git
cd agentefinal
```

### 2️⃣ Setup Environment

**Option A: Docker (Recommended - simplest)**
```bash
docker-compose up --build
```

**Option B: Local Installation**
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables

Create `.env` file:
```bash
cp .env.example .env
```

Edit with your credentials:
```env
# Database (local: postgresql://user:pass@localhost/pangeia_tasks)
DATABASE_URL=postgresql://user:pass@localhost/pangeia_tasks

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://evo.pictorial.cloud
EVOLUTION_API_KEY=your_key_here
EVOLUTION_INSTANCE_NAME=Pangeia Bot

# Notion
NOTION_API_KEY=your_notion_token
NOTION_DATABASE_ID=your_database_id

# Groq (get free key at console.groq.com)
OPENAI_API_KEY=gsk_your_groq_key_here
OPENAI_MODEL=llama-3.1-8b-instant

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
TIMEZONE=America/Sao_Paulo
DEBUG=False
LOG_LEVEL=INFO
```

### 4️⃣ Run Application

**With Docker:**
```bash
docker-compose up
# Visit: http://localhost:8000/docs
```

**Locally:**
```bash
uvicorn src.main:app --reload
# Visit: http://localhost:8000/docs
```

### 5️⃣ Get API Keys

**Groq (Free LLM):**
1. Go to https://console.groq.com
2. Sign up (no credit card needed)
3. Create API key
4. Copy to `OPENAI_API_KEY` in `.env`

**Evolution (WhatsApp):**
1. Visit https://evo.pictorial.cloud
2. Create WhatsApp instance
3. Get API key from dashboard
4. Set webhook to: `https://your-app.onrender.com/webhook/evolution`

**Notion:**
1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Copy "Internal Integration Token"
4. Share your database with the integration
5. Get Database ID from database URL

---

## Usage

### WhatsApp Commands (Examples)

```
User: listar tarefas
Bot: Aqui estão suas tarefas:
✅ Completed: 5 tasks
⏳ In Progress: 2 tasks
📋 Pending: 8 tasks

User: criar tarefa: Terminar MVP do Pangeia Bot
Bot: ✅ Tarefa criada!
Nome: Terminar MVP do Pangeia Bot
Status: Pendente

User: comecei a tarefa 1
Bot: ✅ Tarefa 1 marcada como "Em Andamento"

User: concluí a primeira
Bot: ✅ Tarefa 1 marcada como "Concluída"

User: meu progresso
Bot: 📊 Taxa de Conclusão: 38%
```

### API Documentation

Access interactive docs at: `http://localhost:8000/docs`

**Webhook Endpoint:**
```bash
POST /webhook/evolution
Content-Type: application/json

{
  "event": "messages.upsert",
  "data": {
    "key": {"remoteJid": "5511987654321@s.whatsapp.net"},
    "message": {"conversation": "listar tarefas"}
  }
}
```

---

## Project Structure

```
agentefinal/
├── src/
│   ├── main.py                    # FastAPI entry point
│   ├── config/settings.py         # Configuration
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   └── session.py             # Database connection
│   ├── ai/
│   │   ├── openai_client.py       # Groq LLM wrapper
│   │   ├── function_definitions.py # Task function schemas
│   │   ├── function_executor.py   # Execute operations
│   │   ├── system_prompt.py       # AI instructions
│   │   └── conversation_manager.py # Chat history
│   ├── integrations/
│   │   ├── evolution_api.py       # WhatsApp API
│   │   └── notion_sync.py         # Notion database sync
│   ├── api/webhooks.py            # HTTP endpoints
│   └── utils/
│       ├── logger.py              # Logging setup
│       └── helpers.py             # Utilities
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── docker-compose.yml             # Docker setup
├── Dockerfile                     # Container config
└── README.md                      # This file
```

---

## Architecture

### System Flow Diagram

```
WhatsApp Message
        ↓
Evolution API Webhook (/webhook/evolution)
        ↓
FastAPI Handler
        ↓
Conversation Manager (Memory)
        ↓
Groq LLM (Function Calling)
        ↓
Function Executor
├── view_tasks()
├── create_task()
├── mark_progress()
├── mark_done()
├── view_progress()
└── get_help()
        ↓
Database Operations
├── PostgreSQL
└── Notion Sync
        ↓
Response Message → WhatsApp
```

### Why Groq?

- **Free Tier**: Generous rate limits, no credit card required
- **Fast**: Sub-second latency globally
- **Function Calling**: Structured outputs for reliable task operations
- **Portuguese Support**: Native language support
- **Open Models**: Transparent, reproducible results

---

## Development

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Watch mode
ptw
```

### Code Quality

```bash
# Format
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Docker Workflow

```bash
# Build & start
docker-compose up --build

# View logs
docker-compose logs -f app

# Stop
docker-compose down

# Rebuild (skip cache)
docker-compose up --build --no-cache
```

---

## Deployment

### Deploy to Render

This project is configured for auto-deployment:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update Pangeia Bot"
   git push origin main
   ```

2. **Auto-Deploy** (automatic on Render)
   - View at: https://agentefinal.onrender.com
   - Dashboard: https://dashboard.render.com

3. **Set Environment Variables**
   - Go to Render Dashboard
   - Select app → Settings → Environment
   - Add all variables from `.env`

### Health Check

```bash
curl https://agentefinal.onrender.com/health
# Returns: {"status": "ok"}
```

---

## Roadmap

### Phase 2: Enhanced Features 🚀

- [ ] Recurring/daily reminders
- [ ] AI-suggested task priorities
- [ ] Focus mode (distraction blocker)
- [ ] Team collaboration features
- [ ] Productivity dashboard

### Phase 3: Advanced AI 🧠

- [ ] Habit tracking & analytics
- [ ] Smart task scheduling
- [ ] Voice commands via WhatsApp
- [ ] Third-party integrations (Calendar, GitHub, Jira)
- [ ] ML-based time predictions

### Phase 4: Enterprise 🏢

- [ ] Team dashboard
- [ ] Role-based access control
- [ ] Audit logging
- [ ] SSO integration
- [ ] SLA management

### Milestones

| Version | Status | Features |
|---------|--------|----------|
| 1.0 | ✅ Live | Core task management |
| 1.1 | 🔄 Q4 2024 | Reminders & recurring tasks |
| 2.0 | 📋 Q1 2025 | Analytics & team features |

---

## Contributing

We welcome contributions!

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit: `git commit -m "feat: add amazing feature"`
4. Push: `git push origin feature/amazing`
5. Open Pull Request

### Code Guidelines

- Follow PEP 8
- Add type hints
- Write docstrings
- Include tests
- Update docs

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection error | Check `DATABASE_URL` in `.env`, ensure PostgreSQL running |
| Groq API 429 error | Rate limit hit - wait or upgrade plan |
| Notion sync fails | Verify token & database sharing |
| No WhatsApp messages | Check webhook URL, Evolution API config |

---

## FAQ

**Q: Can I run locally?**
A: Yes! Use Docker Compose for instant setup.

**Q: Is my data private?**
A: Yes! All data stored in PostgreSQL. Self-host if needed.

**Q: How much does this cost?**
A: Free! Groq free tier + free Render hobby dyno.

**Q: Can I modify the AI?**
A: Yes! Edit `src/ai/system_prompt.py` to customize behavior.

---

## License

MIT License - See [LICENSE](LICENSE) for details

## Support

- GitHub Issues: [Report bugs](https://github.com/estevaoantuness/agentefinal/issues)
- Discussions: [Ask questions](https://github.com/estevaoantuness/agentefinal/discussions)

---

## Acknowledgments

- [Groq](https://groq.com) - Fast LLM inference
- [Notion](https://notion.so) - Database platform
- [Evolution API](https://evolution-api.com) - WhatsApp integration
- [FastAPI](https://fastapi.tiangolo.com) - Web framework

---

**Made with ❤️ for productivity enthusiasts**

Last Updated: November 5, 2024
Status: **MVP v1.0 - Production Ready** ✅
Live: https://agentefinal.onrender.com
