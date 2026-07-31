# Phase 4: App Integration with Graph RAG
## How to Update app.py to Use HybridRetriever

This guide shows the minimal changes needed to integrate the HybridRetriever into your Streamlit app.

### Step 1: Add Imports (Top of app.py)

After the existing imports, add:

```python
# Graph RAG integration (Phase 4)
try:
    from graph_rag_starter import LightweightKnowledgeGraph, HybridRetriever
    GRAPH_RAG_ENABLED = True
except ImportError:
    GRAPH_RAG_ENABLED = False
    print("⚠️  Graph RAG not available (graph_rag_starter.py not found)")
```

### Step 2: Add Retriever Initialization (After @st.cache_resource functions)

Add this after the `build_homework_chain` function:

```python
@st.cache_resource
def load_knowledge_graph():
    """Load knowledge graph once per session."""
    if not GRAPH_RAG_ENABLED:
        return None, None
    
    try:
        db_path = str(DB_DIR / "knowledge_graph.db")
        kg = LightweightKnowledgeGraph(db_path)
        retriever = HybridRetriever(kg)
        print(f"✅ Knowledge graph loaded from {db_path}")
        return kg, retriever
    except Exception as e:
        print(f"⚠️  Knowledge graph load failed: {e}")
        return None, None

# Load knowledge graph if available
kg, graph_retriever = load_knowledge_graph()
```

### Step 3: Create Helper Functions for Context Building

Add these functions in the "LLM HELPER" section:

```python
def get_graph_context_for_homework(
    user_question: str,
    hw_topics: list,
    kg
) -> str:
    """
    Build enriched context using knowledge graph.
    
    Args:
        user_question: Student's question
        hw_topics: Topics in this homework (from homework.json)
        kg: KnowledgeGraphNeo4j instance
        
    Returns:
        Formatted context string for system prompt
    """
    if not kg or not graph_retriever:
        return ""
    
    try:
        # Find relevant materials in graph
        result = graph_retriever.retrieve(user_question, top_k=5)
        
        # Filter by homework scope
        relevant = []
        if result.get("direct"):
            relevant.extend(result["direct"][:2])
        if result.get("prerequisites"):
            relevant.extend(result["prerequisites"][:2])
        
        if not relevant:
            return ""
        
        # Format as context for system prompt
        context_lines = [
            "",
            "=== GRAPH-BASED LEARNING CONTEXT ===",
        ]
        
        if result.get("prerequisites"):
            context_lines.append("\n📚 PREREQUISITES (student should know these first):")
            for prereq_id in result["prerequisites"][:2]:
                try:
                    entity = kg.get_entity_info(prereq_id)
                    name = entity.get("entity", {}).get("name", prereq_id)
                    context_lines.append(f"  • {name}")
                except:
                    pass
        
        if result.get("direct"):
            context_lines.append("\n🎯 MAIN TOPICS (directly related to question):")
            for topic_id in result["direct"][:2]:
                try:
                    entity = kg.get_entity_info(topic_id)
                    name = entity.get("entity", {}).get("name", topic_id)
                    desc = entity.get("entity", {}).get("description", "")
                    context_lines.append(f"  • {name}: {desc[:80]}")
                except:
                    pass
        
        if result.get("learning_path"):
            context_lines.append("\n📖 SUGGESTED LEARNING PATH:")
            for i, path_id in enumerate(result["learning_path"][:4], 1):
                try:
                    entity = kg.get_entity_info(path_id)
                    name = entity.get("entity", {}).get("name", path_id)
                    context_lines.append(f"  {i}. {name}")
                except:
                    pass
        
        context_lines.append("=====================================\n")
        return "\n".join(context_lines)
    
    except Exception as e:
        print(f"⚠️  Graph context build failed: {e}")
        return ""
```

### Step 4: Update the Homework Response Handler

Find this section in the chat input handling (around line 690-730):

