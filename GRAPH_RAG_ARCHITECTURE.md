# 🌐 Graph RAG Architecture for Intelligent Tutoring Backend

**Version 1.0** — Optimal backend structure for tutor-bot with dynamic knowledge retrieval

---

## 📋 Problem Statement

**Current Approach (Vector DB only):**
- ❌ Requires knowing exact number of topics upfront
- ❌ No understanding of prerequisites or topic relationships
- ❌ Cannot answer "what should I learn next?" intelligently
- ❌ Treats all topics as isolated points in vector space
- ❌ Hard to scale to new curricula

**Graph RAG Solution:**
- ✅ Dynamically infers relevant material from relationships
- ✅ Understands prerequisites and learning paths
- ✅ Answers "what comes next?" by traversing graph
- ✅ Single query can traverse multiple topics intelligently
- ✅ Easily extensible to new subjects

---

## 🏗️ Architecture Overview

### Three-Layer Stack

```
┌─────────────────────────────────────────────────────┐
│           INFERENCE LAYER (Online)                  │
│  Query Router → Graph Traversal → Context Aggregator│
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│       KNOWLEDGE LAYER (Offline + Online)            │
│  Entity Graph (Neo4j/SQLite) + Vector DB (Chroma)   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           DATA LAYER (Offline Only)                 │
│  PDFs → Text Extraction → Entity Detection → Build  │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Three-Stage Pipeline

### STAGE 1: OFFLINE (Build Once, Use Many Times)

#### 1.1 Entity Extraction
Extract all meaningful concepts from tutorials:

```python
# Example entities for "Sorting Algorithms" tutorial:
Entities = {
    "concepts": ["bubble sort", "merge sort", "quicksort", "time complexity", "space complexity"],
    "prerequisites": ["arrays", "recursion", "comparisons"],
    "related": ["divide and conquer", "dynamic programming"],
    "examples": ["sorting [1,3,2,4]", "in-place sorting"]
}
```

**Tools:**
- LLM extraction: "Extract all algorithm names and concepts from this text"
- Pattern matching: Regex for known algorithms, data structures
- Dependency parsing: NLP to find "requires", "assumes", "uses" relationships

#### 1.2 Relationship Building

Create directed edges between entities:

```
CONCEPT RELATIONSHIPS:
  "Bubble Sort" --requires--> "Comparison Operations"
  "Merge Sort" --requires--> "Recursion"
  "Merge Sort" --requires--> "Divide and Conquer"
  "Quicksort" --similar-to--> "Merge Sort"
  "Sorting" --prerequisite-for--> "Binary Search"
  "Big O Notation" --explains--> "Sorting"
  
LEARNING PATH:
  Arrays → Recursion → Divide and Conquer → Merge Sort → Quicksort
```

**Edge Types (Graph Schema):**
- `requires`: "X requires understanding Y first"
- `prerequisite_for`: "Learning X helps with Y"
- `similar_to`: "X and Y solve same problem differently"
- `specialization_of`: "Quicksort is a specialized sorting algorithm"
- `explained_by`: "Concept X is explained in tutorial Y"
- `example_in`: "Algorithm X has code example in tutorial Y"
- `part_of`: "Mergesort is part of Sorting algorithms topic"

#### 1.3 Graph Construction

**Option A: Neo4j (Production Ready)**
```python
# Persistent graph database
from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://localhost:7687")
session = driver.session()

# Create entities
session.run("""
MERGE (a:Algorithm {name: 'Merge Sort', complexity: 'O(n log n)'})
MERGE (b:Concept {name: 'Recursion'})
MERGE (a)-[:REQUIRES]->(b)
""")
```

**Option B: Lightweight SQLite + NetworkX (MVP)**
```python
import sqlite3
import networkx as nx
import json

# Lightweight storage
conn = sqlite3.connect('db/knowledge_graph.db')
entities = json.load(open('db/entities.json'))  # {id, name, type, tutorial_id}
relationships = json.load(open('db/relationships.json'))  # {from_id, to_id, relation_type}

# In-memory graph for inference
G = nx.DiGraph()
for entity in entities:
    G.add_node(entity['id'], **entity)
for rel in relationships:
    G.add_edge(rel['from_id'], rel['to_id'], relation=rel['type'])
```

#### 1.4 Vector Embeddings

Enhance graph with semantic similarity:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed entity descriptions
for entity in entities:
    text = f"{entity['name']}: {entity['description']}"
    entity['embedding'] = model.encode(text)  # Store in Neo4j or SQLite
```

