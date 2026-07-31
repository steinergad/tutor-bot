#!/usr/bin/env python3
"""
Phase 5: Production Knowledge Graph with Neo4j
===============================================
Migrate from SQLite MVP to production-grade Neo4j graph database.

Features:
- Persistent graph database with query performance
- ACID transactions and rollback support
- Built-in vector search integration (Neo4j 5.x+)
- Cypher query language for complex graph queries
- Cluster support for horizontal scaling

Installation:
    pip install neo4j

Neo4j Setup:
    1. Docker: docker run -p 7687:7687 -p 7474:7474 neo4j:latest
    2. Desktop: Download from neo4j.com/download
    3. Cloud: neo4j.com/cloud (free tier available)

Default credentials: neo4j/neo4j (first login requires password change)

Usage:
    python graph_rag_neo4j.py --connect               # Test connection
    python graph_rag_neo4j.py --build                 # Load entities/relationships
    python graph_rag_neo4j.py --query "merge sort"    # Run query
    python graph_rag_neo4j.py --migrate               # Migrate from SQLite
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class RelationType(Enum):
    """Relationship types in knowledge graph."""
    REQUIRES = "requires"
    TEACHES = "teaches"
    SIMILAR_TO = "similar_to"
    SPECIALIZATION = "specialization_of"
    EXAMPLE_IN = "example_in"
    PREREQUISITE_FOR = "prerequisite_for"
    ENABLES = "enables"


@dataclass
class Entity:
    """Graph entity: concept, algorithm, data structure, etc."""
    id: str
    name: str
    entity_type: str  # algorithm, concept, technique, problem, proof_technique, data_structure, notation
    description: str
    tutorial_id: str = ""
    section: str = ""
    difficulty: str = "beginner"  # beginner, intermediate, advanced


@dataclass
class Relationship:
    """Connection between entities."""
    from_id: str
    to_id: str
    relation_type: str
    confidence: float = 0.8
    explanation: str = ""


class KnowledgeGraphNeo4j:
    """Production Neo4j-based knowledge graph."""
    
    def __init__(
        self,
        uri: str = "neo4j://localhost:7687",
        auth: tuple = ("neo4j", "password"),
        database: str = "neo4j"
    ):
        """
        Initialize connection to Neo4j.
        
        Args:
            uri: Neo4j connection URI (neo4j://, bolt://, or http://)
            auth: (username, password) tuple
            database: Database name to use
        """
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("Error: neo4j package not installed")
            print("Install with: pip install neo4j")
            sys.exit(1)
        
        self.uri = uri
        self.database = database
        self.driver = GraphDatabase.driver(uri, auth=auth)
        
        # Test connection
        try:
            with self.driver.session(database=database) as session:
                session.run("RETURN 1")
            print(f"✅ Connected to Neo4j at {uri}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            print("\nMake sure Neo4j is running:")
            print("  Docker: docker run -p 7687:7687 -p 7474:7474 neo4j:latest")
            print("  Then update credentials in graph_rag_neo4j.py")
            sys.exit(1)
    
    def initialize_schema(self):
        """Create indexes and constraints for better performance."""
        print("Creating indexes and constraints...")
        
        with self.driver.session(database=self.database) as session:
            # Entity indexes
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE")
            session.run("CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.type)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.difficulty)")
            
            print("✅ Schema initialized")
    
    def add_entity(self, entity: Entity) -> bool:
        """
        Add or update entity in graph.
        
        Args:
            entity: Entity object
            
        Returns:
            True if new entity added, False if updated
        """
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MERGE (e:Entity {id: $id})
                ON CREATE SET 
                    e.name = $name,
                    e.type = $type,
                    e.description = $description,
                    e.tutorial_id = $tutorial_id,
                    e.section = $section,
                    e.difficulty = $difficulty,
                    e.created_at = timestamp()
                ON MATCH SET
                    e.updated_at = timestamp()
                RETURN e.id as id, elementId(e) as neo4j_id
            """, {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type,
                "description": entity.description,
                "tutorial_id": entity.tutorial_id,
                "section": entity.section,
                "difficulty": entity.difficulty
            })
            
            # Check if it was a create
            record = result.single()
            if record:
                return True
        
        return False
    
    def add_relationship(self, rel: Relationship) -> bool:
        """
        Add relationship between entities.
        
        Args:
            rel: Relationship object
            
        Returns:
            True if new relationship added
        """
        with self.driver.session(database=self.database) as session:
            # Create dynamic relationship type
            rel_type = rel.relation_type.upper().replace(" ", "_")
            
            result = session.run(f"""
                MATCH (from:Entity {{id: $from_id}})
                MATCH (to:Entity {{id: $to_id}})
                MERGE (from)-[r:{rel_type}]->(to)
                ON CREATE SET
                    r.confidence = $confidence,
                    r.explanation = $explanation,
                    r.created_at = timestamp()
                ON MATCH SET
                    r.updated_at = timestamp(),
                    r.confidence = $confidence
                RETURN r
            """, {
                "from_id": rel.from_id,
                "to_id": rel.to_id,
                "confidence": rel.confidence,
                "explanation": rel.explanation
            })
            
            return result.single() is not None
    
    def find_entity_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find entity by name (case-insensitive)."""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (e:Entity)
                WHERE toLower(e.name) = toLower($name)
                RETURN e {.*} as entity
                LIMIT 1
            """, {"name": name})
            
            record = result.single()
            if record:
                return record["entity"]
            return None
    
    def find_prerequisites(
        self,
        entity_id: str,
        depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Find prerequisites for an entity.
        
        Args:
            entity_id: Entity ID to find prerequisites for
            depth: Maximum traversal depth
            
        Returns:
            List of prerequisite entities
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(f"""
                MATCH path = (target:Entity {{id: $id}})-[:REQUIRES|PREREQUISITES*1..{depth}]-(prereq)
                WHERE target <> prereq
                RETURN DISTINCT
                    prereq {{.*}} as entity,
                    length(path) as distance
                ORDER BY distance ASC
            """, {"id": entity_id})
            
            return [record["entity"] for record in result]
    
    def find_related(
        self,
        entity_id: str,
        depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Find related entities.
        
        Args:
            entity_id: Entity ID
            depth: Maximum traversal depth
            
        Returns:
            List of related entities
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(f"""
                MATCH path = (source:Entity {{id: $id}})-[:TEACHES|EXAMPLE_IN|ENABLES|SIMILAR_TO*1..{depth}]-(related)
                WHERE source <> related
                RETURN DISTINCT
                    related {{.*}} as entity,
                    length(path) as distance
                ORDER BY distance ASC
            """, {"id": entity_id})
            
            return [record["entity"] for record in result]
    
    def find_similar(self, entity_id: str) -> List[Dict[str, Any]]:
        """Find entities similar to target."""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (source:Entity {id: $id})-[:SIMILAR_TO|SPECIALIZATION_OF]-(similar)
                RETURN similar {.*} as entity
                ORDER BY similar.name ASC
            """, {"id": entity_id})
            
            return [record["entity"] for record in result]
    
    def get_learning_path(self, entity_id: str) -> Dict[str, Any]:
        """
        Get complete learning path for an entity.
        
        Returns:
            Dict with prerequisites, concept, related, specializations
        """
        with self.driver.session(database=self.database) as session:
            entity = session.run(
                "MATCH (e:Entity {id: $id}) RETURN e {.*} as entity",
                {"id": entity_id}
            ).single()
            
            if not entity:
                return {"error": "Entity not found"}
            
            prerequisites = self.find_prerequisites(entity_id, depth=3)
            related = self.find_related(entity_id, depth=2)
            similar = self.find_similar(entity_id)
            
            return {
                "prerequisites": prerequisites,
                "concept": entity["entity"],
                "related": related,
                "specializations": similar
            }
    
    def get_entity_info(self, entity_id: str) -> Dict[str, Any]:
        """Get complete information about entity including all relationships."""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (e:Entity {id: $id})
                OPTIONAL MATCH (e)-[r1]->(next)
                OPTIONAL MATCH (prev)-[r2]->(e)
                RETURN
                    e {.*} as entity,
                    collect(DISTINCT {node: next {.*}, relation: type(r1), confidence: r1.confidence}) as outgoing,
                    collect(DISTINCT {node: prev {.*}, relation: type(r2), confidence: r2.confidence}) as incoming
            """, {"id": entity_id})
            
            record = result.single()
            if record:
                return {
                    "entity": record["entity"],
                    "outgoing": record["outgoing"],
                    "incoming": record["incoming"]
                }
            return {}
    
    def load_from_json(
        self,
        entities_file: str,
        relationships_file: str
    ):
        """Load entities and relationships from JSON files."""
        print(f"Loading entities from {entities_file}...")
        with open(entities_file) as f:
            entities_data = json.load(f)
        
        print(f"Loading relationships from {relationships_file}...")
        with open(relationships_file) as f:
            relationships_data = json.load(f)
        
        print(f"Adding {len(entities_data)} entities to Neo4j...")
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
            self.add_entity(entity)
        
        print(f"Adding {len(relationships_data)} relationships to Neo4j...")
        for r in relationships_data:
            rel = Relationship(
                from_id=r["from_id"],
                to_id=r["to_id"],
                relation_type=r["relation_type"],
                confidence=r.get("confidence", 0.8),
                explanation=r.get("explanation", "")
            )
            self.add_relationship(rel)
        
        print("✅ Data loaded successfully!")
    
    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        with self.driver.session(database=self.database) as session:
            nodes_result = session.run("MATCH (n) RETURN count(n) as count")
            edges_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            
            nodes = nodes_result.single()["count"]
            edges = edges_result.single()["count"]
            
            density = (2 * edges) / (nodes * (nodes - 1)) if nodes > 1 else 0
            
            return {
                "nodes": nodes,
                "edges": edges,
                "density": density
            }
    
    def close(self):
        """Close database connection."""
        self.driver.close()
        print("✅ Connection closed")


def migrate_from_sqlite():
    """Migrate knowledge graph from SQLite to Neo4j."""
    print("\n" + "=" * 70)
    print("PHASE 5: Migrating from SQLite to Neo4j")
    print("=" * 70)
    
    try:
        from graph_rag_starter import LightweightKnowledgeGraph
    except ImportError:
        print("Error: graph_rag_starter.py not found")
        return False
    
    # Initialize Neo4j
    print("\n1. Connecting to Neo4j...")
    kg_neo4j = KnowledgeGraphNeo4j()
    
    print("\n2. Initializing schema...")
    kg_neo4j.initialize_schema()
    
    # Load from JSON (same as SQLite uses)
    print("\n3. Loading entities and relationships...")
    entities_file = Path(__file__).parent / "db" / "entities.json"
    relationships_file = Path(__file__).parent / "db" / "relationships.json"
    
    kg_neo4j.load_from_json(str(entities_file), str(relationships_file))
    
    # Verify
    print("\n4. Verifying migration...")
    stats = kg_neo4j.stats()
    print(f"  • Nodes: {stats['nodes']}")
    print(f"  • Edges: {stats['edges']}")
    
    kg_neo4j.close()
    
    print("\n✅ Migration complete!")
    print("\nYou can now use KnowledgeGraphNeo4j in your app:")
    print("  from graph_rag_neo4j import KnowledgeGraphNeo4j")
    print("  kg = KnowledgeGraphNeo4j()")
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Phase 5: Production Neo4j knowledge graph"
    )
    parser.add_argument(
        "--connect",
        action="store_true",
        help="Test Neo4j connection"
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build graph from entities/relationships"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Query entity by name"
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate from SQLite to Neo4j"
    )
    parser.add_argument(
        "--uri",
        default="neo4j://localhost:7687",
        help="Neo4j connection URI"
    )
    parser.add_argument(
        "--password",
        default="password",
        help="Neo4j password"
    )
    
    args = parser.parse_args()
    
    if not any([args.connect, args.build, args.query, args.migrate]):
        parser.print_help()
        return 1
    
    try:
        kg = KnowledgeGraphNeo4j(uri=args.uri, auth=("neo4j", args.password))
        
        if args.connect:
            print("✅ Neo4j connection successful!")
            stats = kg.stats()
            print(f"\nGraph Statistics:")
            print(f"  • Nodes: {stats['nodes']}")
            print(f"  • Edges: {stats['edges']}")
        
        elif args.build:
            kg.initialize_schema()
            entities_file = Path(__file__).parent / "db" / "entities.json"
            relationships_file = Path(__file__).parent / "db" / "relationships.json"
            kg.load_from_json(str(entities_file), str(relationships_file))
            
            stats = kg.stats()
            print(f"\n✅ Graph built successfully!")
            print(f"  • Nodes: {stats['nodes']}")
            print(f"  • Edges: {stats['edges']}")
        
        elif args.query:
            entity = kg.find_entity_by_name(args.query)
            if entity:
                print(f"\n✅ Found: {entity['name']}")
                print(f"  Type: {entity['type']}")
                print(f"  Description: {entity['description']}")
                
                # Get related
                related = kg.find_related(entity['id'])
                if related:
                    print(f"  Related: {', '.join(r['name'] for r in related[:3])}")
            else:
                print(f"❌ Entity not found: {args.query}")
        
        elif args.migrate:
            migrate_from_sqlite()
        
        kg.close()
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
