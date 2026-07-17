"""
homework_validation.py — Enforce homework scope and validate questions

Ensures students stay focused on the current homework assignment and 
don't ask off-topic questions.
"""

import json
from pathlib import Path
from typing import Tuple, List
import re


def load_homework_data() -> dict:
    """Load homework database."""
    hw_file = Path("db/homework.json")
    return json.loads(hw_file.read_text(encoding="utf-8")) if hw_file.exists() else {}


def get_homework_scope(hw_key: str) -> dict:
    """
    Get the scope (topics, concepts, keywords) for a homework assignment.
    
    Args:
        hw_key: Homework identifier (e.g., 'hw_1')
    
    Returns:
        Dictionary with: topics, key_concepts, week_num
    """
    hw_data = load_homework_data().get(hw_key, {})
    
    return {
        "topics": hw_data.get("topics", []),
        "key_concepts": hw_data.get("key_concepts", []),
        "title": hw_data.get("title", hw_key),
        "week": hw_data.get("week", 0),
        "description": hw_data.get("description", ""),
    }


def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text."""
    # Remove common words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "be", "been", "how", "what",
        "when", "where", "why", "do", "does", "can", "could", "would", "should",
        "if", "else", "for", "in", "on", "at", "to", "from", "of", "or", "and",
        "this", "that", "these", "those", "i", "you", "we", "they", "my", "your",
        "about", "with", "by", "as", "not", "no", "yes", "ok", "please", "thanks",
        "question", "question", "ask", "help", "need", "want", "get", "make",
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]+\b', text.lower())
    keywords = [w for w in words if len(w) > 2 and w not in stop_words]
    return keywords


def is_in_scope(query: str, hw_key: str, curriculum_topics: List[str] = None) -> Tuple[bool, str]:
    """
    Check if a query is within the scope of the current homework.
    
    Args:
        query: Student's question
        hw_key: Current homework key
        curriculum_topics: Optional list of all curriculum topics (for cross-hw detection)
    
    Returns:
        (is_valid, reason_if_invalid)
    """
    scope = get_homework_scope(hw_key)
    
    # Extract keywords from query
    query_keywords = set(extract_keywords(query))
    
    if not query_keywords:
        return True, ""  # Generic question OK if no specific keywords
    
    # Build scope keywords (topics + concepts)
    scope_keywords = set()
    for topic in scope["topics"]:
        scope_keywords.update(extract_keywords(topic))
    for concept in scope["key_concepts"]:
        scope_keywords.update(extract_keywords(concept))
    
    # Check for strong topical overlap (at least 30% of query keywords in scope)
    if scope_keywords:
        overlap = len(query_keywords & scope_keywords) / len(query_keywords)
        if overlap < 0.3:  # Less than 30% match = potentially out of scope
            # Additional check: is it asking about a DIFFERENT homework?
            if curriculum_topics:
                for other_topic in curriculum_topics:
                    if other_topic not in scope["topics"]:
                        # Check if this topic is mentioned in the query
                        if any(kw in extract_keywords(other_topic) for kw in query_keywords):
                            return False, f"You're asking about {other_topic}, which is not part of {scope['title']}."
            
            # Ambiguous but probably out of scope
            return False, f"This question doesn't seem to relate to {scope['title']}. Please focus on the current problem."
    
    return True, ""


def get_scope_reminder(hw_key: str) -> str:
    """
    Generate a reminder of what the student can ask about.
    
    Args:
        hw_key: Current homework key
    
    Returns:
        Formatted string listing allowed topics
    """
    scope = get_homework_scope(hw_key)
    
    topics_str = ", ".join(scope["topics"])
    concepts_str = ", ".join(scope["key_concepts"])
    
    return (
        f"**{scope['title']}** covers:\n"
        f"• **Topics**: {topics_str}\n"
        f"• **Concepts**: {concepts_str}\n"
        f"\nPlease ask questions related to these topics."
    )