**Store in Neo4j:**
```cypher
MATCH (e:Entity)
SET e.embedding = $embedding  # Vector index support
```

---

### STAGE 2: ONLINE (Inference)

#### 2.1 Query Router

When student asks a question:

```python
class QueryRouter:
    def route(self, question: str, homework_id: str):
        # Classify question type
        q_type = self.classify(question)  # "specific", "general", "prerequisite"
        
        if q_type == "specific":
            # "How do I implement bubble sort?"
            return self.specific_query_handler(question)
        elif q_type == "general":
            # "What is sorting?"
            return self.general_query_handler(question)
        elif q_type == "prerequisite":
            # "Do I need to know recursion?"
            return self.prerequisite_checker(question, homework_id)
```

#### 2.2 Graph Traversal

Find relevant materials by walking the graph:

```python
def find_relevant_materials(concept: str, depth: int = 2, homework_id: str = None):
    """
    Traverse graph to find:
    1. Related concepts
    2. Prerequisites (what to learn first)
    3. Examples and use cases
    4. Advanced topics
    """
    
    # Start node
    start_node = find_entity_by_name(concept)
    
    # Traverse graph
    relevant = {
        "exact": [start_node],
        "prerequisites": nx.ancestors(G, start_node, depth=depth),
        "related": nx.descendants(G, start_node, depth=depth),
        "explanations": find_nodes_by_relation(start_node, "explained_by"),
        "examples": find_nodes_by_relation(start_node, "example_in"),
    }
    
    # Filter by homework scope
    if homework_id:
        relevant = filter_by_homework(relevant, homework_id)
    
    return relevant
```

**Graph Traversal Patterns:**

```
Pattern 1: PREREQUISITES (answer "what do I need first?")
  Question: "How do I learn Quicksort?"
  Traverse: Quicksort <- requires <- Recursion <- requires <- Arrays
  Result: "First learn arrays, then recursion, then you're ready for Quicksort"

Pattern 2: RELATED CONCEPTS (answer "is this similar to something?")
  Question: "What's the difference between Mergesort and Quicksort?"
  Traverse: Mergesort <-similar_to-> Quicksort, both <- sorting_algorithm
  Related edges: time_complexity, space_complexity, best_case, worst_case
  Result: "Both are divide-and-conquer sorts, but differ in space/time tradeoffs"

Pattern 3: LEARNING PATH (answer "what comes next?")
  Question: "I've learned Big O notation and arrays"
  Traverse: Look for nodes where {BigO, Arrays} are prerequisites
  Result: "Next logical step: learn sorting algorithms (bubble sort is simplest)"

Pattern 4: APPLICATIONS (answer "why do I need this?")
  Question: "Why do I need to know binary search?"
  Traverse: Binary_Search <- used_in <- problem_1, problem_2
  Result: "Used in sorted array lookups, database indexing, game AI..."
```

#### 2.3 Hybrid Search (Vector + Graph)

Combine semantic and structural information:

```python
def hybrid_search(question: str, homework_id: str, k: int = 5):
    """
    1. Vector search: Find semantically similar concepts
    2. Graph enhancement: Expand with related concepts
    3. Rank: Score by relevance + distance in graph
    """
    
    # Step 1: Semantic search
    question_embedding = model.encode(question)
    vector_results = chroma_db.query(
        query_embedding=question_embedding,
        n_results=10  # Get more to filter
    )
    
    # Step 2: Expand with graph relationships
    expanded = set()
    for result in vector_results:
        concept = result['name']
        entity = find_entity(concept, homework_id)
        
        # Add related concepts
        expanded.add(entity)
        expanded.update(find_related(entity, depth=1))
        expanded.update(find_prerequisites(entity, depth=1))
    
    # Step 3: Rank and filter
    ranked = rank_by_relevance(
        expanded,
        question_embedding,
        homework_scope=homework_id
    )
    
    return ranked[:k]
```

#### 2.4 Context Aggregation

Build tutor context from graph results:

```python
def build_tutor_context(question: str, relevant_materials: list, homework_id: str):
    """
    Prepare context for LLM tutor.
    
    Returns:
      - Direct answer material
      - Prerequisites the student might be missing
      - Related concepts for deeper understanding
      - Examples to work through
    """
    
    context = {
        "direct": relevant_materials[:3],
        "prerequisites": [
            material for material in relevant_materials
            if material['relation'] == 'prerequisite'
        ],
        "related": [
            material for material in relevant_materials
            if material['relation'] == 'similar_to'
        ],
        "examples": [
            material for material in relevant_materials
            if material['type'] == 'code_example'
        ],
        "tutorial_references": [
            f"See Tutorial {m['tutorial_id']}: {m['section_name']}"
            for m in relevant_materials
        ]
    }
    
    # Build prompt instruction
    tutor_prompt = f"""
    Student Question: {question}
    
    RELEVANT MATERIAL GRAPH:
    {format_graph_path(relevant_materials)}
    
    PREREQUISITES MISSING:
    {format_prerequisites(context['prerequisites'])}
    
    EXAMPLES TO REFERENCE:
    {format_examples(context['examples'])}
    
    Teach using Socratic method, referencing these materials.
    """
    
    return tutor_prompt
```

---

### STAGE 3: RESPONSE GENERATION

#### 3.1 Curriculum-Grounded Tutor

```python
def generate_homework_response(question: str, homework_id: str):
    # Get relevant materials from hybrid search
    materials = hybrid_search(question, homework_id)
    
    # Build tutor context
    context = build_tutor_context(question, materials, homework_id)
    
    # Generate response with LLM
    response = llm.generate(
        system_prompt=HOMEWORK_SOCRATIC_PROMPT,
        context=context,
        question=question
    )
    
    # Add tutorial references
    response += format_references(materials)
    
    return response
```

**Example Output:**
```
Q: "How do I implement bubble sort?"

A: "Let's connect this to what you've learned. In Tutorial 1, we analyzed 
how sorting works with comparisons. Bubble sort is the simplest: you 
repeatedly swap adjacent elements if they're in wrong order.

Before diving in, let me ask: Do you remember how to compare two elements 
in an array? Can you walk me through a simple example with [3, 1, 2]?

Once you get the comparison logic, bubble sort is just repeating that swap 
until the array is sorted.

→ Reference: Tutorial 1, Section 2.3 (Comparison-based sorting)
→ Prerequisite: Arrays (Tutorial 0, Section 1.2)
→ Related: Other sorting algorithms (Merge sort uses similar ideas)"
```

---

## 📊 Data Model (Schema)

### Entities Table
```json
{
  "id": "algo_bubble_sort",
  "name": "Bubble Sort",
  "type": "algorithm",
  "description": "Sorting algorithm that repeatedly steps through list...",
  "embedding": [0.12, -0.45, ...],
  "tutorial_id": "tutorial_1",
  "section": "sorting_basics",
  "complexity": "O(n²)",
  "best_case": "O(n)",
  "space_complexity": "O(1)",
  "keywords": ["sorting", "comparison", "simple"],
  "difficulty": "beginner",
  "prerequisites": ["array_indexing", "comparisons"],
  "taught_in_week": 1,
  "homework_weeks": [1, 2]
}
```

### Relationships Table
```json
[
  {
    "from_id": "algo_bubble_sort",
    "to_id": "concept_recursion",
    "relation": "not_required",
    "confidence": 1.0,
    "explanation": "Bubble sort doesn't use recursion"
  },
  {
    "from_id": "algo_bubble_sort",
    "to_id": "algo_merge_sort",
    "relation": "similar_to",
    "confidence": 0.7,
    "difference": "Different divide strategy, similar complexity class"
  }
]
```

---

## 🔧 Implementation Comparison

### Option 1: Neo4j (Production)

**Pros:**
- ✅ Built for graph queries
- ✅ Scales to millions of entities
- ✅ Vector search support (Neo4j 5.x)
- ✅ Professional backup/recovery
- ✅ Multi-user support

**Cons:**
- ❌ Requires external database
- ❌ More setup complexity
- ❌ Paid tiers for production

**For Your Project:** Use if deployed to multiple servers

```python
# Installation: docker run -p 7687:7687 neo4j
# Or: conda install neo4j

from neo4j import GraphDatabase

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def add_entity(self, entity_id, name, entity_type, **properties):
        with self.driver.session() as session:
            session.run("""
                MERGE (e:Entity {id: $id})
                SET e += $props
            """, id=entity_id, props={**properties, 'name': name, 'type': entity_type})
    
    def find_prerequisites(self, entity_id, depth=2):
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (start)-[:REQUIRES*1..${depth}]-(prereq)
                WHERE start.id = $id
                RETURN prereq, length(path) as distance
                ORDER BY distance
            """, id=entity_id, depth=depth)
            return list(result)
```

### Option 2: SQLite + NetworkX (MVP)

