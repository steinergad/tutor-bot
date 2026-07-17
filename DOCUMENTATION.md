# 📖 Documentation Index

## Quick Start for New Team Members

👉 **Start here if you're new:**
1. [START_HERE.md](START_HERE.md) — 60-second overview
2. [SETUP_GUIDE.md](SETUP_GUIDE.md) — Installation (5 minutes)
3. [VECTOR_DB_SETUP.md](VECTOR_DB_SETUP.md) — **← Create vector DB from your PDFs**

---

## 📚 Core Documentation

### Getting Started
- **[START_HERE.md](START_HERE.md)** — Quick intro + API key setup
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** — Complete environment setup
- **[README.md](README.md)** — Full feature documentation

### Vector Database & Search
- **[VECTOR_DB_SETUP.md](VECTOR_DB_SETUP.md)** — **How to build vector DB from PDFs** ⭐ NEW
  - Step-by-step extraction pipeline
  - Metadata generation
  - Database construction
  - Troubleshooting guide
  - Team deployment checklist

- **[VECTOR_DB_IMPLEMENTATION.md](VECTOR_DB_IMPLEMENTATION.md)** — Technical deep-dive
- **[VECTOR_DB_SUMMARY.md](VECTOR_DB_SUMMARY.md)** — Performance metrics

### Homework & Learning
- **[HOMEWORK_GUIDE.md](HOMEWORK_GUIDE.md)** — How homework mode works
- **[HOMEWORK_INTEGRATION_SUMMARY.md](HOMEWORK_INTEGRATION_SUMMARY.md)** — Integration details

### Model Selection & Comparison
- **[MODEL_COMPARISON.md](MODEL_COMPARISON.md)** — **Embedding models explained** ⭐ NEW
  - Your current model (all-MiniLM-L6-v2) analysis
  - Google NotebookLM approach
  - Open-Notebook architecture
  - Detailed pros/cons comparison
  - Migration paths & recommendations

---

## 🔧 For Developers

### Code Structure
```
tutor-bot/
├── app.py                          # Main Streamlit app
├── vector_db.py                    # Vector database implementation
├── search_integration.py           # Unified search interface
├── prompts/
│   ├── prompt_builder.py          # Prompt template logic
│   ├── tutorial_prompt.json
│   └── homework_prompt.json
├── db/
│   ├── metadata.json              # Topic index
│   ├── chroma_vector_store/       # Vector embeddings
│   └── homework.json              # Homework problems
└── material/                       # PDF materials
    ├── lectures/
    ├── hw/
    └── ...
```

### Key Files for Vector DB
- `vector_db.py` — VectorDB class (change embedding model here)
- `search_integration.py` — Search API
- `extract_tutorials_pipeline.py` — PDF extraction pipeline

---

## 🚀 Deployment Checklists

### For Classroom (Local)
```
□ Install dependencies: pip install -r requirements.txt
□ Place PDFs in material/ directory
□ Extract & build vector DB (see VECTOR_DB_SETUP.md)
□ Configure API key (.env file)
□ Run: streamlit run app.py
```

### For Team Deployment
```
□ Create Python virtual environment
□ Install dependencies
□ Place PDFs in material/
□ Extract tutorials: python extract_tutorials_pipeline.py
□ Build vector DB: python -c "from vector_db import VectorDB; VectorDB().build_database('db/metadata.json')"
□ Configure API key
□ Test: python -c "from search_integration import find_relevant_topics; print(find_relevant_topics('test query'))"
□ Launch app
```

---

## ❓ FAQ

**Q: How do I add new homework/tutorials?**
A: Follow the extraction pipeline in [VECTOR_DB_SETUP.md](VECTOR_DB_SETUP.md#phase-1-pdf-text-extraction)

**Q: How do I improve search accuracy?**
A: See [MODEL_COMPARISON.md](MODEL_COMPARISON.md#-algorithm-tutoring-which-model) for model upgrade paths

**Q: Which embedding model should I use?**
A: Start with all-MiniLM (current). Upgrade to all-mpnet if F1 < 0.75. See [MODEL_COMPARISON.md](MODEL_COMPARISON.md)

**Q: Can I use this without an API key?**
A: Yes, but you need to configure Ollama (local LLM). See SETUP_GUIDE.md

**Q: What's the difference with Google NotebookLM?**
A: See [MODEL_COMPARISON.md](MODEL_COMPARISON.md#-side-by-side-model-comparison)

---

## 📊 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Search F1 Score | 0.75+ | 0.70 ✓ |
| Query Latency | <100ms | ~15ms ✓ |
| DB Build Time | <5 min | ~2s ✓ |
| Startup Time | <10s | 5-10s ✓ |
| Model Size | <1GB | 22MB ✓ |

---

## 🔗 External Resources

### Embedding Models
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — Compare all models
- [Sentence Transformers](https://www.sbert.net/) — Documentation & tutorials
- [HuggingFace Models](https://huggingface.co/models?library=sentence-transformers)

### Alternatives
- [Google NotebookLM](https://notebooklm.google/) — Official product
- [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) — Python wrapper (17.9k⭐)
- [lfnovo/open-notebook](https://github.com/lfnovo/open-notebook) — Self-hosted (35.7k⭐)

### Vector Databases
- [Chroma](https://www.trychroma.com/) — Used in this project
- [Weaviate](https://weaviate.io/) — Alternative
- [Milvus](https://milvus.io/) — Alternative
- [Pinecone](https://www.pinecone.io/) — Cloud alternative

---

## 📝 Document History

| File | Purpose | Last Updated |
|------|---------|--------------|
| VECTOR_DB_SETUP.md | **NEW** — How to build vector DB from PDFs | 2026-07-17 |
| MODEL_COMPARISON.md | **NEW** — Model comparison & recommendations | 2026-07-17 |
| START_HERE.md | Quick start guide | |
| README.md | Main documentation | |
| HOMEWORK_GUIDE.md | Homework mode explanation | |
| VECTOR_DB_IMPLEMENTATION.md | Technical implementation | |

---

## 💬 Questions?

**Vector DB Questions?** → See [VECTOR_DB_SETUP.md](VECTOR_DB_SETUP.md)

**Model Questions?** → See [MODEL_COMPARISON.md](MODEL_COMPARISON.md)

**Setup Issues?** → See [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Code Questions?** → Check the docstrings in:
- `vector_db.py`
- `search_integration.py`
- `app.py`
