"""
search_integration.py — Integration of vector search into tutoring app

Provides unified search interface that can switch between:
1. Keyword-based search (fast, low accuracy)
2. Vector-based search (slower, higher accuracy)

Usage in app.py:
    from search_integration import find_relevant_topics
    
    topics = find_relevant_topics("How does merge sort work?", top_k=5)
"""

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
import os

# Try to use vector DB if available, fall back to keyword search
_vdb = None
_use_vector_db = False

def init_search(db_dir: str = "db"):
    """Initialize search system (vector DB if available)"""
    global _vdb, _use_vector_db
    
    try:
        from vector_db import VectorDB
        _vdb = VectorDB(db_path=f"{db_dir}/chroma_vector_store")
        metadata_path = Path(db_dir) / "metadata.json"
        if metadata_path.exists():
            _vdb.build_database(str(metadata_path))
            _use_vector_db = True
            print("[Search] Vector DB initialized successfully")
    except Exception as e:
        print(f"[Search] Vector DB not available, using keyword search: {e}")
        _use_vector_db = False


def find_relevant_topics(
    query: str,
    top_k: int = 5,
    use_vector: bool = True
) -> List[Tuple[str, float, str]]:
    """
    Find relevant topics for a student query
    
    Args:
        query: Student question (e.g., "How does merge sort work?")
        top_k: Number of results to return
        use_vector: Try to use vector DB first (falls back to keyword if unavailable)
    
    Returns:
        List of (topic_name, similarity_score, tutorial_id) tuples
    """
    
    # Initialize on first use
    if _vdb is None and use_vector:
        init_search()
    
    # Try vector search first
    if use_vector and _use_vector_db and _vdb:
        try:
            result = _vdb.search(query, top_k=top_k, similarity_threshold=0.2)
            topics = result.get("topics", [])
            tutorials = result.get("tutorial_ids", [])
            
            # Return with tutorial info
            output = []
            for topic, score in topics[:top_k]:
                # Find which tutorial has this topic
                tutorial_id = _find_tutorial_for_topic(topic, tutorials)
                output.append((topic, score, tutorial_id))
            return output
        except Exception as e:
            print(f"[Search] Vector search failed: {e}, falling back to keyword search")
            _use_vector_db = False
    
    # Fall back to keyword search
    return _keyword_search(query, top_k)


def _keyword_search(query: str, top_k: int = 5) -> List[Tuple[str, float, str]]:
    """Fallback: simple keyword matching"""
    metadata_file = Path("db/metadata.json")
    if not metadata_file.exists():
        return []
    
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    
    keywords = set(w.lower() for w in query.split() if len(w) > 3)
    matches = []
    
    for tutorial_id, tutorial_data in metadata.items():
        topics = tutorial_data.get("topics", [])
        for topic in topics:
            # Simple scoring: how many keywords match
            topic_lower = topic.lower()
            score = sum(1 for kw in keywords if kw in topic_lower) / max(len(keywords), 1)
            if score > 0:
                matches.append((topic, score, tutorial_id))
    
    # Sort by score and return top_k
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_k]


def _find_tutorial_for_topic(topic: str, preferred_tutorials: List[str] = None) -> str:
    """Find which tutorial a topic belongs to"""
    metadata_file = Path("db/metadata.json")
    if not metadata_file.exists():
        return "unknown"
    
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    
    # First check preferred tutorials
    if preferred_tutorials:
        for tutorial_id in preferred_tutorials:
            if tutorial_id in metadata:
                topics = metadata[tutorial_id].get("topics", [])
                if topic in topics:
                    return tutorial_id
    
    # Then search all
    for tutorial_id, tutorial_data in metadata.items():
        if topic in tutorial_data.get("topics", []):
            return tutorial_id
    
    return "unknown"


def get_search_method() -> str:
    """Get current search method being used"""
    return "vector_db" if _use_vector_db else "keyword"


def get_search_stats() -> Dict[str, Any]:
    """Get search system statistics"""
    if _vdb:
        return _vdb.stats()
    return {"method": "keyword", "status": "fallback"}
