# Mobile Store AI Telegram Sales Bot

An intelligent Telegram sales bot integrated with Odoo 17, powered by LLM (Local/Groq/Gemini) with conversation memory and RAG capabilities.

## 🎯 Features

- **Multi-LLM Support**: Local (Ollama), Groq, Google Gemini
- **Conversation Memory**: Remembers last 5 messages per user
- **RAG System**: Semantic search over product catalog using embeddings
- **Odoo Integration**: Real-time inventory check and quotation creation
- **Service Layer**: Clean separation of concerns with caching
- **Telegram Bot**: Direct messaging interface
- **REST API**: FastAPI endpoints for integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       TELEGRAM BOT                              │
│                    (Telegram User)                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER                             │
│  ┌──────────────────┐          ┌──────────────────┐             │
│  │ /api/chat        │          │ /api/telegram    │             │
│  │ (REST Endpoint)  │          │ (Webhook)        │             │
│  └────────┬─────────┘          └────────┬─────────┘             │
└───────────┼─────────────────────────────┼───────────────────────┘
            │                             │
            └──────────────┬──────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SALES AGENT (Core)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Retrieve conversation history (Memory)                 │ │
│  │ 2. Retrieve relevant products (RAG)                       │ │
│  │ 3. Build system prompt with context                       │ │
│  │ 4. Call LLM provider                                      │ │
│  │ 5. Extract action (create_order, get_stock)              │ │
│  │ 6. Save to conversation history                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
        │                       │                        │
        ▼                       ▼                        ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  Conversation│  │  Service Layer   │  │   RAG System         │
│   Manager    │  │  ┌────────────┐  │  │ ┌────────────────┐  │
│              │  │  │OdooService │  │  │ │ProductRetriever│  │
│ Store/Load   │  │  │CustomerSvc │  │  │ │VectorStore     │  │
│ 5-msg limit  │  │  │OrderService│  │  │ │EmbeddingProvider
│ JSON files   │  │  └────────────┘  │  │ └────────────────┘  │
└──────────────┘  │  +Caching (+LRU) │  │ ChromaDB+           │
                  └──────────────────┘  │ sentence-transformers
                           │            └──────────────────────┘
                           ▼
                  ┌──────────────────┐
                  │  Odoo 17 (RPC)   │
                  │ • Product Stock  │
                  │ • Customers      │
                  │ • Quotations     │
                  └──────────────────┘
```

## 📦 Project Structure

```
e:/odoo_work/
├── backend/
│   ├── agent/
│   │   ├── sales_agent.py           # Core agent logic
│   │   ├── conversation_manager.py  # Memory management
│   │   ├── intent_detector.py       # Booking intent detection
│   │   ├── json_parser.py           # Action JSON extraction
│   │   ├── product_matcher.py       # Product matching
│   │   └── prompts.py               # LLM prompts
│   ├── models/                      # Pydantic data models
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── agent.py
│   │   └── api.py
│   ├── services/                    # Business logic layer
│   │   ├── odoo_service.py          # Odoo integration (+caching)
│   │   ├── customer_service.py      # Customer operations
│   │   └── order_service.py         # Order operations
│   ├── rag/                         # Retrieval-Augmented Generation
│   │   ├── embeddings.py            # sentence-transformers
│   │   ├── vector_store.py          # ChromaDB persistence
│   │   └── retriever.py             # Product retriever
│   ├── tools/
│   │   └── odoo_tools.py            # Low-level Odoo XML-RPC
│   ├── main.py                      # FastAPI application
│   └── config.py                    # Configuration
├── data/
│   ├── conversations/               # User chat histories (JSON)
│   ├── vector_store/                # ChromaDB data
│   └── products_catalog.json        # Product catalog for RAG
├── tests/
│   ├── test_phase1.py               # Conversation memory tests
│   ├── test_json_parser.py          # JSON parser tests
│   ├── test_agent.py                # Agent tests
│   └── test_odoo.py                 # Odoo service tests (mocked)
├── .env.example                     # Environment variables template
├── docker-compose.yml               # Docker Compose configuration
├── README.md                        # This file
└── requirements.txt                 # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Odoo 17 with XML-RPC enabled
- Telegram Bot Token (from @BotFather)
- One of:
  - Local Ollama instance (for local LLM)
  - Groq API key
  - Google Gemini API key

### 1. Setup Environment

```bash
# Clone/navigate to project
cd e:/odoo_work

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Additional dependencies for RAG (optional)
pip install sentence-transformers chromadb
```

### 2. Configure Environment

```bash
# Copy template and edit
cp .env.example .env

# Edit .env with your values:
# - ODOO_URL, ODOO_DB, credentials
# - TELEGRAM_BOT_TOKEN
# - LLM provider (LOCAL_LLM_URL or GROQ_API_KEY or GEMINI_API_KEY)
```

### 3. Setup Odoo

Ensure Odoo 17 is running with XML-RPC enabled:
```bash
# In Odoo, create a database with demo data
# Enable XML-RPC in Settings > Technical > System Parameters
# Add admin user with API access
```

### 4. Run the Server

```bash
# Start FastAPI server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Run Tests

```bash
# Test conversation memory
python test_phase1.py

