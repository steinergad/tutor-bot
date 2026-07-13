# 🚀 Tutor Bot — Team Setup Guide

## For Your Teammate (5 Minutes Setup)

### **Step 1: Clone the Repository**
```bash
git clone <your-repo-url>
cd tutor-bot
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Configure API Key**
Copy the example file and add your API key:
```bash
cp .env.example .env
```

Then edit `.env` with ONE of these options:

**Option A: GitHub Copilot** (Recommended)
```
GITHUB_TOKEN=github_pat_xxxxxxxxxxxx
```
Get token: https://github.com/settings/tokens → Generate new token (classic)

**Option B: OpenAI API**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```
Get key: https://platform.openai.com/api/keys

**Option C: Local Ollama** (Free)
```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
```
First install: https://ollama.ai and run `ollama pull llama3.2`

### **Step 5: Run the App**
```bash
streamlit run app.py
```

Visit: **http://localhost:8501**

---

## ✨ Features

### **Two Learning Modes**
- **📖 Learn Material** — Study algorithms with AI tutor
- **💪 Solve Homework** — Practice with Socratic guidance (hints only, no answers)

### **5 Weeks of Homework**
- Week 1: Algorithm Analysis & Big O
- Week 2: Greedy & Divide-and-Conquer  
- Week 3: Dynamic Programming
- Week 4: Graph Algorithms (Dijkstra, MST)
- Week 5: Advanced Topics (Max Flow, NP-Completeness)

### **Smart Features**
- ✅ Socratic method (questions instead of answers)
- ✅ Progressive hints (4-5 levels per problem)
- ✅ Cumulative learning (knows what students learned in previous weeks)
- ✅ Curriculum boundaries (enforced topic scoping)
- ✅ Math rendering (KaTeX formulas: $O(n^2)$)

---

## 🎯 Quick Test

**Try This:**
1. Select **💪 Solve Homework**
2. Pick **Week 1: Homework 1**
3. Ask: *"How do I prove n² is O(n²)?"*
4. Bot responds with guiding questions, not answers!

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main application (465 lines) |
| `db/homework.json` | 5 homework assignments with hints |
| `db/metadata.json` | 8 tutorials metadata |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
| `README.md` | Detailed documentation |

---

## 🆘 Troubleshooting

### **"Chat needs an API key"**
→ Check that `.env` file exists and has API key set

### **Port 8501 already in use**
```bash
streamlit run app.py --server.port 8502
```

### **Slow responses**
- Using Ollama? It runs locally (slower than API)
- Using API? Check internet connection
- GitHub Copilot is usually fastest

### **Module not found errors**
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Reinstall
pip install -r requirements.txt
```

---

## 📊 Example Homework Data (Week 1)

```json
{
  "hw_1": {
    "week": 1,
    "title": "Homework 1",
    "problems": 4,
    "description": "Introduction to algorithm analysis and complexity",
    "topics": ["Big O notation", "Asymptotic analysis", "Time complexity"],
    "key_concepts": [
      "Asymptotic notation (Big O, Omega, Theta)",
      "Analyzing algorithms empirically",
      "Identifying growth rates",
      "Proving complexity bounds"
    ],
    "hint_sequence": [
      "Look at the dominant term in the function.",
      "Which term grows fastest as n increases?",
      "Can you find constants c and n₀ to satisfy the definition?",
      "What's the relationship between your constants and the Big O notation?"
    ]
  }
}
```

---

## 🔄 Team Workflow

### **Adding New Homework**
1. Edit `db/homework.json`
2. Add entry: `"hw_6": { ... }`
3. Commit and push
4. Everyone pulls and sees it immediately

### **Customizing Hints**
1. Edit the `hint_sequence` array
2. Make hints more/less specific
3. Everyone benefits from the update

### **Adding Tutorials**
1. Edit `db/metadata.json`
2. Add new tutorial with topics
3. App reloads automatically

---

## 💡 Socratic Guidance Example

**Student asks:** "How do I solve this greedy problem?"

**Bot responds with progressive hints:**

**Hint 1 (Easiest):**
> "Is there a property that makes a local choice globally optimal?"

**Hint 2:**
> "What happens when you pick the item with the earliest finish time?"

**Hint 3:**
> "Can you prove this choice leads to an optimal solution?"

**Hint 4 (Close to answer):**
> "How would you construct the remaining solution after making the greedy choice?"

→ **No direct answer given** — student learns through guided thinking!

---

## ✅ Verification

To verify everything works:
1. Run `streamlit run app.py`
2. Select **💪 Solve Homework**
3. Pick **Week 1**
4. Ask a question
5. Bot responds with guiding questions (not answers)
6. ✅ Success!

---

## 📞 Questions?

Check the full README.md for:
- Detailed feature list
- Customization guide
- Deployment options
- LLM provider comparison
- Security best practices

---

## 🎉 Ready to Go!

Your teammate can now:
1. Clone the repo
2. Run setup (5 minutes)
3. Start tutoring immediately

**No complex configuration needed!**

Happy learning! 🎓
