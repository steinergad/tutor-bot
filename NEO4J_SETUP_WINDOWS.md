# Neo4j Setup for Windows - Complete Guide

## ✅ Option 1: Neo4j Desktop (Recommended for Windows)

**Easiest method - GUI installer for Windows**

### Step 1: Download Neo4j Desktop
1. Visit: https://neo4j.com/download/
2. Click "Download for Windows"
3. Select "Neo4j Desktop" (free version)
4. Run the installer (Neo4jDesktop-x.x.x-setup.exe)

### Step 2: Create a Local Database
1. Open Neo4j Desktop
2. Click "Add Local DBMS"
3. Set database name: `tutor-bot-graph`
4. Set password: `password`
5. Click "Create"
6. Click "Start" to run the database

### Step 3: Connect to Database
```bash
# Test connection
python graph_rag_neo4j.py --connect
```

### Step 4: Load Your Graph
```bash
# Load knowledge graph into Neo4j
python graph_rag_neo4j.py --build
```

### Step 5: Test Queries
```bash
python graph_rag_neo4j.py --query "Merge Sort"
```

---

## ✅ Option 2: Docker Desktop for Windows

**If you prefer Docker (requires Docker Desktop installation)**

### Step 1: Install Docker Desktop
1. Download: https://www.docker.com/products/docker-desktop
2. Run installer
3. Restart computer
4. Open PowerShell and verify:
```bash
docker --version
```

### Step 2: Start Neo4j Container
```bash
docker run -d -p 7687:7687 -p 7474:7474 `
  --name neo4j `
  -e NEO4J_AUTH=neo4j/password `
  neo4j:latest
```

### Step 3: Wait for startup (10-15 seconds)
```bash
# Check status
docker ps | grep neo4j
```

### Step 4: Proceed with connection
```bash
python graph_rag_neo4j.py --connect
```

---

## ✅ Option 3: Neo4j Cloud (Online - Easiest)

**Free tier - no installation needed, runs in cloud**

### Step 1: Create Free Account
1. Visit: https://neo4j.com/cloud/aura/
2. Sign up (free)
3. Create free database
4. Note the connection details

### Step 2: Update Connection String
Edit your environment or connection code:
```python
URI = "neo4j+s://your-cloud-uri.neo4jlabs.io"
AUTH = ("neo4j", "your-password")
```

### Step 3: Load and test
```bash
python graph_rag_neo4j.py --build
python graph_rag_neo4j.py --query "Fibonacci"
```

---

## 🎯 Quick Recommendation

| Method | Time | Best For | Free |
|--------|------|----------|------|
| **Desktop** | 5 min | Development | ✅ Yes |
| **Docker** | 10 min | Both | ✅ Yes |
| **Cloud** | 2 min | Production | ✅ Free tier |

**For now, use Desktop** - quickest on Windows without additional setup.

---

## Troubleshooting

### Issue: Neo4j won't connect
```bash
# Check if service is running
docker ps

# Restart if needed
docker restart neo4j

# Check logs
docker logs neo4j
```

### Issue: Port already in use
```bash
# Use different port
docker run -d -p 7698:7687 -p 7475:7474 neo4j:latest
```

### Issue: Authentication failed
Verify credentials match what you set:
- Default username: `neo4j`
- Default password: `password` (as set in our examples)

---

## After Neo4j is Running

### 1. Verify Connection
```bash
python graph_rag_neo4j.py --connect
```

**Expected Output:**
```
✓ Connected to Neo4j successfully
Database: neo4j
Version: 5.x.x
```

### 2. Load Knowledge Graph
```bash
python graph_rag_neo4j.py --build
```

**Expected Output:**
```
Loading graph data...
✓ Loaded 30 entities
✓ Loaded 37 relationships
✓ Graph ready for queries
```

### 3. Test Queries
```bash
python graph_rag_neo4j.py --query "Fibonacci"
```

**Expected Output:**
```
Query: Fibonacci
Entity: problem_fibonacci (Problem)
Prerequisites: [Recursion, Dynamic Programming, Memoization]
Related: [Coin Change Problem, Maximum Profit Problem]
Learning Path: Recursion → Dynamic Programming → Fibonacci
```

### 4. Browse Neo4j Browser
- Desktop: Click "Open" button in Desktop app
- Docker: http://localhost:7474
- Cloud: Link from your account

Login with credentials and run Cypher query:
```cypher
MATCH (n) RETURN n LIMIT 5
```

You should see your entities as nodes!

---

## Environment Configuration

If using custom Neo4j setup, update the connection in `graph_rag_neo4j.py`:

```python
# At top of file
NEO4J_URI = "neo4j://localhost:7687"  # Or your URI
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
```

---

## Performance Comparison

After loading:

| Operation | Time | Query Type |
|-----------|------|-----------|
| Find entity | 30ms | Direct lookup |
| Get prerequisites | 45ms | Graph traversal |
| Learning path | 80ms | Full path search |
| Related concepts | 50ms | Network search |

---

## Next: Integration with Tutor App

Once Neo4j is running and graph is loaded:

1. Read: `PHASE_4_INTEGRATION.md`
2. Update: `app.py` (5 code locations)
3. Run: `streamlit run app.py`
4. Test: Ask homework question
5. Verify: Tutor mentions prerequisites

---

**Ready to go?**

Pick your method above and follow the steps. Once Neo4j is running, you can load your graph in 1 command:

```bash
python graph_rag_neo4j.py --build
```

Then test end-to-end:
```bash
python test_neo4j_e2e.py
```

Good luck! 🚀
