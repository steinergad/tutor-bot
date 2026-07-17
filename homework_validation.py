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
    """Extract meaningful keywords from text (supports English and Hebrew)."""
    # English stop words
    en_stop_words = {
        "the", "a", "an", "is", "are", "was", "be", "been", "how", "what",
        "when", "where", "why", "do", "does", "can", "could", "would", "should",
        "if", "else", "for", "in", "on", "at", "to", "from", "of", "or", "and",
        "this", "that", "these", "those", "i", "you", "we", "they", "my", "your",
        "about", "with", "by", "as", "not", "no", "yes", "ok", "please", "thanks",
        "question", "ask", "help", "need", "want", "get", "make",
    }
    
    # Hebrew stop words
    he_stop_words = {
        "את", "של", "אני", "אתה", "הוא", "היא", "הם", "הן", "זה", "זאת", 
        "עם", "על", "אל", "מן", "לא", "כן", "או", "ו", "ל", "מ", "כ",
        "זה", "כמו", "בין", "מה", "איך", "למה", "כיצד", "הוא", "היא",
        "עזור", "לעזור", "שאלה", "שוא", "לשאול", "צריך", "רוצה", "יכול",
    }
    
    combined_stop_words = en_stop_words | he_stop_words
    
    # Extract English words
    en_words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Extract Hebrew words (Hebrew Unicode range)
    he_words = re.findall(r'[\u05D0-\u05EA]+', text)
    
    # Combine and filter
    all_words = en_words + he_words
    keywords = [w for w in all_words if len(w) > 2 and w not in combined_stop_words]
    return keywords


def normalize_keyword(word: str) -> str:
    """Normalize keywords to handle plurals and common variants."""
    # Handle common singular/plural forms
    if word.endswith('s') and len(word) > 3:
        # Try singular form: "algorithms" → "algorithm", "loops" → "loop"
        return word[:-1]
    return word


def get_scope_error_message(hw_key: str, lang: str = "en") -> str:
    """
    Get an out-of-scope error message in the specified language.
    
    Args:
        hw_key: Current homework key  
        lang: Language for output ("en" or "he")
    
    Returns:
        Out-of-scope error message in the specified language
    """
    scope = get_homework_scope(hw_key)
    
    if lang == "he":
        return f"❌ השאלה הזו לא נראית קשורה ל{scope['title']}. בואו נתמקד בבעיה הנוכחית."
    else:  # English (default)
        return f"❌ This question doesn't seem to relate to {scope['title']}. Please focus on the current problem."


def is_in_scope(query: str, hw_key: str, curriculum_topics: List[str] = None) -> Tuple[bool, str]:
    """
    Check if a query is within the scope of the current homework.
    
    Args:
        query: Student's question (English or Hebrew)
        hw_key: Current homework key
        curriculum_topics: Optional list of all curriculum topics (for cross-hw detection)
    
    Returns:
        (is_valid, reason_if_invalid)
    """
    scope = get_homework_scope(hw_key)
    
    # ── First check: Is this clearly a homework help question? ──────────────────────
    # Common Hebrew homework help phrases
    he_homework_phrases = ["עזור", "בעיה", "משימה", "תרגיל", "צריך"]
    en_homework_phrases = ["help", "problem", "question", "stuck", "confused", "understand"]
    
    has_he_homework = any(phrase in query for phrase in he_homework_phrases)
    has_en_homework = any(phrase in query.lower() for phrase in en_homework_phrases)
    
    if has_he_homework or has_en_homework:
        # Student is clearly asking for homework help - allow it
        return True, ""
    
    # ── Second check: Keyword-based scope validation ──────────────────────────────
    # Extract keywords from query (works for both English and Hebrew)
    query_keywords = set(extract_keywords(query))
    
    if not query_keywords:
        return True, ""  # Generic question OK if no specific keywords
    
    # Build scope keywords (topics + concepts) with normalization
    scope_keywords = set()
    for topic in scope["topics"]:
        for kw in extract_keywords(topic):
            scope_keywords.add(normalize_keyword(kw))
    for concept in scope["key_concepts"]:
        for kw in extract_keywords(concept):
            scope_keywords.add(normalize_keyword(kw))
    
    # Normalize query keywords too
    normalized_query = {normalize_keyword(kw) for kw in query_keywords}
    
    # Check for strong topical overlap (at least 20% of query keywords in scope)
    if scope_keywords:
        overlap = len(normalized_query & scope_keywords) / len(normalized_query)
        if overlap < 0.20:  # Less than 20% match = probably out of scope
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


def get_scope_reminder(hw_key: str, lang: str = "en") -> str:
    """
    Generate a reminder of what the student can ask about.
    
    Args:
        hw_key: Current homework key
        lang: Language for output ("en" or "he")
    
    Returns:
        Formatted string listing allowed topics
    """
    scope = get_homework_scope(hw_key)
    
    topics_str = ", ".join(scope["topics"])
    concepts_str = ", ".join(scope["key_concepts"])
    
    if lang == "he":
        return (
            f"**{scope['title']}** כוללת:\n"
            f"• **נושאים**: {topics_str}\n"
            f"• **מושגים**: {concepts_str}\n"
            f"\nבואו נשתמש לשאלות הקשורות לנושאים אלה."
        )
    else:  # English (default)
        return (
            f"**{scope['title']}** covers:\n"
            f"• **Topics**: {topics_str}\n"
            f"• **Concepts**: {concepts_str}\n"
            f"\nPlease ask questions related to these topics."
        )
