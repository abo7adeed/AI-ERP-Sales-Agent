# QUICK START GUIDE

## 🚀 Get Started in 5 Minutes

### Option 1: Local Development (Fastest)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and fill in your details:
#    - ODOO_URL, ODOO_DB, credentials
#    - TELEGRAM_BOT_TOKEN
#    - Choose one LLM: LOCAL_LLM_URL or GROQ_API_KEY

# 3. Install dependencies
pip install -r requirements.txt
pip install sentence-transformers chromadb  # For RAG

# 4. Run the server
python -m uvicorn backend.main:app --reload

# 5. Test the API
curl http://localhost:8000/

# 6. Post a chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "السلام عليكم، أريد موبايل أيفون",
    "customer_name": "أحمد علي",
    "customer_phone": "+201001234567",
    "provider": "local"
  }'
```

### Option 2: Docker (Production)

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env with your values

# 2. Start all services
docker-compose up

# 3. API is at http://localhost:8000

# To stop
docker-compose down
```

### Option 3: Docker with Ollama (Local LLM)

```bash
# Start with Ollama support
docker-compose --profile with-ollama up

# In another terminal, pull a model:
docker exec mobile_ai_bot_ollama ollama pull mistral

# API ready at http://localhost:8000
```

---

## 🧪 Run Tests

```bash
# Test conversation memory
python test_phase1.py

# Test JSON parser
python test_json_parser.py

# Test agent context
python test_agent.py

# Test Odoo service (mocked)
python test_odoo.py
```

All tests should show `[OK] ALL TESTS PASSED!`

---

## 📚 Key Files to Know

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application & endpoints |
| `backend/agent/sales_agent.py` | Core agent logic |
| `backend/services/odoo_service.py` | Odoo integration & caching |
| `backend/rag/retriever.py` | Semantic product search |
| `backend/agent/conversation_manager.py` | Message history |
| `README.md` | Full documentation |
| `.env.example` | Configuration template |
| `docker-compose.yml` | Docker setup |

---

## 🔑 Configuration

### Minimal `.env` for Local LLM

```
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

TELEGRAM_BOT_TOKEN=your_token_here

LOCAL_LLM_URL=http://localhost:11434/api/generate
LOCAL_MODEL_NAME=mistral
```

### Using Groq Instead

```
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL_NAME=mixtral-8x7b-32768
```

### Using Gemini Instead

```
GEMINI_API_KEY=AIza_your_key_here
GEMINI_MODEL_NAME=gemini-pro
```

---

## 🌐 API Endpoints

### Health Check
```
GET /
→ {"status": "online", "message": "..."}
```

### Chat API
```
POST /api/chat
{
  "message": "User message",
  "customer_name": "Customer Name",
  "customer_phone": "+201001234567",
  "provider": "local"  # or groq, gemini
}
→ {"response": "Bot response", "status": "success"}
```

### Telegram Webhook
```
POST /api/telegram/webhook
(Auto-configured by Telegram)
→ {"status": "success"}
```

---

## 📁 Data Storage

### Conversation History
```
data/conversations/
├── 123456789.json    # Telegram chat_id
├── user_2.json
└── ...

Each file: [{"role": "user", "content": "...", "timestamp": "..."}, ...]
```

### Vector Store
```
data/vector_store/
├── duckdb_metadata.db
└── data.parquet
(ChromaDB stores product embeddings here)
```

### Product Catalog
```
data/products_catalog.json
(8 sample products with metadata)
```

---

## 🔍 Features You Get

✅ **Conversation Memory** - Remembers last 5 messages  
✅ **Semantic Search** - Finds products by meaning  
✅ **Odoo Integration** - Real-time inventory  
✅ **Multiple LLMs** - Local, Groq, or Gemini  
✅ **Telegram Bot** - Direct messaging  
✅ **REST API** - For integrations  
✅ **Production Ready** - Docker, tests, docs  

---

## ⚡ Performance Tips

- **Caching**: Product list cached in memory (LRU)
- **Persistence**: Conversation history in JSON files
- **Vectorization**: ChromaDB for fast semantic search
- **Async**: FastAPI handles concurrent requests

---

## 🆘 Troubleshooting

### "Error connecting to Odoo"
- Check ODOO_URL in `.env`
- Verify Odoo is running on that port
- Check credentials are correct

### "No response from LLM"
- For local: Start Ollama with `ollama serve`
- For Groq: Verify API key is valid
- For Gemini: Check API key and quotas

### "RAG not working"
- Run: `pip install sentence-transformers chromadb`
- Check `data/products_catalog.json` exists
- Clear cache: Delete `data/vector_store/`

### "Telegram not receiving messages"
- Use ngrok to expose local: `ngrok http 8000`
- Set webhook URL with Telegram
- Check bot token in `.env`

---

## 📖 Next Steps

1. Read `README.md` for full documentation
2. Explore `backend/` directory structure
3. Check test files for usage examples
4. Review Pydantic models in `backend/models/`
5. Modify `data/products_catalog.json` with your products

---

## 💡 Example Conversation Flow

**User**: "السلام عليكم، أريد موبايل اقتصادي"  
↓  
**Bot** (fetches):
- Previous 5 messages from memory
- Relevant products via RAG semantic search
- Current Odoo inventory

**Bot** (generates):
- Response with available options using LLM
- Offers iPhone 13 or Samsung Galaxy A13

**User**: "الآيفون 13 بكام؟"  
↓  
**Bot**: "السعر 3500 جنيه"

**User**: "تمام، حجز لي واحد"  
↓  
**Bot** (executes):
- Extracts create_order action from LLM response
- Creates customer in Odoo
- Creates quotation
- Returns: "تم حجز الآيفون 13 برقم SO0001"

---

## 📞 Support Resources

- Full docs: `README.md`
- Architecture: See ASCII diagram in `README.md`
- Code examples: Check `test_*.py` files
- API reference: Pydantic models in `backend/models/`
- Setup troubleshooting: `README.md` → Troubleshooting

---

**Ready? Start with:**
```bash
cp .env.example .env
# Edit .env
python -m uvicorn backend.main:app --reload
```

Enjoy! 🚀
