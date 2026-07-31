# Integration Guide: Adding Graph RAG to Your Tutor Bot

## Quick Start (15 minutes)

### 1. Test the demo
```bash
python graph_rag_starter.py --demo
```

Expected output:
```
QUERY: How do I learn Quicksort?

📚 Learning Prerequisites:
  • Recursion
  • Divide and Conquer

🎯 Main Concept:
  • Quicksort: Average O(n log n) sorting

🔗 Related Concepts:
  • Merge Sort
  • Bubble Sort

📖 Suggested Learning Path:
  1. Arrays
  2. Recursion
  3. Divide and Conquer
  4. Quicksort
  5. Merge Sort
```

---

## Phase 1: Extract Entities (Week 1)

### Option A: Manual (Most Accurate)
1. Read through tutorials
2. Create `db/entities.json`:
```json
[
  {
    "id": "algo_bubble_sort",
    "name": "Bubble Sort",
    "entity_type": "algorithm",
    "description": "Sorting by repeated swaps of adjacent elements",
    "tutorial_id": "tutorial_1",
    "section": "sorting_basics",
    "difficulty": "beginner"
  }
]
```

### Option B: LLM-Assisted (Faster)
```python
from langchain import ChatOpenAI, ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini")

extraction_prompt = ChatPromptTemplate.from_template("""
Extract all algorithms, data structures, and concepts from this text.
Return JSON array:
[
  {{"id": "algo_xyz", "name": "Algorithm Name", "entity_type": "algorithm", 
    "description": "...", "difficulty": "beginner"}}
]

Text:
{text}
""")

# For each tutorial
for tutorial_file in glob("material/*.txt"):
    text = open(tutorial_file).read()
    result = llm.invoke(extraction_prompt.format(text=text))
    entities = json.loads(result.content)
    # Save to db/entities.json
```

---

## Phase 2: Extract Relationships (Week 2)

### Method 1: Pattern-Based (Fast)
```python
import re

PATTERNS = {
    r"requires? knowledge of (.+?)(?:\.|,|before)": ("requires", 0),
    r"first.*(.+?), then.*(.+?)": ("prerequisite_for", 1),
    r"similar to (.+?)": ("similar_to", 0),
}

def extract_relationships(text):
    relationships = []
    for pattern, (rel_type, group_idx) in PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            target = match[group_idx] if isinstance(match, tuple) else match
            relationships.append({
                "from_id": find_entity_id(current_topic),
                "to_id": find_entity_id(target),
                "type": rel_type
            })
    return relationships
```

### Method 2: LLM-Assisted (Most Accurate)
```python
relationship_prompt = ChatPromptTemplate.from_template("""
Given these algorithm concepts, identify learning relationships.
Return JSON:
[
  {{"from_id": "algo_x", "to_id": "algo_y", "type": "requires", "explanation": "..."}}
]

Concepts:
{concepts}

Text:
{text}
""")
```

---

## Phase 3: Build and Test (Week 2)

### Build the graph:
```python
from graph_rag_starter import LightweightKnowledgeGraph

kg = LightweightKnowledgeGraph("db/knowledge_graph.db")
kg.load_from_json("db/entities.json", "db/relationships.json")

# Check stats
print(kg.stats())
# Output: {'nodes': 150, 'edges': 320, 'density': 0.08, 'is_connected': False}
```

### Test queries:
```python
from graph_rag_starter import HybridRetriever

retriever = HybridRetriever(kg)

# Test 1: Specific algorithm
result = retriever.retrieve("quicksort")
print(result['prerequisites'])  # Should show Recursion, Divide & Conquer

# Test 2: General concept
result = retriever.retrieve("sorting")
print(result['learning_path'])  # Should show: Arrays → Bubble Sort → Merge Sort → Quicksort

# Test 3: Unknown topic
result = retriever.retrieve("machine learning")
print(result)  # Should return empty (out of scope)
```

---

## Phase 4: Integration with App (Week 3)

### Update `app.py`:

```python
# Add to imports
from graph_rag_starter import LightweightKnowledgeGraph, HybridRetriever

# Add to initialization (outside Streamlit functions)
@st.cache_resource
def load_knowledge_graph():
    """Load knowledge graph once"""
    kg = LightweightKnowledgeGraph("db/knowledge_graph.db")
    return kg, HybridRetriever(kg)

knowledge_graph, graph_retriever = load_knowledge_graph()

# Update homework response handler
def handle_homework_question(question: str, homework_id: str, selected_hw: dict):
    # 1. Get relevant materials from graph
    materials = graph_retriever.retrieve(question)
    
    # 2. Filter by homework scope
    hw_topics = selected_hw.get('topics', [])
    filtered_materials = filter_materials_by_scope(materials, hw_topics)
    
    # 3. Build context for tutor
    context = build_tutor_context_from_graph(
        filtered_materials,
        question,
        knowledge_graph
    )
    
    # 4. Generate response
    response = get_llm_response(
        system_prompt=HOMEWORK_SOCRATIC_PROMPT,
        context=context,
        question=question
    )
    
    return response

# Helper: Build tutor context from graph results
def build_tutor_context_from_graph(materials, question, kg):
    context = {
        "question": question,
        "direct_materials": materials.get('direct', []),
        "prerequisites": [
            kg.get_entity_info(e) for e in materials.get('prerequisites', [])
        ],
        "related": [
            kg.get_entity_info(e) for e in materials.get('related', [])
        ],
        "learning_path": [
            kg.get_entity_info(e) for e in materials.get('learning_path', [])
        ]
    }
    
    # Format for system prompt
    context_str = f"""
STUDENT QUESTION: {question}

RELEVANT LEARNING PATH:
{format_learning_path(context['learning_path'])}

PREREQUISITES (learn these first):
{format_materials(context['prerequisites'])}

CURRENT TOPIC:
{format_materials(context['direct_materials'])}

NEXT CONCEPTS:
{format_materials(context['related'])}
"""
    
    return context_str
```

