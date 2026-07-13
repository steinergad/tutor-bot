# 📋 Prompts & Policies

This folder contains all system prompts and policies used by the tutoring bot. Prompts are stored as **structured JSON** files with a Python builder module, making them:

- **Easy to modify** — No code changes needed, just edit the JSON
- **Consistent** — Ensures formatting rules are applied uniformly
- **Testable** — Can swap prompts for A/B testing or optimization
- **Auditable** — Clear record of what the bot is instructed to do

## 📁 Files

### `tutorial_prompt.json`
System prompt for **Learn Material mode** (Lecture-based learning)

- **Role**: Teacher guiding students through course material
- **Curriculum Boundary**: Students can only ask about topics they've learned
- **Teaching Style**: Clear explanations, examples, encouragement
- **Math Formatting**: KaTeX inline ($...$) and block ($$...$$)

**Usage**:
```python
from prompt_builder import build_tutorial_prompt

sys_msg = build_tutorial_prompt(
    topics_list="• Topic 1\n• Topic 2",
    tutorial_label="Tutorial 1 — Intro to Algorithm Analysis",
    topic_context="## Algorithms\n- Bubble Sort..."
)
```

### `homework_prompt.json`
System prompt for **Solve Homework mode** (Problem-solving with Socratic method)

- **Role**: Socratic tutor guiding students toward solutions
- **Core Principle**: Ask questions, don't give answers
- **DOs**: Guide step-by-step, ask "why?", celebrate progress
- **DON'Ts**: Never reveal answers or pseudocode
- **Math Formatting**: KaTeX inline and block

**Usage**:
```python
from prompt_builder import build_homework_prompt

sys_msg = build_homework_prompt(
    concepts_list="• Big O Notation\n• Recursion",
    hw_title="Homework 1 — Algorithm Complexity",
    hw_description="Analyze time complexity of sorting algorithms",
    key_concepts="• Asymptotic analysis\n• Comparison-based sorting"
)
```

### `prompt_builder.py`
Python module that loads and builds complete system prompts

**Functions**:
- `load_prompt_template(template_name)` — Load JSON template
- `build_tutorial_prompt(...)` — Build tutorial system prompt
- `build_homework_prompt(...)` — Build homework system prompt
- `get_prompt_metadata(template_name)` — Get template info

## 🔄 How It Works

1. **JSON Structure**: Each prompt template contains:
   - `system_message_template` with placeholders
   - Guidelines, rules, and formatting instructions
   - Reusable components (curriculum boundary, math formatting, etc.)

2. **Python Builder**: `prompt_builder.py` reads JSON and:
   - Substitutes placeholders with actual values
   - Ensures consistent formatting
   - Adds static guidelines

3. **In app.py**:
   ```python
   from prompts.prompt_builder import build_tutorial_prompt
   
   # OLD: Hardcoded string
   # sys_msg = "You are a teacher..."
   
   # NEW: Load from prompts/
   sys_msg = build_tutorial_prompt(topics_list, tutorial_label, topic_context)
   ```

## ✏️ Modifying Prompts

To change the tutorial teaching style:

1. Open `tutorial_prompt.json`
2. Edit `teaching_guidelines` or `curriculum_boundary` section
3. Save — no code changes needed!
4. Restart Streamlit app to reload prompts

Example: Add a new teaching guideline:
```json
"teaching_guidelines": [
  "Explain concepts clearly and help them learn.",
  "Use examples from the course material to illustrate points.",
  "Encourage understanding and thinking, not just memorization.",
  "Be patient, supportive, and encouraging.",
  "Reference previous concepts to build connections."  // NEW
]
```

## 🧪 Testing Prompts

To compare different prompt versions (A/B testing):

```python
from prompts.prompt_builder import build_tutorial_prompt
import copy

# Load base template
template = load_prompt_template("tutorial_prompt")

# Create variant A (strict boundary)
template_a = copy.deepcopy(template)
template_a["system_message_template"]["curriculum_boundary"]["out_of_scope"] = \
    "I can only help with topics we've covered."

# Create variant B (helpful boundary)
template_b = copy.deepcopy(template)
template_b["system_message_template"]["curriculum_boundary"]["out_of_scope"] = \
    "We haven't covered that yet, but here's how it relates to what we know..."

# Test both versions
```

## 📊 Prompt Metrics to Track

When optimizing prompts, track these metrics:

- **Accuracy**: Does bot stay within curriculum?
- **Helpfulness**: Do students find responses useful?
- **Clarity**: Are explanations easy to understand?
- **Math Quality**: Are formulas rendered correctly?
- **Tone**: Does personality match teaching style?

## 🚀 Future Improvements

- [ ] Add `expert_prompt.json` for advanced/accelerated mode
- [ ] Add `debugging_prompt.json` for code/algorithm debugging
- [ ] Add `hint_generation.json` for progressive hint levels
- [ ] Create prompt versioning system (v1.0, v1.1, etc.)
- [ ] Add prompt performance metrics to Streamlit sidebar
- [ ] Implement prompt A/B testing framework