# Test JSON parser
python test_json_parser.py

# Test agent
python test_agent.py

# Test Odoo service (mocked)
python test_odoo.py
```

## 🔗 API Endpoints

### Chat API

```
POST /api/chat
Content-Type: application/json

{
  "message": "السلام عليكم، أريد موبايل أيفون",
  "customer_name": "أحمد علي",
  "customer_phone": "+201001234567",
  "provider": "local"
}

Response:
{
  "response": "وعليكم السلام، لدينا عدة أيفونات متاحة...",
  "status": "success"
}
```

### Telegram Webhook

```
POST /api/telegram/webhook
(Handled automatically by Telegram)
```

### Health Check

```
GET /

Response:
{
  "status": "online",
  "message": "FastAPI backend is running successfully"
}
```

## 🧠 System Behavior

### 1. User Message Flow

```
User Message
    ↓
1. Load conversation history (last 5 messages)
2. Retrieve relevant products (RAG semantic search)
3. Get current inventory from Odoo
4. Build system prompt with context
5. Call LLM provider
6. Extract JSON action (if any)
7. Execute action (create_order, etc.)
8. Save conversation to history
9. Return response to user
```

### 2. Conversation Memory

- **Storage**: `data/conversations/{user_id}.json`
- **Limit**: Last 5 messages retrieved and injected into prompt
- **Format**: Arabic labels (العميل/المساعد)
- **Auto-save**: Each message automatically saved

### 3. RAG System

- **Catalog**: `data/products_catalog.json`
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Database**: ChromaDB (persistent)
- **Search**: Semantic similarity matching
- **Injection**: Top 3 results injected into system prompt

### 4. Service Layer

- **OdooService**: Wraps XML-RPC with LRU caching
- **CustomerService**: Customer validation and creation
- **OrderService**: Order validation and creation
- **Caching**: LRU cache for product list and lookups

## 🔧 LLM Provider Configuration

### Local (Ollama)

```bash
# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull mistral

# In .env:
LOCAL_LLM_URL=http://localhost:11434/api/generate
LOCAL_MODEL_NAME=mistral
```

### Groq

```bash
# Get API key from https://console.groq.com

# In .env:
GROQ_API_KEY=gsk_...
GROQ_MODEL_NAME=mixtral-8x7b-32768
```

### Gemini

```bash
# Get API key from https://makersuite.google.com

# In .env:
GEMINI_API_KEY=AIza...
GEMINI_MODEL_NAME=gemini-pro
```

## 📊 Data Storage

### Conversation Files

```
data/conversations/
├── 123456789.json        # Telegram chat_id as user_id
├── user_2.json
└── ...

Format:
[
  {
    "role": "user",
    "content": "السلام عليكم",
    "timestamp": "2026-06-17T10:30:00"
  },
  {
    "role": "assistant",
    "content": "وعليكم السلام",
    "timestamp": "2026-06-17T10:30:05"
  }
]
```

### Vector Store

```
data/vector_store/
├── duckdb_metadata.db
├── data.parquet
└── (ChromaDB files)
```

## 🧪 Testing

All tests use mocking to avoid external dependencies:

```bash
# Run all tests
pytest

# Run specific test
pytest test_phase1.py::test_add_and_retrieve_messages -v

# Run with coverage
pytest --cov=backend --cov-report=html
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up

# Services:
# - FastAPI: http://localhost:8000
# - PostgreSQL: localhost:5432
# - ChromaDB: localhost:8001
```

See `docker-compose.yml` for full configuration.

## 📚 Dependencies

### Core

- FastAPI >= 0.100.0
- Pydantic >= 2.0.0
- requests >= 2.31.0
- python-dotenv >= 1.0.0

### RAG

- sentence-transformers >= 2.2.0
- chromadb >= 0.4.0

### Optional

- pytest >= 7.0.0
- pytest-cov >= 4.0.0

Full list in `requirements.txt`

## 🐛 Troubleshooting

### Odoo Connection Error

```
Error connecting to Odoo inventory
```

Check:
- Odoo URL and credentials in `.env`
- Odoo XML-RPC is enabled
- Firewall allows connection

### RAG Not Working

```
RAG retrieval failed: No module named 'sentence_transformers'
```

Install: `pip install sentence-transformers chromadb`

### Telegram Webhook Not Receiving

```
Telegram update ignored: no message field
```

Check:
- Webhook URL is correct and publicly accessible
- Telegram bot is configured with correct webhook URL
- Use ngrok for local development: `ngrok http 8000`

### Memory Issues with Products

```
LRU cache exceeds memory
```

The cache is limited to 128 products + 256 individual lookups. This is configurable in `odoo_service.py`

## 📈 Monitoring

Check service status:

```python
# In Python console or API endpoint
from backend.services.odoo_service import OdooService
from backend.rag.retriever import ProductRetriever

print(OdooService.get_cache_info())
print(ProductRetriever.get_stats())
```

## 📝 License

Proprietary - All rights reserved

## 🤝 Support

For issues or feature requests, contact the development team.

---

**Last Updated**: 2026-06-17
**Version**: 1.0.0 (Production Ready)
