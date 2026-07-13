# 🎓 Socratic Algorithm Tutor — Start Here

**Your teammate's first-time experience:**

## ⚡ 60-Second Setup

```bash
# 1. Clone
git clone <repo-url>
cd tutor-bot

# 2. Environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Dependencies
pip install -r requirements.txt

# 4. API Key
cp .env.example .env
# Edit .env: Add GITHUB_TOKEN or OPENAI_API_KEY

# 5. Run
streamlit run app.py
```

**Opens at:** http://localhost:8501

---

## 📚 What You Get

### **📖 Learn Material Mode**
- 8 tutorial topics
- Full explanations
- Curriculum-bounded (can't learn ahead)
- Example: "Big O notation", "Dynamic Programming", "Graph Algorithms"

### **💪 Solve Homework Mode**
- 5 weeks of homework (with 4 problems each)
- Socratic guidance (hints, NOT answers)
- Progressive difficulty
- Week 1→5: Builds on previous concepts

---

## 🎯 Try It Now

1. Select **💪 Solve Homework**
2. Pick **Week 1: Homework 1**
3. Ask: *"How do I prove n² is O(n²)?"*
4. Bot responds: *"What do you think Big O notation measures?"*
5. Notice: **No direct answer!** Just guided questions.

That's the Socratic method in action! 🎓

---

## 🔑 API Key (Pick One)

### **Option A: GitHub Copilot** ⭐ Recommended
```
GITHUB_TOKEN=github_pat_xxxxxxxxxxxx
```
Get it: https://github.com/settings/tokens

### **Option B: OpenAI**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```
Get it: https://platform.openai.com/api/keys

### **Option C: Local Ollama** (Free & Offline)
```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
```
Setup: Download https://ollama.ai, then `ollama pull llama3.2`

---

## 📖 Documentation

| File | Purpose |
|------|---------|
| **SETUP_GUIDE.md** | ← Read this first (5 min setup) |
| **README.md** | Full feature documentation |
| **HOMEWORK_GUIDE.md** | How homework mode works |
| **GIT_DEPLOYMENT.md** | For team deployments |

---

## 🚨 Common Issues

**"Chat needs an API key"**
→ Check `.env` file has API key set

**Port 8501 already in use**
→ `streamlit run app.py --server.port 8502`

**Slow responses**
→ Using Ollama? It's local (normal slowness). Try GitHub Copilot for faster responses.

**Module not found**
→ Did you run `pip install -r requirements.txt`?

---

## ✨ Key Features

✅ **Socratic Method** — Guides students, never gives answers directly
✅ **5 Weeks of Homework** — Progressive difficulty, cumulative learning
✅ **8 Tutorials** — Teach algorithm concepts
✅ **Math Rendering** — Formulas display beautifully ($O(n^2)$)
✅ **Multiple LLMs** — GitHub Copilot, OpenAI, or local Ollama
✅ **Clean UI** — Modern Streamlit interface
✅ **Zero Config** — Just add your API key, run!

---

## 📊 Data Structure

### **5 Homework Weeks**
- Week 1: Algorithm Analysis (Big O)
- Week 2: Greedy Algorithms & Divide & Conquer
- Week 3: Dynamic Programming
- Week 4: Graph Algorithms (Dijkstra, MST)
- Week 5: Advanced Topics (Max Flow, NP-Completeness)

### **8 Tutorials**
- Intro to Algorithm Analysis
- Greedy Algorithms
- Divide and Conquer
- Dynamic Programming
- Graph Algorithms Intro
- Shortest Paths
- Minimum Spanning Trees
- And more...

---

## 🎯 Example Workflow

**Day 1: Learn Concepts**
```
Select: 📖 Learn Material
Pick: Tutorial 1 - Algorithm Analysis
Study: Big O notation, asymptotic analysis
Ask bot: Questions about concepts
```

**Day 2: Solve Homework**
```
Select: 💪 Solve Homework
Pick: Week 1 - Homework 1
Try: Solving the problems
Ask bot: Hints and guidance
→ Bot uses hint sequences, never gives answer
```

**Result:** Student learns by doing! 🎓

---

## 📁 Project Structure

```
tutor-bot/
├── app.py                 ← Main app (start here to understand)
├── requirements.txt       ← Dependencies (pip install)
├── .env.example          ← Config template (copy & edit)
├── db/
│   ├── homework.json     ← 5 weeks of homework + hints
│   └── metadata.json     ← 8 tutorials + topics
├── README.md             ← Full documentation
├── SETUP_GUIDE.md        ← Quick setup (you are here!)
└── [other docs]
```

---

## 🎓 How Socratic Guidance Works

**Student:** "How do I solve this?"

**Bot gives 4 progressive hints:**

1️⃣ **Hint 1 (Easy)** — What algorithm have we learned?
2️⃣ **Hint 2 (Moderate)** — How would you break this down?
3️⃣ **Hint 3 (Specific)** — Try thinking about this part...
4️⃣ **Hint 4 (Close)** — What if you used this technique?

→ **Student figures out the answer themselves!** ✅

---

## 🔐 Security

- ✅ `.env` file is local only (not in Git)
- ✅ `.env.example` has no real secrets
- ✅ API keys stay on your machine
- ✅ No data leaves except to LLM API

---

## 🚀 Ready to Start?

```bash
streamlit run app.py
```

Then open: **http://localhost:8501**

**Choose a mode and start learning!** 🎓

---

## 💬 Questions?

Check the detailed guides:
- **Setup issues?** → SETUP_GUIDE.md
- **Feature details?** → README.md  
- **How homework works?** → HOMEWORK_GUIDE.md
- **Deployment?** → GIT_DEPLOYMENT.md

---

## 🎉 Welcome to the Socratic Tutor!

Enjoy building smarter students through guided problem-solving! 🎓✨

---

**Next step:** Read SETUP_GUIDE.md for detailed setup instructions
