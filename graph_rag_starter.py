"""
graph_rag_starter.py — Minimal implementation to get started with Graph RAG

This is a lightweight MVP version using SQLite + NetworkX.
It shows all the core concepts without external database dependencies.

Usage:
    python graph_rag_starter.py --build  # Build graph from data
    python graph_rag_starter.py --query "How do I learn sorting?"
"""

import json
import sqlite3
import networkx as nx
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from enum import Enum


# ═════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═════════════════════════════════════════════════════════════════════════════

class RelationType(Enum):
    """Relationship types in knowledge graph"""
    REQUIRES = "requires"              # "A requires B first"
    TEACHES = "teaches"                # "Tutorial X teaches concept Y"
    SIMILAR_TO = "similar_to"          # "Quicksort and Mergesort are similar"
    SPECIALIZATION = "specialization"  # "Quicksort is a specialized sort"
    EXAMPLE_IN = "example_in"          # "Code example in tutorial X"
    PREREQUISITE_FOR = "prerequisite_for"  # "A is needed for B"


@dataclass
class Entity:
    """Knowledge graph entity (concept, algorithm, etc)"""
    id: str
    name: str
    entity_type: str  # "algorithm", "concept", "data_structure"
    description: str = ""
    tutorial_id: str = ""
    section: str = ""
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    week: int = 0
    homework_weeks: List[int] = None
    
    def __post_init__(self):
        if self.homework_weeks is None:
            self.homework_weeks = []
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.entity_type,
            'description': self.description,
            'tutorial_id': self.tutorial_id,
            'section': self.section,
            'difficulty': self.difficulty,
            'week': self.week,
            'homework_weeks': self.homework_weeks
        }


@dataclass
class Relationship:
    """Connection between entities"""
    from_id: str
    to_id: str
    relation_type: RelationType
    confidence: float = 1.0
    explanation: str = ""


# ═════════════════════════════════════════════════════════════════════════════
# LIGHTWEIGHT KNOWLEDGE GRAPH
# ═════════════════════════════════════════════════════════════════════════════

