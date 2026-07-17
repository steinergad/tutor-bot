# 🗂️ Vector Database Setup Guide

This guide explains how to create and build the vector database for the Socratic Algorithm Tutor from scratch, using your homework and material PDFs.

---

## 📋 Overview

The vector database powers semantic search in the tutor bot. It converts your PDFs into embeddings (numerical vectors) so the system can find contextually relevant topics when students ask questions.

**Current Setup:**
- **Vector DB**: Chroma (persistent local storage)
- **Embedding Model**: all-MiniLM-L6-v2 (384-dim, 22MB)
- **Search Method**: Cosine similarity
- **Performance**: ~15ms per query, F1 score ≈ 0.70

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Prepare Your PDFs

Place your homework and material PDFs in this structure:
```
tutor-bot/
├── material/
│   ├── lectures/
│   │   ├── lecture_1.pdf
│   │   ├── lecture_2.pdf
│   │   └── ...
│   └── hw/
│       ├── homework_week1.pdf
│       ├── homework_week2.pdf
│       └── ...
└── db/
    └── (vector database will be created here)
```

### Step 2: Run the Ingest Script

```bash
python extract_tutorials_pipeline.py
```

This will:
1. Extract text from all PDFs
2. Generate a `metadata.json` with indexed topics
3. Save raw text to `raw_tutorial_texts/`

### Step 3: Build Vector Database

```bash
python -c "
from vector_db import VectorDB
vdb = VectorDB()
vdb.build_database('db/metadata.json')
print('✓ Vector database built successfully!')
"
```

**That's it!** Your vector DB is ready. The app will use it automatically.

---

## 📚 Detailed Setup (Step-by-Step)

### Phase 1: PDF Text Extraction

#### Option A: Use Existing Pipeline (Recommended)

```bash
python extract_tutorials_pipeline.py
```

This script:
- Scans `material/` directory
- Extracts text from each PDF using PyPDF2
- Saves raw text to `raw_tutorial_texts/` for inspection
- Outputs character/line counts

**Output:**
```
tutorial_1.txt: 45,234 characters, 1,203 lines
tutorial_2.txt: 52,109 characters, 1,456 lines
...
```

#### Option B: Custom PDF Processing

If you have a different structure, create `extract_custom.py`:

```python
import PyPDF2
import json
from pathlib import Path

def extract_pdf(pdf_path):
    """Extract text from a single PDF"""
    text = []
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text())
    return "\n".join(text)

# Extract all PDFs
materials = {}
for pdf in Path("material").glob("**/*.pdf"):
    materials[pdf.stem] = extract_pdf(pdf)

# Save extracted texts
for name, text in materials.items():
    Path(f"raw_tutorial_texts/{name}.txt").write_text(text)

print(f"✓ Extracted {len(materials)} PDFs")
```

---

### Phase 2: Generate Metadata

The metadata file defines what topics exist in your curriculum. It should look like:

```json
{
  "tutorial_1": {
    "display_name": "Tutorial 1: Algorithm Analysis",
    "topics": [
      "Big O Notation",
      "Time Complexity",
      "Space Complexity",
      "Asymptotic Analysis",
      "Worst-Case Analysis"
    ]
  },
  "tutorial_2": {
    "display_name": "Tutorial 2: Divide and Conquer",
    "topics": [
      "Merge Sort",
      "Quick Sort",
      "Binary Search",
      "Recurrence Relations"
    ]
  }
}
```

#### Option A: Auto-Generate with LLM (Recommended)

```python
"""
extract_topics_with_llm.py
Uses OpenAI/Claude to intelligently extract topics from your PDFs
"""

import json
import os
from pathlib import Path
from openai import OpenAI  # or use langchain

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_topics_from_text(text, tutorial_name):
    """Use LLM to intelligently extract topics"""
    
    prompt = f"""
    Analyze this tutorial text and extract 10-15 key topics/concepts.
    Return as a JSON array of strings.
    
    Text (first 2000 chars):
    {text[:2000]}
    
    Return ONLY valid JSON array, no markdown:
    ["Topic 1", "Topic 2", ...]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    topics = json.loads(response.choices[0].message.content)
    return topics

# Process all raw texts
metadata = {}
for txt_file in Path("raw_tutorial_texts").glob("*.txt"):
    text = txt_file.read_text()
    tutorial_id = txt_file.stem
    
    topics = extract_topics_from_text(text, tutorial_id)
    
    metadata[tutorial_id] = {
        "display_name": tutorial_id.replace("_", " ").title(),
        "topics": topics
    }
    
    print(f"✓ {tutorial_id}: {len(topics)} topics extracted")

# Save metadata
Path("db/metadata.json").write_text(json.dumps(metadata, indent=2))
print("\n✓ metadata.json saved")
```

**Run it:**
```bash
OPENAI_API_KEY=sk-... python extract_topics_with_llm.py
```

#### Option B: Manual Definition

Simply edit `db/metadata.json` directly:

```bash
# Create directory
mkdir -p db

# Create metadata.json with your topics
cat > db/metadata.json << 'EOF'
{
  "homework_week1": {
    "display_name": "Week 1: Arrays & Complexity",
    "topics": ["Array Basics", "Big O", "Sorting"]
  },
  "homework_week2": {
    "display_name": "Week 2: Recursion",
    "topics": ["Recursion", "Backtracking", "Recurrence"]
  }
}
EOF
```

