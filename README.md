# 🎓 Socratic Algorithm Tutor with Homework Guidance

An interactive tutoring system for teaching algorithms through Streamlit, featuring:
- **Learn Mode**: 8 algorithm tutorials with curriculum-enforced boundaries
- **Homework Mode**: 5 weeks of assignments with Socratic guidance (hints, not answers)
- **Multiple LLM Backends**: GitHub Copilot, OpenAI, or local Ollama
- **Math Support**: Full KaTeX rendering for equations
- **Minimal Stack**: No vector databases, embeddings, or external dependencies

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.11+
- GitHub token (or OpenAI API key)

### 2. Setup
```bash
cd C:\Users\stein\tutor-bot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure API
```bash
# GitHub Copilot (recommended)
$env:GITHUB_TOKEN = "your-github-pat-here"

# OR OpenAI
$env:OPENAI_API_KEY = "sk-proj-..."
```

### 4. Run
```bash
streamlit run app.py
# Opens http://localhost:8501/
```

---

## 📚 Core Features

### **Learn Material Mode** (Tutorials 1-8)
- 8 algorithm tutorials covering complexity, sorting, DP, graphs, etc.
- Topics are cumulative (T1: 18 topics → T8: 67 total topics)
- Curriculum enforcement: Students can't ask about topics not yet covered
- Clear explanations with course material injection

**Example**:
```
Student (T1): "What is Dijkstra's algorithm?"
Bot: "We haven't covered Dijkstra's algorithm yet. 
     Based on what we've studied, I can help with: 
     [suggests T1 topics]"

Student (T8): "What is Dijkstra's algorithm?"
Bot: "Dijkstra's algorithm finds the shortest path... [full explanation]"
```

### **Solve Homework Mode** (Weeks 1-5)
- 5 weeks of homework assignments with progressive difficulty
- Socratic method: Guide students, never give direct answers
- Progressive hints: Questions that guide toward solution
- Key concepts: Remind students what's relevant
- No pseudocode or solutions revealed

**Example**:
```
Student: "How do I prove n² is O(n²)?"
Bot: "Good question! Can you recall what the formal definition 
     of O(f(n)) is? Once we have that, we can apply it."

Student: "f(n) ≤ c·g(n) for some constants c and n₀?"
Bot: "Exactly! So for O(n²), you need to find constants c and n₀ 
     such that n² ≤ c·n². What values of c and n₀ work?"
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│          STREAMLIT WEB UI                        │
│  (Mode selector, tutorial dropdown, chat)        │
└──────────────┬───────────────────────────────────┘
               │
       ┌───────▼──────────┐
       │ metadata.json    │
       │ homework.json    │
       └───────┬──────────┘
               │
       ┌───────▼──────────────────┐
       │ LangChain Pipeline       │
       │ (Prompts, Chat History)  │
       └───────┬──────────────────┘
               │
        ┌──────▼────────┐
        │ ChatGPT 4o    │
        │ (via GitHub   │
        │  Copilot)     │
        └───────────────┘
```

**No Vector Database**: Material is pre-indexed in JSON files. Direct metadata search is sufficient for curriculum-bounded learning.

---

## 📁 Project Structure

```
tutor-bot/
├── app.py                              # Main Streamlit app (465 lines)
├── requirements.txt                    # Dependencies (6 packages)
├── .env.example                        # Configuration template
│
├── db/
│   ├── metadata.json                   # Tutorial topics (8 tutorials, 67 cumulative topics)
│   ├── homework.json                   # Homework assignments (5 weeks)
│   └── tutorial_*/                     # Chroma vector stores (from pipeline)
│
├── prompts/                            # ✨ NEW: Configurable prompts
│   ├── tutorial_prompt.json            # System prompt for Learn mode
│   ├── homework_prompt.json            # System prompt for Homework mode
│   ├── prompt_builder.py               # Load & build prompts
│   └── README.md                       # Prompt customization guide
│
├── extract_homework.py                 # Homework PDF extraction pipeline
├── extract_tutorials_pipeline.py       # Tutorial PDF → text extraction
├── process_with_llm.py                 # Topic indexing via LLM
├── transform_to_metadata.py            # Transform to metadata.json
│
├── tutorials_auto_discovery.py         # ✨ NEW: Auto-detect new tutorials
├── test_search_comparison.py           # ✨ NEW: Compare search methods
│
└── [docs & guides]
    ├── README.md
    ├── START_HERE.md
    ├── SETUP_GUIDE.md
    ├── HOMEWORK_GUIDE.md
    └── [6 more guides]
