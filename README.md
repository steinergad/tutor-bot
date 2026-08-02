# 🎓 Tutor Bot - Local Socratic AI Tutoring System

A **100% local Socratic tutoring chatbot** powered by Ollama + Mistral 7B. No cloud APIs, no internet required for inference. Students learn through guided questioning, not direct answers.

**Version 3.0** — Production Ready | Ollama-powered | Privacy-first

---

## ✨ Key Features

- **Socratic Method**: Asks guiding questions instead of giving answers
- **Completely Local**: Runs entirely on your machine via Ollama + Mistral 7B
- **Real-time Streaming**: Token-by-token response display with thinking indicator  
- **Dual Learning Modes**:
  - 📖 **Learn Mode**: Direct teaching with curriculum context
  - 💪 **Homework Mode**: Socratic questions with scope validation
- **Smart Context**: Knowledge graph + semantic vector search for relevant materials
- **Production Ready**: Tested, documented, ready to deploy

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- Ollama 0.6.2+ ([download](https://ollama.ai))
- 8+ GB RAM (16+ GB recommended)

### Step 1: Download Mistral Model
```powershell
# Install Ollama first, then:
ollama pull mistral      # Downloads 4.4GB model
ollama serve             # Start Ollama server (keep running)
```

### Step 2: Setup Python Environment
```powershell
git clone https://github.com/steinergad/tutor-bot.git
cd tutor-bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Run
```powershell
streamlit run app.py
# Opens http://localhost:8501
```

That's it! No API keys, no configuration needed.

---

## 🏗️ System Architecture

```
Streamlit UI (http://localhost:8501)
    ↓
User Input → Language Processing → Context Retrieval
    ↓
┌──────────────────────────────────────┐
│ Context Sources:                      │
├─ Knowledge Graph (SQLite)            │
│  └─ Curriculum entities & relations  │
├─ Vector Search (Chroma)              │
│  └─ Semantic search on course topics │
├─ Validation (Scope checker)          │
│  └─ Ensure question is on-topic      │
└──────────────────────────────────────┘
    ↓
LangChain → Prompt Building → Message Formatting
    ↓
Ollama (Mistral 7B) → LLM Inference
    ↓
Stream Response ← Token by Token ← Real-time Display
    ↓
Chat History + Math Formatting (KaTeX)
```

### Technology Stack

| Component | Tech | Role |
|-----------|------|------|
| **LLM Engine** | Ollama + Mistral 7B | Local inference, no APIs |
| **Web UI** | Streamlit 1.59.1 | Interactive chat interface |
| **Orchestration** | LangChain 1.3+ | Prompt chains & templating |
| **Knowledge Graph** | SQLite | Curriculum relationships |
| **Vector DB** | Chroma | Semantic search |
| **Embeddings** | all-MiniLM-L6-v2 | Text vectorization |

---

## 📁 Project Structure

```
tutor-bot/
├── app.py                          # Main Streamlit app (850+ lines)
├── requirements.txt                # Dependencies
├── .env.example                    # Config template
│
├── 📂 prompts/
│   ├── prompt_builder.py          # Generates system prompts
│   ├── tutorial_prompt.json       # Learn mode template
│   └── homework_prompt.json       # Homework mode template
│
├── 📂 Core Modules
│   ├── language_config.py         # UI translations
│   ├── homework_validation.py     # Scope validation
│   ├── search_integration.py      # Search API
│   ├── vector_db.py              # Vector database
│   └── graph_rag_starter.py      # Knowledge graph
│
├── 📂 db/
│   ├── metadata.json             # 336 course topics
│   ├── homework.json             # 5 assignments
│   ├── knowledge_graph.db        # SQLite graph
│   └── chroma_vector_store/      # Vector embeddings
│
└── 📂 material/
    ├── english/                  # Course PDFs
    ├── lectures/
    └── hw1/
```

---

## 🎯 How It Works

### Learn Mode Flow
```
Student: "Explain Big O notation"
    ↓
App retrieves: Tutorial 1 topics, related algorithms
    ↓
LLM generates: Clear explanation with examples
    ↓
Response: Tutorial-aware, references learned concepts
```

### Homework Mode Flow
```
Student: "How do I find the time complexity?"
    ↓
App checks: Is this question about current homework?
    ↓
LLM generates: Socratic questions to guide discovery
    ↓
Response: "What operations happen each time we loop?"
          "How many times do we loop through n elements?"
```

---

## ⚙️ Configuration

### Environment File (.env)
```env
# Ollama Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=mistral

# Optional: If you want to switch to a different model later
# OLLAMA_LLM_MODEL=neural-chat    (4GB, faster)
# OLLAMA_LLM_MODEL=phi             (2.6GB, smallest)
```

### Changing Models
```powershell
# Download new model
ollama pull neural-chat

# Update .env
OLLAMA_LLM_MODEL=neural-chat

# Restart app
streamlit run app.py
```

---

## 🎮 Usage Examples

### Example 1: Learn Mode
```
User: "What is time complexity?"

Tutor: "Great question! Time complexity tells us how long an algorithm 
takes to run as the input size grows.

From Tutorial 1, we learned Big O notation helps us analyze this:
- O(n): Linear - looks at each element once
- O(n²): Quadratic - nested loops
- O(log n): Logarithmic - divide and conquer

Can you think of an algorithm that looks at each element once?"
```

### Example 2: Homework Mode  
```
User: "How do I find maximum in an array?"

Tutor: "Good question! Let me guide you step by step.

From Tutorial 1, we learned about basic operations. 
For finding a maximum, think:
1. Do we need to look at EVERY element in the array?
2. How many times do we compare values?

What do you think the time complexity would be?"
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Connection refused"** | Make sure `ollama serve` is running in background |
| **"Module not found"** | Run `pip install -r requirements.txt` |
| **Slow responses (>15s)** | Normal for Mistral on CPU. Try smaller model: `neural-chat` |
| **App won't start** | Kill any old processes: `taskkill /F /IM streamlit.exe` |
| **Knowledge graph not loading** | Run `python build_knowledge_graph.py` |

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **First Response** | 6-8 seconds (Mistral 7B, CPU) |
| **Generation Speed** | ~10-15 tokens/sec |
| **Memory Usage** | 4-6 GB (with Mistral loaded) |
| **Vector Search** | ~50-100ms per query |

**Tips for Better Performance**:
- Use SSD for faster DB access
- Enable GPU in Ollama: `CUDA_VISIBLE_DEVICES=0 ollama serve`
- Switch to smaller model (`neural-chat`, `phi`)

---

## 🔀 Model Options

### Mistral 7B (Current)
- ✅ Best quality responses
- ✅ 4.4 GB  
- ⏱️ 6-8 seconds latency (CPU)
- 📊 Handles English fluently

### Alternatives
```bash
# Faster, smaller, still good
ollama pull neural-chat      # 4GB, 5-6s latency

# Extremely small/fast
ollama pull phi              # 2.6GB, 3-4s latency

# Context-heavy tasks
ollama pull llama2           # 7GB, longer context
```

**To switch**: Edit `.env` → `OLLAMA_LLM_MODEL=neural-chat` → Restart app

---

## 📚 Adding Course Materials

### Add New PDFs
```
1. Place PDF files in material/english/ or material/lectures/
2. Run: python extract_tutorials_pipeline.py
3. Restart the app
```

### Manual Metadata Update
Edit `db/metadata.json` to add topics:
```json
{
  "tutorial_1": {
    "topics": ["Big O", "Time Complexity", "Algorithm Analysis"]
  }
}
```

Rebuild knowledge graph:
```powershell
python build_knowledge_graph.py
```

---

## 🔐 Security & Privacy

✅ **Completely Local**: All processing on your machine  
✅ **No Internet**: No data sent anywhere for inference  
✅ **No Accounts**: No login, no tracking  
✅ **No APIs**: No API keys required  
✅ **Data Stays Local**: Chat history only in Streamlit session  

---

## 📋 System Requirements

| Item | Minimum | Recommended |
|------|---------|-------------|
| **Python** | 3.11 | 3.11+ |
| **RAM** | 8 GB | 16+ GB |
| **Disk** | 500 MB | 1 GB (includes models) |
| **CPU** | Any | Ryzen/Intel current gen |
| **GPU** | N/A | NVIDIA/AMD (10x speedup) |

**Ollama Resources**:
- Mistral 7B: ~4.4 GB
- Vector embeddings: ~80 MB  
- SQLite databases: ~100 MB
- Total: ~5 GB

---

## 📦 Dependencies

All production dependencies in `requirements.txt`:
```
streamlit>=1.59.1
langchain>=1.3
langchain-core>=1.4.9
langchain-ollama>=1.1.0
chromadb>=0.5.0
sentence-transformers>=2.2.0
python-dotenv>=1.0
```

Install: `pip install -r requirements.txt`

---

## 🧪 Testing

```powershell
# Test Ollama connection
python test_ollama_api.py

# Rebuild knowledge graph
python build_knowledge_graph.py

# Full system test
python test_full_system.py
```

---

## 🚀 Deployment

### Local Machine
```powershell
streamlit run app.py
```

### Windows Background Service
```powershell
# Create batch file: start_tutor.bat
@echo off
cd C:\path\to\tutor-bot
.venv\Scripts\activate.bat
streamlit run app.py --server.headless true
```

### Production Considerations
- ✅ Runs offline (no internet needed)
- ✅ Single machine deployment
- ✅ No database sync needed
- ⚠️ UI only: Can't share without running separate instances

---

## 📝 License

MIT License - Free for educational and commercial use

---

## ✅ Status

```
Version:        3.0.0
Status:         ✅ Production Ready
Last Updated:   2026-08-02
LLM:            Mistral 7B via Ollama
Python:         3.11.9
```

---

## 🤝 Support

- **Ollama Issues**: https://github.com/ollama/ollama
- **Streamlit Help**: https://docs.streamlit.io
- **LangChain Docs**: https://docs.langchain.com

---

**Happy Learning! 🚀**