**Pros:**
- ✅ Zero external dependencies
- ✅ Single file database
- ✅ Fast for small graphs (<10K nodes)
- ✅ Perfect for local development
- ✅ Easy to backup/version

**Cons:**
- ❌ Not ideal for >100K entities
- ❌ In-memory graph for traversal (slower)
- ❌ No built-in vector support

**For Your Project:** Start here, migrate to Neo4j later

```python
# Installation: pip install networkx

import sqlite3
import networkx as nx
import json

class LightweightKnowledgeGraph:
    def __init__(self, db_path="db/knowledge.db"):
        self.conn = sqlite3.connect(db_path)
        self.G = nx.DiGraph()
        self._init_db()
        self._load_graph()
    
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                data JSON
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY,
                from_id TEXT,
                to_id TEXT,
                relation TEXT,
                FOREIGN KEY(from_id) REFERENCES entities(id),
                FOREIGN KEY(to_id) REFERENCES entities(id)
            )
        """)
    
    def find_prerequisites(self, entity_id, depth=2):
        return nx.ancestors(self.G, entity_id)
    
    def find_related(self, entity_id, depth=1):
        return nx.descendants(self.G, entity_id)
```

---

## 📈 Build Process (Offline)

### Step 1: Extract Entities

```python
# Step 1: Extract from PDFs
from extract_tutorials_pipeline import extract_tutorial_text

tutorials = extract_tutorial_text("material/")

# Step 2: LLM-powered entity extraction
from langchain import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini")

entity_prompt = ChatPromptTemplate.from_template("""
Extract all algorithm names, concepts, and data structures from this tutorial text.
Format as JSON:
{{
  "algorithms": ["name1", "name2"],
  "concepts": ["concept1", "concept2"],
  "prerequisites": ["prereq1"],
  "examples": ["example1"]
}}

Text:
{text}
""")

for tutorial_id, text in tutorials.items():
    result = llm.invoke(entity_prompt.format(text=text))
    entities = json.loads(result.content)
    store_entities(tutorial_id, entities)
```

### Step 2: Extract Relationships

```python
# Method 1: LLM-based relationship extraction
relationship_prompt = ChatPromptTemplate.from_template("""
Given these concepts from an algorithm tutorial, identify relationships.
Return JSON:
{{
  "relationships": [
    {{"from": "Bubble Sort", "to": "Comparison", "type": "requires"}},
    {{"from": "Merge Sort", "to": "Recursion", "type": "requires"}}
  ]
}}

Concepts: {concepts}
Text: {text}
""")

# Method 2: Pattern-based relationships
PREREQUISITE_PATTERNS = {
    r"requires? knowledge of (.+?)(?:\.|,|;)": "requires",
    r"before learning (.+?) you should know (.+?)": "prerequisite_for",
    r"(.+?) is similar to (.+?)": "similar_to",
}

def extract_relationships_pattern(text):
    relationships = []
    for pattern, rel_type in PREREQUISITE_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            relationships.append({
                "from": match[0],
                "to": match[1] if isinstance(match, tuple) else match,
                "type": rel_type
            })
    return relationships
```

### Step 3: Build Graph

```python
# Neo4j version
from neo4j import GraphDatabase

class GraphBuilder:
    def __init__(self, driver):
        self.driver = driver
    
    def build(self, entities_file, relationships_file):
        with self.driver.session() as session:
            # Load entities
            with open(entities_file) as f:
                for entity in json.load(f):
                    session.run("""
                        MERGE (e:Entity {id: $id})
                        SET e += $props
                    """, id=entity['id'], props=entity)
            
            # Load relationships
            with open(relationships_file) as f:
                for rel in json.load(f):
                    session.run(f"""
                        MATCH (a {{id: $from}})
                        MATCH (b {{id: $to}})
                        MERGE (a)-[:{rel['type'].upper()}]->(b)
                    """, from=rel['from'], to=rel['to'])

# Run build
builder = GraphBuilder(driver)
builder.build('entities.json', 'relationships.json')
```

---

## 🚀 Integration with Current App

### Update app.py Workflow

**Before (Vector DB only):**
```
Question → Vector Search → Top 5 results → LLM response
```

**After (Graph RAG):**
```
Question 
  ↓
Classify type (specific/general/prerequisite)
  ↓
Hybrid Search (vector + graph traversal)
  ↓
Build context graph
  ↓
Format for tutor (with references)
  ↓
LLM response (curriculum-grounded)
```

### New Module: `graph_retriever.py`

