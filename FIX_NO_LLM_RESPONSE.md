# 🔧 PIPELINE FIX GUIDE - Why App Doesn't Respond

## ✅ What's Working

All components are functional and integrated correctly:
- ✅ Knowledge graph loaded (30 entities, 37 relationships)
- ✅ Homework validation working (English & Hebrew)
- ✅ Prompt system ready (tutorial & homework)
- ✅ Language support active (Hebrew & English)
- ✅ Search system operational
- ✅ Database files present and validated

## ❌ The Problem

**No LLM is configured.** The app needs one of:
1. OpenAI API key (`OPENAI_API_KEY`)
2. GitHub Models token (`GITHUB_TOKEN`)
3. Local Ollama server (`OLLAMA_BASE_URL`)

Without this, the `get_llm()` function has no LLM to call, so it can't generate any responses.

---

## 🚀 SOLUTION 1: Use GitHub Copilot (Fastest - 2 Minutes)

If you're in VS Code with GitHub Copilot, use the free GitHub Models API:

### Step 1: Get GitHub Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `tutor-bot-models`
4. Check scopes: `repo`, `read:user`, `user:email`
5. Click "Generate token"
6. **Copy the token** (starts with `github_pat_...` or `ghp_`)

### Step 2: Set Environment Variable
```bash
# Option A: One-time (for this session only)
$env:GITHUB_TOKEN = "github_pat_YOUR_TOKEN_HERE"

# Option B: Permanent (add to .env file)
echo "GITHUB_TOKEN=github_pat_YOUR_TOKEN_HERE" >> .env
```

### Step 3: Restart Streamlit
```bash
streamlit run app.py
```

✅ **Done!** App will now use GitHub Models (free, part of your Copilot subscription)

---

## 🚀 SOLUTION 2: Use OpenAI API Key

### Step 1: Get OpenAI API Key
1. Go to: https://platform.openai.com/api/keys
2. Click "Create new secret key"
3. **Copy the key** (starts with `sk-`)
4. Save it securely

### Step 2: Set Environment Variable
```bash
# Option A: One-time
$env:OPENAI_API_KEY = "sk-YOUR_KEY_HERE"

# Option B: Permanent (.env file)
echo "OPENAI_API_KEY=sk-YOUR_KEY_HERE" >> .env
```

### Step 3: Restart Streamlit
```bash
streamlit run app.py
```

✅ **Done!** App will now use OpenAI (gpt-4o-mini)

---

## 🚀 SOLUTION 3: Use Local Ollama (Free, No API Key)

### Step 1: Install Ollama
- Download from: https://ollama.ai
- Installation takes ~2 minutes
- Comes with popular open-source models

### Step 2: Start Ollama Server
```bash
# This runs Ollama on http://localhost:11434
ollama serve
```

### Step 3: Download a Model (in another terminal)
```bash
ollama pull llama2  # 4 GB, good balance
# OR
ollama pull mistral  # 5 GB, faster
# OR
ollama pull neural-chat  # 3 GB, optimized for chat
```

### Step 4: Configure in app.py
Edit `app.py`, find this line (around line 270):
```python
return ChatOllama(
    model="llama3.2",  # ← Change to your model
    base_url="http://localhost:11434",
    temperature=0,
)
```

Change `llama3.2` to the model you installed (e.g., `mistral` or `llama2`)

### Step 5: Restart Streamlit
```bash
streamlit run app.py
```

✅ **Done!** App will use local Ollama (completely free, no internet needed)

---

## 📋 Quick Decision Matrix

| Solution | Cost | Setup Time | Speed | Internet |
|----------|------|-----------|-------|----------|
| **GitHub Models** | ✅ Free | 2 min | Fast | Required |
| **OpenAI API** | $ Paid | 1 min | Fast | Required |
| **Ollama Local** | ✅ Free | 10 min | Slow | Not needed |

**Recommendation**: Use **GitHub Models** (free + you already have it)

---

## ✨ Complete Fix Workflow

### Fastest Path (2 minutes):

```bash
# Terminal 1: Stop current app
taskkill /F /IM streamlit.exe

# Terminal 2: Set GitHub token (one-time, this session)
$env:GITHUB_TOKEN = "github_pat_YOUR_TOKEN"

# Terminal 3: Restart app
cd c:\Users\stein\tutor-bot
streamlit run app.py
```

### Permanent Fix (add to .env):

```bash
# Edit or create .env file in c:\Users\stein\tutor-bot\.env
# Add this line:
GITHUB_TOKEN=github_pat_YOUR_TOKEN
```

Then restart Streamlit.

---

## ✅ Verification

After setting the API key, the app will:
1. ✅ Load knowledge graph (shown in console: "✅ Knowledge graph loaded...")
2. ✅ Initialize LLM (no error on startup)
3. ✅ Accept homework questions (Hebrew & English)
4. ✅ Generate Socratic responses with graph context
5. ✅ Show learning paths and prerequisites

---

## 🐛 Troubleshooting

**Issue**: "Error calling the model: Invalid API key"
- **Fix**: Your API key is wrong or expired. Get a new one.

**Issue**: "Error calling the model: Connection refused"
- **Fix**: For Ollama, make sure `ollama serve` is running in another terminal.

**Issue**: "Error calling the model: 401 Unauthorized"
- **Fix**: Your GitHub/OpenAI token is invalid. Re-generate it.

**Issue**: Still no response after setting API key
- **Fix**: Restart Streamlit completely:
  ```bash
  taskkill /F /IM streamlit.exe
  streamlit run app.py
  ```

---

## 🎯 Summary

**Problem**: No LLM provider configured
**Solution**: Set ONE of these environment variables:
- `GITHUB_TOKEN` (recommended - free)
- `OPENAI_API_KEY` (reliable but costs $)
- `OLLAMA_BASE_URL` (free but slow)

**Verification**: Run diagnostic again
```bash
python full_pipeline_diagnostic.py
```

**Expected Output**:
```
7️⃣  CHECKING LLM CONNECTIVITY
   GitHub Models: ✓ (Token configured)
   OR
   OpenAI: ✓ (API key configured)
```

Then the app will respond immediately! 🚀