```

---

## 🔄 Data Pipeline

For adding new tutorials (optional):

```bash
# Stage 1: Extract PDFs → Text
python extract_tutorials_pipeline.py

# Stage 2: Index topics with LLM
python process_with_llm.py
python process_failed_tutorials.py  # For large PDFs (T6-T7)

# Stage 3: Transform to metadata
python transform_to_metadata.py
```

**Auto-Discovery** (NEW): Drop files in `tutorials/` folder:
```bash
cp my_tutorial.pdf tutorials/tutorial_9.pdf
python tutorials_auto_discovery.py scan
# Automatically processes and updates metadata!
```

---

## ⚙️ Configuration

### System Prompts
Edit prompts without code changes:

```bash
# Tutorial teaching style
nano prompts/tutorial_prompt.json

# Homework Socratic method
nano prompts/homework_prompt.json

# Uses in app.py:
from prompts import build_tutorial_prompt, build_homework_prompt
```

### Environment Variables
```bash
GITHUB_TOKEN       # Recommended: GitHub Copilot PAT
OPENAI_API_KEY     # Alternative: OpenAI key
OLLAMA_LLM_MODEL   # Optional: local Ollama model
OLLAMA_BASE_URL    # Optional: Ollama endpoint
```

---

## 🧪 Testing & Optimization

### Compare Search Methods
Test metadata.json vs vector database (RAG):

```bash
python test_search_comparison.py

# Evaluates:
# - Accuracy (precision, recall, F1)
# - Latency
# - Resource usage
# Compares 15 standard questions
```

### Prompt A/B Testing
```python
from prompts.prompt_builder import build_tutorial_prompt
import copy

# Create variant A (strict boundary)
# Create variant B (helpful boundary)
# Test both with students
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| App startup | <3s |
| Response time | 3-10s (streaming) |
| Memory usage | ~200MB |
| Dependencies | 6 packages |
| Heavyweight components | None |

---

## ❓ FAQ

**Q: Can I add more tutorials?**
A: Yes! Drop PDF in `tutorials/` folder and run `tutorials_auto_discovery.py scan`

**Q: How do I change the teaching style?**
A: Edit `prompts/tutorial_prompt.json` or `prompts/homework_prompt.json`

**Q: Why no vector database?**
A: Material is pre-indexed. Direct metadata search is fast & sufficient. Run `test_search_comparison.py` to compare both methods.

**Q: Can I use a local LLM?**
A: Yes. Install Ollama, set `OLLAMA_LLM_MODEL` and `OLLAMA_BASE_URL`

**Q: What about PDF math extraction?**
A: See `extract_homework.py` docstring for 3 options (easy to hard). Currently uses text extraction.

**Q: How is the homework Socratic method enforced?**
A: System prompt with explicit DON'Ts: "Never give answers directly". Hints guide toward solution step-by-step.

---

## 🎓 How It Works

### Learn Material Mode
1. Student selects tutorial (1-8)
2. App loads cumulative topic list (all topics up to selected tutorial)
3. LLM receives:
   - System prompt: topic whitelist + teaching guidelines
   - Chat history
   - Student question
4. LLM responds within curriculum boundaries

### Solve Homework Mode
1. Student selects week (1-5)
2. App loads concepts from weeks 1 through selected week
3. LLM receives:
   - System prompt: Socratic method (guide, don't answer)
   - Key concepts for this homework
   - Progressive hint sequence
4. LLM guides toward solution without revealing it

---

## 📈 Future Improvements

- [ ] Automated vector DB comparison framework
- [ ] Prompt versioning & A/B testing dashboard
- [ ] Student progress tracking
- [ ] Hint level progression (1-5 difficulty)
- [ ] Deployment to Streamlit Cloud
- [ ] Multi-language support
- [ ] Code debugging mode (in addition to conceptual learning)

---

## 📋 Documentation

- **START_HERE.md** — 60-second quick start
- **SETUP_GUIDE.md** — Detailed team setup
- **HOMEWORK_GUIDE.md** — Student guide for homework mode
- **prompts/README.md** — Customizing system prompts
- **GIT_DEPLOYMENT.md** — Deploying to GitHub

---

**Status**: Production Ready ✓
**Last Updated**: July 13, 2026
**Maintainer**: Course Team
**License**: MIT
