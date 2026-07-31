#!/usr/bin/env python3
"""
Phase 3: Build and Test Knowledge Graph
========================================
Build the knowledge graph from extracted entities and relationships,
then run comprehensive tests to validate the structure.

Usage:
    python build_knowledge_graph.py --build     # Build graph from entities/relationships
    python build_knowledge_graph.py --test      # Run test queries
    python build_knowledge_graph.py --stats     # Show graph statistics
    python build_knowledge_graph.py --all       # Build + test + stats
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from graph_rag_starter import (
    LightweightKnowledgeGraph,
    HybridRetriever,
    Entity,
    Relationship,
    RelationType
)


def build_graph():
    """Build knowledge graph from entities and relationships."""
    print("\n" + "=" * 70)
    print("PHASE 3: Building Knowledge Graph")
    print("=" * 70)
    
    db_path = Path(__file__).parent / "db" / "knowledge_graph.db"
    
    # Create/recreate database
    if db_path.exists():
        print(f"  ⚠️  Removing existing database: {db_path}")
        db_path.unlink()
    
    kg = LightweightKnowledgeGraph(str(db_path))
    print(f"  ✅ Created new database: {db_path}")
    
    # Load entities and relationships
    entities_file = Path(__file__).parent / "db" / "entities.json"
    relationships_file = Path(__file__).parent / "db" / "relationships.json"
    
    print(f"\n  Loading entities from: {entities_file}")
    with open(entities_file) as f:
        entities_data = json.load(f)
    print(f"  ✅ Loaded {len(entities_data)} entities")
    
    print(f"\n  Loading relationships from: {relationships_file}")
    with open(relationships_file) as f:
        relationships_data = json.load(f)
    print(f"  ✅ Loaded {len(relationships_data)} relationships")
    
    # Convert to Entity and Relationship objects
    entities = []
    for e in entities_data:
        entity = Entity(
            id=e["id"],
            name=e["name"],
            entity_type=e["entity_type"],
            description=e["description"],
            tutorial_id=e.get("tutorial_id", ""),
            section=e.get("section", ""),
            difficulty=e.get("difficulty", "beginner")
        )
        entities.append(entity)
    
    relationships = []
    for r in relationships_data:
        rel = Relationship(
            from_id=r["from_id"],
            to_id=r["to_id"],
            relation_type=r["relation_type"],
            confidence=r.get("confidence", 0.8),
            explanation=r.get("explanation", "")
        )
        relationships.append(rel)
    
    # Add to graph
    print("\n  Adding entities to graph...")
    added = 0
    for entity in entities:
        if kg.add_entity(entity):
            added += 1
    print(f"  ✅ Added {added} entities to graph")
    
    print("\n  Adding relationships to graph...")
    added = 0
    for rel in relationships:
        if kg.add_relationship(rel):
            added += 1
    print(f"  ✅ Added {added} relationships to graph")
    
    print(f"\n  ✅ Knowledge graph built successfully!")
    return kg


def test_queries(kg: LightweightKnowledgeGraph):
    """Run test queries against the knowledge graph."""
    print("\n" + "=" * 70)
    print("PHASE 3: Testing Knowledge Graph Queries")
    print("=" * 70)
    
    retriever = HybridRetriever(kg)
    
    # Test queries
    test_queries_list = [
        ("Merge Sort", "Specific algorithm"),
        ("Dynamic Programming", "Technique"),
        ("Time Complexity", "Concept"),
        ("Fibonacci", "Classic DP problem"),
        ("Greedy", "Algorithm paradigm"),
        ("Recursion", "Foundational concept"),
        ("Array", "Basic data structure"),
        ("Tree", "Advanced data structure"),
    ]
    
    print(f"\nRunning {len(test_queries_list)} test queries...\n")
    
    for query, query_type in test_queries_list:
        print(f"  📋 Query: '{query}' ({query_type})")
        
        try:
            result = retriever.retrieve(query, top_k=5)
            
            if result["direct"]:
                print(f"     ✅ Direct match: {result['direct'][0]}")
            else:
                print(f"     ℹ️  No direct match (searching graph)")
            
            if result["prerequisites"]:
                prereqs = [kg.get_entity_info(e)["name"] for e in result["prerequisites"][:2]]
                print(f"     📚 Prerequisites: {', '.join(prereqs)}")
            
            if result["related"]:
                related = [kg.get_entity_info(e)["name"] for e in result["related"][:2]]
                print(f"     🔗 Related: {', '.join(related)}")
            
            if result["learning_path"]:
                path = [kg.get_entity_info(e)["name"] for e in result["learning_path"][:3]]
                print(f"     📖 Learning path: {' → '.join(path)}")
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        print()


def show_statistics(kg: LightweightKnowledgeGraph):
    """Show graph statistics and connectivity analysis."""
    print("\n" + "=" * 70)
    print("PHASE 3: Knowledge Graph Statistics")
    print("=" * 70)
    
    stats = kg.stats()
    
    print(f"\n  Graph Size:")
    print(f"    • Nodes (concepts):  {stats['nodes']}")
    print(f"    • Edges (relations): {stats['edges']}")
    print(f"    • Density:          {stats['density']:.4f}")
    
    print(f"\n  Connectivity:")
    print(f"    • Is connected:     {'✅ Yes' if stats['is_connected'] else '❌ No (disconnected components exist)'}")
    
    # Show top entities by connectivity
    print(f"\n  Most Connected Entities (by out-degree):")
    
    from collections import defaultdict
    out_degree = defaultdict(int)
    
    for from_id in kg.G.nodes():
        out_degree[from_id] = len(list(kg.G.successors(from_id)))
    
    top_entities = sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for entity_id, degree in top_entities:
        try:
            entity_info = kg.get_entity_info(entity_id)
            print(f"    • {entity_info['name']}: {degree} outgoing edges")
        except:
            pass
    
    # Entity type distribution
    print(f"\n  Entity Type Distribution:")
    type_counts = defaultdict(int)
    
    with kg.conn.cursor() as cur:
        cur.execute("SELECT entity_type, COUNT(*) as count FROM entities GROUP BY entity_type")
        for entity_type, count in cur.fetchall():
            type_counts[entity_type] = count
    
    for entity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    • {entity_type}: {count}")
    
    # Relationship type distribution
    print(f"\n  Relationship Type Distribution:")
    rel_counts = defaultdict(int)
    
    with kg.conn.cursor() as cur:
        cur.execute("SELECT relation_type, COUNT(*) as count FROM relationships GROUP BY relation_type")
        for rel_type, count in cur.fetchall():
            rel_counts[rel_type] = count
    
    for rel_type, count in sorted(rel_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    • {rel_type}: {count}")


def verify_graph():
    """Verify graph integrity and return any warnings."""
    print("\n" + "=" * 70)
    print("PHASE 3: Graph Integrity Check")
    print("=" * 70)
    
    db_path = Path(__file__).parent / "db" / "knowledge_graph.db"
    kg = LightweightKnowledgeGraph(str(db_path))
    
    warnings = []
    errors = []
    
    # Check for orphaned nodes
    print("\n  Checking for orphaned entities...")
    with kg.conn.cursor() as cur:
        cur.execute("""
            SELECT e.id, e.name FROM entities e
            WHERE e.id NOT IN (
                SELECT from_id FROM relationships
                UNION
                SELECT to_id FROM relationships
            )
        """)
        orphaned = cur.fetchall()
        if orphaned:
            warnings.append(f"Found {len(orphaned)} orphaned entities (no relationships)")
        else:
            print("  ✅ No orphaned entities")
    
    # Check for broken relationships
    print("\n  Checking for broken relationships...")
    with kg.conn.cursor() as cur:
        cur.execute("""
            SELECT r.id, r.from_id, r.to_id FROM relationships r
            WHERE r.from_id NOT IN (SELECT id FROM entities)
            OR r.to_id NOT IN (SELECT id FROM entities)
        """)
        broken = cur.fetchall()
        if broken:
            errors.append(f"Found {len(broken)} broken relationships (missing entities)")
        else:
            print("  ✅ No broken relationships")
    
    # Check relationship type validity
    print("\n  Checking relationship types...")
    valid_types = [t.value for t in RelationType]
    with kg.conn.cursor() as cur:
        cur.execute("SELECT DISTINCT relation_type FROM relationships")
        db_types = [row[0] for row in cur.fetchall()]
        invalid = set(db_types) - set(valid_types)
        if invalid:
            warnings.append(f"Found {len(invalid)} invalid relationship types: {invalid}")
        else:
            print("  ✅ All relationship types are valid")
    
    # Summary
    print("\n" + "-" * 70)
    if errors:
        print(f"  ❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"     • {error}")
    else:
        print("  ✅ No errors found")
    
    if warnings:
        print(f"\n  ⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"     • {warning}")
    else:
        print("  ✅ No warnings found")
    
    return len(errors) == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Phase 3: Build and test knowledge graph"
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build graph from entities/relationships"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test queries"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show graph statistics"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify graph integrity"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build + test + stats + verify"
    )
    
    args = parser.parse_args()
    
    # If no args, show help
    if not any([args.build, args.test, args.stats, args.verify, args.all]):
        parser.print_help()
        return 1
    
    try:
        if args.all or args.build:
            kg = build_graph()
        else:
            db_path = Path(__file__).parent / "db" / "knowledge_graph.db"
            if not db_path.exists():
                print(f"Error: Knowledge graph not found at {db_path}")
                print("Run with --build first")
                return 1
            kg = LightweightKnowledgeGraph(str(db_path))
        
        if args.all or args.verify:
            verify_graph()
        
        if args.all or args.test:
            test_queries(kg)
        
        if args.all or args.stats:
            show_statistics(kg)
        
        print("\n" + "=" * 70)
        print("✅ Phase 3 Complete!")
        print("=" * 70)
        print("\nNext Steps:")
        print("  1. Review test results above")
        print("  2. Adjust entities or relationships if needed")
        print("  3. Move to Phase 4: Integration with app.py")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