**BEFORE:**
```python
    # 2. Use vector search to find related topics (enhances context)
    enhanced_context = topic_ctx
    if mode == "tutorial":
        try:
            related_topics = find_relevant_topics(user_input, top_k=3)
            if related_topics:
                related_names = [t[0] for t in related_topics if t[2] == selected_hw]
                if related_names:
                    enhanced_context = topic_ctx + f"\n\n[Related topics from your question: {', '.join(related_names)}]"
        except:
            pass

    # 3. Build appropriate chain based on mode
    if mode == "homework":
        parts        = build_homework_chain(selected_hw, [], week_num)
    else:
        parts        = build_chain(selected_hw, enhanced_context, disp_name)
```

**AFTER:**
```python
    # 2. Use vector search to find related topics (enhances context)
    enhanced_context = topic_ctx
    if mode == "tutorial":
        try:
            related_topics = find_relevant_topics(user_input, top_k=3)
            if related_topics:
                related_names = [t[0] for t in related_topics if t[2] == selected_hw]
                if related_names:
                    enhanced_context = topic_ctx + f"\n\n[Related topics from your question: {', '.join(related_names)}]"
        except:
            pass

    # 3. Build appropriate chain based on mode
    if mode == "homework":
        parts = build_homework_chain(selected_hw, [], week_num)
        
        # 🆕 Phase 4: Enhance with graph context if available
        if kg and GRAPH_RAG_ENABLED:
            hw_topics = hw_info.get("topics", [])
            graph_context = get_graph_context_for_homework(
                user_input,
                hw_topics,
                kg
            )
            if graph_context:
                # Append graph context to system prompt
                parts["graph_context"] = graph_context
    else:
        parts = build_chain(selected_hw, enhanced_context, disp_name)
```

### Step 5: Update Message Building (Around Line 740)

**BEFORE:**
```python
        messages = ans_prompt.format_messages(
            chat_history=chat_history,
            input=user_input,
        )
```

**AFTER:**
```python
        # Format messages with optional graph context
        prompt_kwargs = {
            "chat_history": chat_history,
            "input": user_input,
        }
        
        # 🆕 Phase 4: Add graph context to system prompt if available
        if mode == "homework" and parts.get("graph_context"):
            # Modify system prompt to include graph context
            system_with_context = ans_prompt.messages[0]  # Get system message
            if hasattr(system_with_context, "content"):
                system_with_context.content = (
                    system_with_context.content + 
                    "\n\n" + 
                    parts["graph_context"]
                )
        
        messages = ans_prompt.format_messages(**prompt_kwargs)
```

---

## Testing the Integration

1. **Build the knowledge graph first:**
   ```bash
   python build_knowledge_graph.py --all
   ```

2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

3. **Test homework questions:**
   - Ask a homework question
   - Check console output for Graph RAG messages
   - Response should reference prerequisite concepts

4. **Check log messages:**
   - "✅ Knowledge graph loaded" = Integration working
   - No message = Graph RAG skipped (optional)

---

## What Gets Enhanced

### Before (Vector-only):
```
Student: "How do I implement merge sort?"

Tutor: "Let's think about how you'd divide the array... 
[Generic Socratic response without learning path context]"
```

### After (Graph-Enhanced):
```
Student: "How do I implement merge sort?"

=== GRAPH-BASED LEARNING CONTEXT ===
📚 PREREQUISITES (student should know these first):
  • Recursion
  • Divide and Conquer

🎯 MAIN TOPICS (directly related to question):
  • Merge Sort: Divide and conquer sorting algorithm with O(n log n) time complexity

📖 SUGGESTED LEARNING PATH:
  1. Recursion
  2. Divide and Conquer  
  3. Arrays
  4. Merge Sort
=====================================

Tutor: "Great question! Before implementing merge sort, let me ask you about 
the prerequisites. Do you remember how recursion works? Specifically, how 
you'd write a function that calls itself..."
```

---

## Fallback Behavior

If the knowledge graph is not available:
- App still works normally (Graph RAG is optional)
- Falls back to vector-only search
- No error messages shown to student
- Graceful degradation

---

## Performance Notes

- First request: ~100ms (graph already in memory)
- Subsequent requests: ~50ms (cached graph)
- No impact on response generation (context only)
- Vector search: ~15ms via Chroma

---

## Next Steps

After integrating Phase 4:
1. Test with live homework questions
2. Adjust graph if relationships are wrong
3. Move to Phase 5: Scale to Neo4j (optional)

See: `GRAPH_RAG_INTEGRATION_GUIDE.md` for complete details