```python
class GraphRetriever:
    def __init__(self, knowledge_graph, vector_db, homework_data):
        self.kg = knowledge_graph
        self.vdb = vector_db
        self.hw = homework_data
    
    def retrieve(self, question: str, homework_id: str, context_depth: int = 2):
        """
        Hybrid search: graph + vector
        Returns: (direct_materials, prerequisites, related, examples)
        """
        
        # 1. Vector search for semantic match
        semantic_results = self.vdb.search(question, k=10)
        
        # 2. For each semantic result, traverse graph
        expanded = self._expand_with_graph(semantic_results, context_depth)
        
        # 3. Filter by homework scope
        filtered = self._filter_by_scope(expanded, homework_id)
        
        # 4. Organize by relationship type
        organized = self._organize_by_type(filtered)
        
        return organized

    def _expand_with_graph(self, semantic_results, depth):
        expanded = set()
        for result in semantic_results:
            concept = result['name']
            entity = self.kg.find_entity(concept)
            if entity:
                expanded.add(entity)
                # Add prerequisites
                expanded.update(self.kg.find_prerequisites(entity, depth))
                # Add related
                expanded.update(self.kg.find_related(entity, depth))
        return expanded
    
    # ... more methods ...
```

### Integration Point

```python
# In app.py homework mode

from graph_retriever import GraphRetriever

# Initialize once at startup
graph_retriever = GraphRetriever(
    knowledge_graph=knowledge_graph,
    vector_db=vector_db,
    homework_data=homework_data
)

# In homework response handler
def handle_homework_question(question: str, homework_id: str):
    # Get relevant materials
    materials = graph_retriever.retrieve(question, homework_id)
    
    # Build tutor context
    context = build_tutor_context(materials, question)
    
    # Generate response
    response = llm.generate(
        system_prompt=HOMEWORK_SOCRATIC_PROMPT,
        context=context,
        question=question
    )
    
    return response
```

---

## 📊 Implementation Roadmap

### Phase 1: MVP (2-3 weeks)
- [ ] Extract entities from tutorials (manual + LLM-assisted)
- [ ] Build relationship manually (spreadsheet → JSON)
- [ ] Implement lightweight SQLite + NetworkX version
- [ ] Basic hybrid search (vector + graph)
- [ ] Test with homework questions

### Phase 2: Production (1-2 weeks)
- [ ] Migrate to Neo4j
- [ ] Automate entity/relationship extraction (LLM pipeline)
- [ ] Add vector search to Neo4j
- [ ] Performance optimization (caching, indexing)
- [ ] Multi-language support

### Phase 3: Advanced (ongoing)
- [ ] Community detection (find topic clusters)
- [ ] Prerequisite validation (ensure learning order)
- [ ] Learning path recommendation ("what to study next")
- [ ] Weak link detection (common misconceptions)
- [ ] Adaptive difficulty (adjust based on progress)

---

## 📚 External Resources

- **Graph RAG Paper**: https://arxiv.org/abs/2404.16130
- **Microsoft GraphRAG**: https://github.com/microsoft/graphrag
- **Neo4j Python Driver**: https://neo4j.com/docs/python-manual/current/
- **LangGraph**: https://docs.langchain.com/oss/python/langgraph/
- **NetworkX Docs**: https://networkx.org/documentation/stable/

---

## ⚡ Quick Start Code Template

```python
# Step 1: Build graph (offline)
from graph_rag.builder import build_knowledge_graph
build_knowledge_graph(
    tutorials_path="material/",
    output_db="db/knowledge_graph.db",
    llm_provider="openai"  # For entity extraction
)

# Step 2: Initialize retriever (online)
from graph_rag.retriever import GraphRetriever
retriever = GraphRetriever("db/knowledge_graph.db")

# Step 3: Use in homework mode
materials = retriever.retrieve(
    question="How do I implement quicksort?",
    homework_id="hw_1",
    depth=2
)
print(materials)
# Output:
# {
#   "direct": [Quicksort entity],
#   "prerequisites": [Recursion, Divide-and-Conquer],
#   "related": [Mergesort, Heapsort],
#   "examples": [code example, trace example]
# }
```

---

## 🎯 Success Metrics

- ✅ Dynamic topic retrieval (not predefined count)
- ✅ Prerequisites correctly identified
- ✅ Learning path recommendations working
- ✅ Context relevance score > 0.8
- ✅ Query response time < 500ms (including LLM)
- ✅ Scales to 500+ concepts without slowdown