### Update `prompts/homework_prompt.json`:

```json
{
  "system_message_template": {
    "with_graph_rag": true,
    "graph_context": {
      "principle": "Use the learning path graph to provide context-aware Socratic guidance",
      "dos": [
        "Reference the prerequisite concepts they should know",
        "Explain how current concept builds on prerequisites",
        "Suggest next concepts in learning path",
        "Ask about understanding of related similar concepts"
      ]
    }
  }
}
```

---

## Phase 5: Scale to Neo4j (Optional, Week 4)

Once satisfied with MVP, migrate to Neo4j:

```python
# graph_rag_neo4j.py
from neo4j import GraphDatabase

class KnowledgeGraphNeo4j:
    def __init__(self, uri="neo4j://localhost:7687", auth=("neo4j", "password")):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def add_entity(self, entity_id, name, entity_type, **props):
        with self.driver.session() as session:
            session.run("""
                MERGE (e:Entity {id: $id})
                SET e.name = $name, e.type = $type
                SET e += $props
            """, id=entity_id, name=name, type=entity_type, props=props)
    
    def add_relationship(self, from_id, to_id, rel_type, confidence=1.0):
        with self.driver.session() as session:
            session.run(f"""
                MATCH (a {{id: $from}})
                MATCH (b {{id: $to}})
                MERGE (a)-[:{rel_type}]->(b)
                SET r.confidence = $conf
            """, from=from_id, to=to_id, conf=confidence)
    
    def find_prerequisites(self, entity_id, depth=2):
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (start)-[:REQUIRES*1..$depth]-(prereq)
                WHERE start.id = $id
                RETURN DISTINCT prereq.id as id, prereq.name as name
                ORDER BY length(path)
            """, id=entity_id, depth=depth)
            return [dict(record) for record in result]
```

Then just swap:
```python
# In app.py
# kg = LightweightKnowledgeGraph(...)  # OLD
kg = KnowledgeGraphNeo4j()  # NEW
```

---

## Testing Checklist

- [ ] Entity extraction: 150+ concepts extracted
- [ ] Relationship extraction: 300+ relationships mapped
- [ ] Graph building: Zero errors, valid graph
- [ ] Specific queries: "How do I learn quicksort?" → correct prerequisites
- [ ] General queries: "What's sorting?" → returns all sorting algorithms
- [ ] Scope filtering: Homework-relevant materials only
- [ ] Performance: Query response < 100ms
- [ ] Integration: App loads graph on startup
- [ ] Homework mode: Uses graph for context
- [ ] Learning path: Suggests logical progression

---

## File Structure After Implementation

```
tutor-bot/
├── graph_rag_starter.py           # Core implementation
├── GRAPH_RAG_ARCHITECTURE.md      # Design doc (this file)
├── app.py                         # Updated with graph integration
├── db/
│   ├── knowledge_graph.db         # SQLite graph database
│   ├── entities.json              # Entity definitions
│   ├── relationships.json         # Relationship definitions
│   ├── chroma_vector_store/       # Keep existing vector DB
│   └── ...
├── prompts/
│   ├── homework_prompt.json       # Updated with graph context
│   └── prompt_builder.py          # Keep existing
└── ...
```

---

## Debugging

### Query not returning results?
```python
# Check if entity exists
kg.find_entity_by_name("Quicksort")

# Check if relationships are loaded
list(kg.G.successors("algo_quicksort"))

# Visualize graph (requires graphviz)
import matplotlib.pyplot as plt
import networkx as nx
nx.draw_networkx(kg.G, with_labels=True)
plt.show()
```

### Performance issues?
```python
# Profile a query
import time
start = time.time()
result = retriever.retrieve("quicksort")
print(f"Query took {time.time() - start:.3f}s")

# If > 100ms, add indices to SQLite:
kg.conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON entities(type)")
kg.conn.execute("ANALYZE")
```

### Wrong results?
```python
# Check entity properties
info = kg.get_entity_info("algo_quicksort")
print(json.dumps(info, indent=2))

# Verify relationships
for succ in kg.G.successors("algo_quicksort"):
    edge_data = kg.G.edges["algo_quicksort", succ]
    print(f"{algo_quicksort} -> {succ}: {edge_data}")
```

---

## Next Steps

1. **Week 1-2**: Extract entities & relationships manually (most accurate)
2. **Week 2**: Build and test knowledge graph locally
3. **Week 3**: Integrate with app
4. **Week 4**: Add community detection (find topic clusters)
5. **Future**: Learning path recommendations, adaptive difficulty

---

## Questions?

See these resources:
- `GRAPH_RAG_ARCHITECTURE.md` — Detailed architecture
- `graph_rag_starter.py` — Runnable code with comments
- Microsoft GraphRAG: https://github.com/microsoft/graphrag
- NetworkX docs: https://networkx.org/