---

### Phase 3: Build Vector Database

Once you have `db/metadata.json`, build the embeddings:

```bash
python -c "
from vector_db import VectorDB

print('[1/3] Initializing embedding model...')
vdb = VectorDB(
    db_path='db/chroma_vector_store',
    model_name='all-MiniLM-L6-v2'  # or 'all-mpnet-base-v2' for higher accuracy
)

print('[2/3] Building database from metadata.json...')
vdb.build_database('db/metadata.json')

print('[3/3] Verifying...')
results = vdb.search('How do I sort an array?', top_k=3)
print(f'✓ Search test successful!')
print(f'Found topics: {[t[0] for t in results[\"topics\"]]}')
"
```

**Expected output:**
```
[1/3] Initializing embedding model...
[VectorDB] Loading embedding model: all-MiniLM-L6-v2...
[VectorDB] Initializing Chroma at db/chroma_vector_store...

[2/3] Building database from metadata.json...
[VectorDB] Building from db/metadata.json...
[VectorDB] Encoding 42 topics to embeddings...
Batches: 100%|████| 2/2

[3/3] Verifying...
✓ Search test successful!
Found topics: ['Sorting', 'Time Complexity', 'Divide and Conquer']
```

---

## 🔧 Advanced Configuration

### Use a Different Embedding Model

```python
from vector_db import VectorDB

# Option 1: Higher accuracy (slower)
vdb = VectorDB(model_name="all-mpnet-base-v2")  # F1 ≈ 0.80, 200ms

# Option 2: Better for algorithm-specific content
vdb = VectorDB(model_name="sentence-transformers/all-distilroberta-v1")  # F1 ≈ 0.75

# Option 3: State-of-the-art (if you have GPU)
vdb = VectorDB(model_name="sentence-transformers/e5-large-v2")  # F1 ≈ 0.85
```

### Rebuild Database (Clear Old Embeddings)

```bash
# Remove old database
rm -rf db/chroma_vector_store

# Rebuild
python -c "from vector_db import VectorDB; VectorDB().build_database('db/metadata.json')"
```

### Test Search Quality

```python
from vector_db import VectorDB
from search_integration import find_relevant_topics

vdb = VectorDB()
vdb.build_database('db/metadata.json')

# Test queries
test_queries = [
    "How does sorting work?",
    "What is dynamic programming?",
    "Explain recursion",
    "Big O notation",
]

for query in test_queries:
    results = find_relevant_topics(query, top_k=3)
    print(f"\nQ: {query}")
    for topic, score, tutorial in results:
        print(f"  → {topic} (score: {score:.3f})")
```

---

## 📊 Troubleshooting

### "vector DB not available"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

Or specifically:
```bash
pip install chromadb sentence-transformers langchain-chroma
```

### "metadata.json not found"

**Solution:** Ensure `db/metadata.json` exists
```bash
# Check
ls -la db/metadata.json

# If missing, create it
mkdir -p db
# Then run extraction pipeline
```

### Search returns no results

**Solution:** Rebuild the vector database
```bash
rm -rf db/chroma_vector_store
python extract_tutorials_pipeline.py  # Regenerate metadata
python -c "from vector_db import VectorDB; VectorDB().build_database('db/metadata.json')"
```

### Slow search performance

**Solution:** Check your model size
```python
from vector_db import VectorDB

# Switch to faster model
vdb = VectorDB(model_name="all-MiniLM-L6-v2")  # Fast (100ms)

# Avoid these for production (too slow)
# vdb = VectorDB(model_name="all-mpnet-base-v2")  # Slow (200ms)
```

---

## 🎯 For Your Team

### To Deploy on Their Machines:

1. **Prerequisites:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Mac/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Vector DB (2 options):**

   **Option A: Rebuild from PDFs (faster setup)**
   ```bash
   # Place PDFs in material/ directory
   python extract_tutorials_pipeline.py
   python -c "from vector_db import VectorDB; VectorDB().build_database('db/metadata.json')"
   ```

   **Option B: Use pre-built DB (if you shared it)**
   ```bash
   # Just extract the db/ folder from zip
   unzip tutor-bot-with-db.zip
   cd tutor-bot
   ```

4. **Run App:**
   ```bash
   streamlit run app.py
   ```

---

## 📈 Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Model load | 3-5s | One-time, on first search |
| Embed 100 topics | 2-3s | One-time build |
| Single search | ~15ms | Subsequent queries |
| Full app startup | 5-10s | Includes model + Streamlit |

---

## 🔗 Related Files

- [vector_db.py](vector_db.py) — Core VectorDB implementation
- [search_integration.py](search_integration.py) — Search API
- [extract_tutorials_pipeline.py](extract_tutorials_pipeline.py) — PDF extraction
- [VECTOR_DB_IMPLEMENTATION.md](VECTOR_DB_IMPLEMENTATION.md) — Technical deep-dive
- [requirements.txt](requirements.txt) — Python dependencies

---

**Questions?** Check the troubleshooting section or open an issue!
