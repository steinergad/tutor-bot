# Language support for Socratic Tutor

LANGUAGES = {
    "en": {
        # Mode selection
        "mode_learn": "📖 Learn Material",
        "mode_homework": "💪 Solve Homework",
        "select_mode": "Select mode:",
        
        # UI Labels
        "current_question": "Current Problem",
        "solving": "Solving...",
        "clear_chat": "🗑 Clear",
        "settings": "⚙️ Settings",
        "api_key": "🔑 API Key",
        
        # Homework view
        "homework_details": "Homework Details",
        "description": "Description",
        "problems_count": "Problems",
        "topics": "Topics",
        "preview": "Preview",
        "key_concepts": "Key Concepts",
        
        # Messages
        "no_tutorials": "No tutorials loaded yet. Add tutorial PDFs to metadata.json",
        "no_homework": "No homework assignments loaded yet. Add homework.json to db/",
        "out_of_scope": "❌ Your question is outside the scope of this homework assignment.",
        "refocus": "Please focus on the current problem. You can ask about:",
        "type_question": "Type your question here...",
        
        # Tutor feedback
        "great_thinking": "Great thinking! Now",
        "correct_direction": "You're on the right track.",
        "think_about": "What did we learn about",
        "reference": "Recall from",
        
        # Language selector
        "language": "Language",
        "english": "English",
        "hebrew": "עברית",
    },
    "he": {
        # Mode selection
        "mode_learn": "📖 חומר למידה",
        "mode_homework": "💪 פתרו שיעורי בית",
        "select_mode": "בחר מצב:",
        
        # UI Labels
        "current_question": "בעיה נוכחית",
        "solving": "פותרים...",
        "clear_chat": "🗑 נקה",
        "settings": "⚙️ הגדרות",
        "api_key": "🔑 מפתח API",
        
        # Homework view
        "homework_details": "פרטי שיעורי בית",
        "description": "תיאור",
        "problems_count": "בעיות",
        "topics": "נושאים",
        "preview": "תצוגה מקדימה",
        "key_concepts": "מושגי מפתח",
        
        # Messages
        "no_tutorials": "אין הדרכות שנטענו עדיין. הוסף קבצי PDF הדרכות ל-metadata.json",
        "no_homework": "אין מטלות שיעורי בית שנטענו עדיין. הוסף homework.json ל-db/",
        "out_of_scope": "❌ השאלה שלך חוצה את ההיקף של מטלת שיעורי בית זו.",
        "refocus": "בואו נתמקד בבעיה הנוכחית. אתה יכול לשאול על:",
        "type_question": "הקלד את השאלה שלך כאן...",
        
        # Tutor feedback
        "great_thinking": "חשיבה נהדרת! עכשיו",
        "correct_direction": "אתה בכיוון הנכון.",
        "think_about": "מה למדנו על",
        "reference": "זכור מ",
        
        # Language selector
        "language": "שפה",
        "english": "English",
        "hebrew": "עברית",
    }
}

def get_text(lang: str, key: str) -> str:
    """Get translated text for given language and key."""
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)