class LightweightKnowledgeGraph:
    """
    SQLite-backed knowledge graph with NetworkX for graph algorithms.
    
    Pros: No dependencies, single file, easy to backup
    Cons: Graph loaded in memory (OK for <10K nodes)
    """
    
    def __init__(self, db_path: str = "db/knowledge_graph.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.G = nx.DiGraph()  # In-memory graph for traversal
        
        self._init_db()
        self._load_graph()
    
    def _init_db(self):
        """Create database schema"""
        cursor = self.conn.cursor()
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                description TEXT,
                tutorial_id TEXT,
                section TEXT,
                difficulty TEXT DEFAULT 'intermediate',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_id TEXT NOT NULL,
                to_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                explanation TEXT,
                FOREIGN KEY(from_id) REFERENCES entities(id),
                FOREIGN KEY(to_id) REFERENCES entities(id),
                UNIQUE(from_id, to_id, relation_type)
            )
        """)
        
        # Create indices for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_from_id ON relationships(from_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_to_id ON relationships(to_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tutorial ON entities(tutorial_id)")
        
        self.conn.commit()
    
    def _load_graph(self):
        """Load graph from database into memory"""
        cursor = self.conn.cursor()
        
        # Load entities
        cursor.execute("SELECT * FROM entities")
        for row in cursor.fetchall():
            entity_id, name, type_, desc, tut_id, section, difficulty, _ = row
            self.G.add_node(entity_id, 
                          name=name, 
                          type=type_, 
                          description=desc,
                          tutorial_id=tut_id,
                          section=section,
                          difficulty=difficulty)
        
        # Load relationships
        cursor.execute("SELECT from_id, to_id, relation_type FROM relationships")
        for from_id, to_id, rel_type in cursor.fetchall():
            self.G.add_edge(from_id, to_id, relation=rel_type)
    
    # ─────────────────────────────────────────────────────────────────────
    # WRITE OPERATIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def add_entity(self, entity: Entity) -> bool:
        """Add entity to graph. Returns True if new, False if exists."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO entities 
                (id, name, type, description, tutorial_id, section, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (entity.id, entity.name, entity.entity_type, entity.description,
                  entity.tutorial_id, entity.section, entity.difficulty))
            self.conn.commit()
            
            # Add to in-memory graph
            self.G.add_node(entity.id, **entity.to_dict())
            return True
        except sqlite3.IntegrityError:
            return False  # Already exists
    
    def add_relationship(self, rel: Relationship) -> bool:
        """Add relationship between entities. Returns True if new."""
        cursor = self.conn.cursor()
        try:
            # Handle both string and enum relation_types
            rel_type = rel.relation_type.value if hasattr(rel.relation_type, 'value') else str(rel.relation_type)
            
            cursor.execute("""
                INSERT INTO relationships 
                (from_id, to_id, relation_type, confidence, explanation)
                VALUES (?, ?, ?, ?, ?)
            """, (rel.from_id, rel.to_id, rel_type,
                  rel.confidence, rel.explanation))
            self.conn.commit()
            
            # Add to in-memory graph
            self.G.add_edge(rel.from_id, rel.to_id, relation=rel_type)
            return True
        except sqlite3.IntegrityError:
            return False  # Already exists
    
    # ─────────────────────────────────────────────────────────────────────
    # READ OPERATIONS (Graph Traversal)
    # ─────────────────────────────────────────────────────────────────────
    
    def find_entity_by_name(self, name: str) -> Entity | None:
        """Find entity by name (case-insensitive)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, type, description, tutorial_id, section, difficulty "
            "FROM entities WHERE LOWER(name) = LOWER(?)",
            (name,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        entity_id, name, type_, desc, tut_id, section, difficulty = row
        return Entity(entity_id, name, type_, desc, tut_id, section, difficulty)
    
    def find_prerequisites(self, entity_id: str, depth: int = 2) -> Set[str]:
        """
        Find prerequisites (ancestors in graph).
        What needs to be learned BEFORE this?
        """
        if entity_id not in self.G:
            return set()
        
        # Follow REQUIRES edges backwards
        prerequisites = set()
        visited = set()
        
        def traverse(node, current_depth):
            if current_depth > depth or node in visited:
                return
            visited.add(node)
            
            # Find all nodes that point to this one with REQUIRES edge
            for pred in self.G.predecessors(node):
                edge_data = self.G.edges[pred, node]
                if edge_data.get('relation') == RelationType.REQUIRES.value:
                    prerequisites.add(pred)
                    traverse(pred, current_depth + 1)
        
        traverse(entity_id, 0)
        return prerequisites
    
    def find_related(self, entity_id: str, depth: int = 1) -> Set[str]:
        """
        Find related concepts (successors in graph).
        What can I learn AFTER this?
        """
        if entity_id not in self.G:
            return set()
        
        related = set()
        visited = set()
        
        def traverse(node, current_depth):
            if current_depth > depth or node in visited:
                return
            visited.add(node)
            
            # Find all nodes this points to
            for succ in self.G.successors(node):
                related.add(succ)
                traverse(succ, current_depth + 1)
        
        traverse(entity_id, 0)
        return related
    
    def find_similar(self, entity_id: str) -> Set[str]:
        """Find concepts similar to this one"""
        similar = set()
        
        if entity_id not in self.G:
            return similar
        
        # Direct similar_to edges
        for neighbor in self.G.successors(entity_id):
            edge_data = self.G.edges[entity_id, neighbor]
            if edge_data.get('relation') == RelationType.SIMILAR_TO.value:
                similar.add(neighbor)
        
        # Reverse similar_to edges
        for neighbor in self.G.predecessors(entity_id):
            edge_data = self.G.edges[neighbor, entity_id]
            if edge_data.get('relation') == RelationType.SIMILAR_TO.value:
                similar.add(neighbor)
        
        return similar
    
    def get_learning_path(self, start_id: str) -> List[str]:
        """
        Get suggested learning path starting from this concept.
        Order: prerequisites -> concept -> related -> specializations
        """
        path = []
        
        # Prerequisites first
        prerequisites = self.find_prerequisites(start_id)
        path.extend(prerequisites)
        
        # Main concept
        path.append(start_id)
        
        # Related concepts
        related = self.find_related(start_id)
        path.extend(related)
        
        return path
    
    def get_entity_info(self, entity_id: str) -> Dict | None:
        """Get all information about an entity"""
        if entity_id not in self.G:
            return None
        
        node_data = self.G.nodes[entity_id]
        
        return {
            'id': entity_id,
            'name': node_data.get('name'),
            'type': node_data.get('type'),
            'description': node_data.get('description'),
            'tutorial_id': node_data.get('tutorial_id'),
            'section': node_data.get('section'),
            'difficulty': node_data.get('difficulty'),
            'prerequisites': self.find_prerequisites(entity_id, depth=1),
            'related': self.find_related(entity_id, depth=1),
            'similar': self.find_similar(entity_id)
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # BATCH OPERATIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def load_from_json(self, entities_file: str, relationships_file: str):
        """Load entities and relationships from JSON files"""
        
        # Load entities
        with open(entities_file) as f:
            entities_data = json.load(f)
            for entity_dict in entities_data:
                # Extract only the fields that Entity expects
                entity = Entity(
                    id=entity_dict['id'],
                    name=entity_dict['name'],
                    entity_type=entity_dict.get('entity_type', entity_dict.get('type', 'unknown')),
                    description=entity_dict.get('description', ''),
                    tutorial_id=entity_dict.get('tutorial_id', ''),
                    section=entity_dict.get('section', ''),
                    difficulty=entity_dict.get('difficulty', 'intermediate'),
                    week=entity_dict.get('week', 0),
                    homework_weeks=entity_dict.get('homework_weeks', [])
                )
                self.add_entity(entity)
        
        print(f"✓ Loaded {len(entities_data)} entities")
        
        # Load relationships
        with open(relationships_file) as f:
            rels_data = json.load(f)
            for rel_dict in rels_data:
                # Handle both 'type' and 'relation_type' keys
                rel_type_str = rel_dict.get('relation_type', rel_dict.get('type', 'requires'))
                
                # Handle string relation types
                try:
                    if isinstance(rel_type_str, str):
                        # Map string to enum if it matches, otherwise keep as string
                        rel_type = rel_type_str
                    else:
                        rel_type = rel_type_str.value
                except (ValueError, AttributeError):
                    rel_type = rel_type_str
                
                rel = Relationship(
                    from_id=rel_dict['from_id'],
                    to_id=rel_dict['to_id'],
                    relation_type=rel_type,
                    confidence=rel_dict.get('confidence', 1.0),
                    explanation=rel_dict.get('explanation', '')
                )
                self.add_relationship(rel)
        
        print(f"✓ Loaded {len(rels_data)} relationships")
    
    def stats(self) -> Dict:
        """Get graph statistics"""
        return {
            'num_entities': self.G.number_of_nodes(),
            'num_relationships': self.G.number_of_edges(),
            'density': nx.density(self.G) if self.G.number_of_nodes() > 0 else 0,
            'is_connected': nx.is_strongly_connected(self.G) if self.G.number_of_nodes() > 0 else False,
            'nodes': self.G.number_of_nodes(),
            'edges': self.G.number_of_edges()
        }


# ═════════════════════════════════════════════════════════════════════════════
# HYBRID SEARCH (Vector + Graph)
# ═════════════════════════════════════════════════════════════════════════════

class HybridRetriever:
    """
    Combines vector search with graph traversal.
    
    Vector search finds semantically similar concepts.
    Graph traversal finds related concepts by structure.
    """
    
    def __init__(self, knowledge_graph: LightweightKnowledgeGraph, 
                 vector_db=None):  # Can integrate with Chroma later
        self.kg = knowledge_graph
        self.vector_db = vector_db
    
    def retrieve(self, query: str, top_k: int = 5) -> Dict:
        """
        Retrieve relevant materials for a query.
        
        Returns:
        {
            'direct': [matching concepts],
            'prerequisites': [what to learn first],
            'related': [what to learn after],
            'learning_path': [suggested order]
        }
        """
        
        # For now: simple name matching (later: replace with vector search)
        # Find closest entity by name
        best_match = None
        for entity_id in self.kg.G.nodes:
            entity_name = self.kg.G.nodes[entity_id].get('name', '')
            if query.lower() in entity_name.lower():
                best_match = entity_id
                break
        
        if not best_match:
            return {
                'direct': [],
                'prerequisites': [],
                'related': [],
                'learning_path': []
            }
        
        # Expand with graph
        info = self.kg.get_entity_info(best_match)
        path = self.kg.get_learning_path(best_match)
        
        return {
            'direct': [best_match],
            'prerequisites': list(info['prerequisites'])[:top_k],
            'related': list(info['related'])[:top_k],
            'similar': list(info['similar'])[:top_k],
            'learning_path': path
        }


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═════════════════════════════════════════════════════════════════════════════

def demo():
    """Demo: Build a small knowledge graph and query it"""
    
    print("🌐 Building lightweight knowledge graph...\n")
    
    # Initialize
    kg = LightweightKnowledgeGraph("demo_knowledge.db")
    
    # Add some entities
    entities = [
        Entity("concept_array", "Arrays", "data_structure", 
               "Linear data structure", "tutorial_0", "data_structures", "beginner"),
        Entity("concept_recursion", "Recursion", "concept",
               "Function calling itself", "tutorial_0", "advanced_concepts", "intermediate"),
        Entity("algo_bubble_sort", "Bubble Sort", "algorithm",
               "Simple O(n²) sorting", "tutorial_1", "sorting", "beginner"),
        Entity("algo_merge_sort", "Merge Sort", "algorithm",
               "Divide & conquer O(n log n)", "tutorial_1", "sorting", "intermediate"),
        Entity("algo_quicksort", "Quicksort", "algorithm",
               "Average O(n log n) sorting", "tutorial_1", "sorting", "intermediate"),
        Entity("concept_divide_conquer", "Divide and Conquer", "concept",
               "Algorithm design paradigm", "tutorial_0", "algorithms", "intermediate"),
    ]
    
    for entity in entities:
        kg.add_entity(entity)
    
    print(f"✓ Added {len(entities)} concepts\n")
    
    # Add relationships
    relationships = [
        Relationship("algo_bubble_sort", "concept_array", RelationType.REQUIRES,
                    explanation="Need to understand array indexing"),
        Relationship("algo_merge_sort", "concept_recursion", RelationType.REQUIRES,
                    explanation="Merge sort is recursive"),
        Relationship("algo_merge_sort", "concept_divide_conquer", RelationType.TEACHES),
        Relationship("algo_quicksort", "concept_recursion", RelationType.REQUIRES),
        Relationship("algo_merge_sort", "algo_quicksort", RelationType.SIMILAR_TO,
                    explanation="Both are O(n log n) sorts"),
        Relationship("algo_bubble_sort", "algo_merge_sort", RelationType.PREREQUISITE_FOR,
                    explanation="Learn simple sort before complex"),
    ]
    
    for rel in relationships:
        kg.add_relationship(rel)
    
    print(f"✓ Added {len(relationships)} relationships\n")
    
    # Query: "How do I learn Quicksort?"
    print("=" * 60)
    print("QUERY: How do I learn Quicksort?")
    print("=" * 60)
    
    retriever = HybridRetriever(kg)
    results = retriever.retrieve("Quicksort")
    
    print("\n📚 Learning Prerequisites:")
    for prereq_id in results['prerequisites']:
        name = kg.G.nodes[prereq_id].get('name')
        print(f"  • {name}")
    
    print("\n🎯 Main Concept:")
    for direct_id in results['direct']:
        info = kg.get_entity_info(direct_id)
        print(f"  • {info['name']}: {info['description']}")
    
    print("\n🔗 Related Concepts:")
    for related_id in results['related']:
        name = kg.G.nodes[related_id].get('name')
        print(f"  • {name}")
    
    print("\n📖 Suggested Learning Path:")
    for i, path_id in enumerate(results['learning_path'], 1):
        name = kg.G.nodes[path_id].get('name')
        print(f"  {i}. {name}")
    
    # Print stats
    print("\n" + "=" * 60)
    print("GRAPH STATISTICS")
    print("=" * 60)
    stats = kg.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    import sys
    
    if "--demo" in sys.argv:
        demo()
    else:
        print(__doc__)
