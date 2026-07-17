"""
app.py  —  Socratic Course Tutor
Run:  streamlit run app.py  ->  http://localhost:8501
"""
import json, os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

# Vector DB integration
from search_integration import init_search, find_relevant_topics, get_search_method

# Prompt templates from /prompts directory
from prompts.prompt_builder import build_tutorial_prompt, build_homework_prompt

# Socratic guidance with curriculum references + Hebrew support
from socratic_guidance import (
    validate_homework_query, 
    generate_curriculum_reference,
    get_text,
    format_current_problem,
    load_curriculum,
)

load_dotenv()

PROVIDER  = os.getenv("LLM_PROVIDER", "openai").lower()
# Use script-relative path so the app works regardless of launch CWD
_HERE     = Path(__file__).parent
DB_DIR    = _HERE / "db"
META_FILE = DB_DIR / "metadata.json"
# Also switch CWD so relative paths in other places work consistently
os.chdir(_HERE)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG + CSS
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Course Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Strip Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer { display:none !important; }
.block-container { padding-top:1.2rem !important; padding-bottom:0 !important; }

/* App background */
.stApp { background:#f0f4f8; }
.main .block-container { max-width:820px; }

/* Sidebar: dark admin panel */
[data-testid="stSidebar"] { background:#0f172a !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stCaption { color:#94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color:#f1f5f9 !important; }
[data-testid="stSidebar"] .stTextInput>div>div>input,
[data-testid="stSidebar"] .stTextArea>div>div>textarea {
    background:#1e293b !important;
    border:1px solid #334155 !important;
    color:#e2e8f0 !important;
    border-radius:8px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background:#1e293b !important;
    border:1px solid #334155 !important;
    border-radius:10px !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background:white !important;
    border-radius:14px !important;
    margin-bottom:6px !important;
    box-shadow:0 1px 4px rgba(0,0,0,.06) !important;
    border:1px solid #e8ecf1 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background:#eff6ff !important;
    border-color:#bfdbfe !important;
}
/* Force dark readable text everywhere in the main area */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] .stMarkdown { color:#0f172a !important; }
.main p, .main li, .main span, .main h1, .main h2, .main h3 { color:#0f172a !important; }
/* Inline code blocks — light background so they don't appear as black boxes */
[data-testid="stChatMessage"] code {
    color: #c7254e !important;
    background: #f9f2f4 !important;
    padding: 1px 5px !important;
    border-radius: 3px !important;
    font-size: 0.875em !important;
}
/* KaTeX math containers */
[data-testid="stChatMessage"] .katex,
[data-testid="stChatMessage"] .katex * { color:#0f172a !important; background:transparent !important; }
/* Alert/info/success boxes inside chat */
[data-testid="stChatMessage"] [data-testid="stAlert"] p { color:#0f172a !important; }

/* Chat input */
[data-testid="stChatInputContainer"]>div {
    background:white !important;
    border-radius:14px !important;
    border:1px solid #cbd5e1 !important;
    box-shadow:0 2px 8px rgba(0,0,0,.07) !important;
}

/* Selectbox pill */
.stSelectbox>div>div>div { border-radius:10px !important; font-weight:600; }

/* Divider */
hr { border-color:#e2e8f0 !important; margin:0.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def load_meta() -> dict:
    return json.loads(META_FILE.read_text(encoding="utf-8")) if META_FILE.exists() else {}

def save_meta(meta: dict) -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

def load_homework() -> dict:
    """Load homework database from homework.json"""
    hw_file = DB_DIR / "homework.json"
    return json.loads(hw_file.read_text(encoding="utf-8")) if hw_file.exists() else {}

def get_hw_list() -> list:
    """Only return items that exist in metadata (keeps stale DB dirs invisible)."""
    meta = load_meta()
    if not DB_DIR.exists() or not meta:
        return []
    return sorted(
        name for name in meta
        if (DB_DIR / name).is_dir()
    )

def get_homework_list() -> list:
    """Return list of homework assignments"""
    hw = load_homework()
    return sorted(hw.keys())

def api_key_ok() -> bool:
    return (
        os.getenv("OPENAI_API_KEY", "").startswith("sk-")
        or os.getenv("GITHUB_TOKEN", "").startswith("github_pat_")
        or os.getenv("GITHUB_TOKEN", "").startswith("ghp_")
    )

# ── Smart history trimming ────────────────────────────────────────────────────
# Keep last 6 exchanges verbatim (12 messages) so the Socratic thread stays
# coherent. Older exchanges are condensed into a compact breadcrumb that
# preserves BOTH the student's questions AND the key points of the tutor's
# responses — so the tutor can reference or briefly re-explain past concepts
# if the student asks, without repeating full first-time explanations.

MAX_VERBATIM_EXCHANGES = 6  # last N full exchanges kept verbatim

def trimmed_history(full: list) -> list:
    max_msgs = MAX_VERBATIM_EXCHANGES * 2
    if len(full) <= max_msgs:
        return full                     # short session — send everything as-is

    recent = full[-max_msgs:]           # last N exchanges: full detail
    older  = full[:-max_msgs]           # earlier exchanges: condensed

    # Pair up [HumanMessage, AIMessage] from the older section and capture
    # both the question AND the first meaningful sentence of the tutor's hint,
    # so the model can reference or briefly re-explain those concepts if asked.
    condensed_lines = []
    for i in range(0, len(older) - 1, 2):
        if i + 1 >= len(older):
            break
        q = older[i].content[:70].replace("\n", " ").rstrip(".,;")
        a = older[i + 1].content[:120].replace("\n", " ").rstrip(".,;")
        condensed_lines.append(f"• Student asked: \"{q}…\"  →  Tutor hinted: \"{a}…\"")

    breadcrumb_text = "\n".join(condensed_lines)

    breadcrumb = [
        HumanMessage(
            content=(
                "[Earlier in this session we covered:\n"
                + breadcrumb_text
                + "\nIf I ask about any of these again, give a brief reminder "
                "rather than a full first-time explanation.]"
            )
        ),
        AIMessage(
            content=(
                "[Understood. I remember what we covered. I can re-explain or "
                "build on any of those concepts concisely if you need it.]"
            )
        ),
    ]
    return breadcrumb + recent

def save_env_var(key: str, value: str) -> None:
    env_path = Path(".env")
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    found = False
    for i, ln in enumerate(lines):
        if ln.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ[key] = value

# ─────────────────────────────────────────────────────────────────────────────
# LLM HELPER
# ─────────────────────────────────────────────────────────────────────────────

def get_llm():
    if PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_LLM_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )
    from langchain_openai import ChatOpenAI
    # GitHub Models: OpenAI-compatible endpoint — uses your Copilot subscription
    gh_token = os.getenv("GITHUB_TOKEN", "")
    if gh_token:
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=gh_token,
            base_url="https://models.inference.ai.azure.com",
            temperature=0,
            streaming=True,
        )
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

@st.cache_resource
def build_chain(hw_id: str, topic_context: str, disp_name: str = "") -> dict:
    """Builds LangChain pipeline using prompts from /prompts directory and metadata.json"""
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    llm = get_llm()

    # Load topic list from metadata for curriculum boundary enforcement
    _meta_now = json.loads(META_FILE.read_text(encoding="utf-8"))
    topic_list = _meta_now.get(hw_id, {}).get("topics", [])
    
    # Initialize vector DB for semantic search
    try:
        init_search(str(DB_DIR))
    except:
        pass  # Vector DB optional; falls back to keyword search
    
    if topic_list:
        topics_formatted = "\n".join(f"  • {t}" for t in topic_list)
    else:
        topics_formatted = "  (foundational concepts)"

    tutorial_label = disp_name or hw_id.replace("_", " ").title()

    # Build system prompt from /prompts/tutorial_prompt.json
    sys_msg = build_tutorial_prompt(
        topics_list=topics_formatted,
        tutorial_label=tutorial_label,
        topic_context=topic_context
    )

    # Build the prompt template
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", sys_msg),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    return {
        "llm": llm,
        "answer_prompt": answer_prompt,
    }

@st.cache_resource
def build_homework_chain(hw_key: str, topics_covered: list, week_num: int) -> dict:
    """Builds LangChain pipeline for homework problem-solving using /prompts directory (Socratic method)"""
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    llm = get_llm()
    hw_data = load_homework().get(hw_key, {})
    
    # Build topics known so far (cumulative: all weeks up to this week)
    all_hw = load_homework()
    known_concepts = []
    for k, v in all_hw.items():
        if v.get("week", 0) <= week_num:
            known_concepts.extend(v.get("topics", []))
    known_concepts = sorted(set(known_concepts))
    
    concepts_str = "\n".join(f"  • {c}" for c in known_concepts) if known_concepts else "  (foundational concepts)"
    
    hw_title = hw_data.get("title", f"Homework {week_num}")
    hw_description = hw_data.get("description", "")
    key_concepts_list = hw_data.get("key_concepts", [])
    key_concepts = "\n".join(f"  • {c}" for c in key_concepts_list)
    
    # Build system prompt from /prompts/homework_prompt.json
    sys_msg = build_homework_prompt(
        concepts_list=concepts_str,
        hw_title=hw_title,
        hw_description=hw_description,
        key_concepts=key_concepts
    )
    
    # Build the prompt template
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", sys_msg),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    return {
        "llm": llm,
        "answer_prompt": answer_prompt,
        "hw_data": hw_data,
    }

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE SUPPORT  —  Initialize language state
# ─────────────────────────────────────────────────────────────────────────────

# Initialize language in session state
if "language" not in st.session_state:
    st.session_state.language = "en"

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  —  dark admin panel (teacher only)
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()

    # Language selector
    lang_choice = st.radio(
        "Language / שפה",
        options=["English", "עברית"],
        index=0 if st.session_state.language == "en" else 1,
        key="lang_selector"
    )
    st.session_state.language = "en" if lang_choice == "English" else "he"
    st.divider()

    with st.expander("🔑 API Key", expanded=not api_key_ok()):
        if api_key_ok():
            src = "GitHub Copilot" if os.getenv("GITHUB_TOKEN") else "OpenAI"
            st.success(f"{src} key saved ✅")

        st.markdown("**Option A — GitHub Copilot** *(recommended — you already pay for it)*")
        st.caption(
            "Get a free PAT at [github.com/settings/tokens](https://github.com/settings/tokens) "
            "→ *Generate new token (classic)* → no scopes needed → copy."
        )
        gh_input = st.text_input(
            "GitHub PAT", type="password",
            placeholder="github_pat_... or ghp_...",
            label_visibility="collapsed",
        )
        if st.button("Save GitHub token", use_container_width=True):
            if gh_input.startswith(("github_pat_", "ghp_")):
                save_env_var("GITHUB_TOKEN", gh_input)
                save_env_var("OPENAI_API_KEY", "")   # clear OpenAI key
                build_chain.clear()
                st.success("GitHub token saved! Uses gpt-4o-mini via Copilot.")
                st.rerun()
            else:
                st.error("Must start with github_pat_ or ghp_")

        st.divider()
        st.markdown("**Option B — OpenAI key** *(pay-per-use, needs credits)*")
        oi = st.text_input(
            "OpenAI key", type="password",
            placeholder="sk-proj-...",
            label_visibility="collapsed",
        )
        if st.button("Save OpenAI key", use_container_width=True):
            if oi.startswith("sk-"):
                save_env_var("OPENAI_API_KEY", oi)
                save_env_var("GITHUB_TOKEN", "")   # clear GH token
                build_chain.clear()
                st.success("OpenAI key saved!")
                st.rerun()
            else:
                st.error("Must start with sk-")

    st.divider()
    active = "GitHub Copilot" if os.getenv("GITHUB_TOKEN") else PROVIDER.upper()
    st.caption(f"LLM: **{active}**")
    if not api_key_ok():
        st.warning("Chat needs an API key.")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN  —  student chat interface
# ─────────────────────────────────────────────────────────────────────────────

meta    = load_meta()
hw_list = get_hw_list()
homework_list = get_homework_list()

# ── Nothing loaded yet ────────────────────────────────────────────────────────
if not hw_list and not homework_list:
    st.markdown(
        "<div style=\"text-align:center;padding:80px 0;color:#64748b\">"
        "<div style=\"font-size:4rem\">🎓</div>"
        "<h2 style=\"color:#1e293b;margin:12px 0 8px\">Course Tutor</h2>"
        "<p style=\"font-size:1rem\">No tutorials or homework loaded.<br>"
        "Please ensure metadata.json and homework.json are populated in the db/ folder.</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ── Mode selector: Tutorial vs Homework ───────────────────────────────────────
col_mode_1, col_mode_2 = st.columns(2)
with col_mode_1:
    mode_tabs = st.radio(
        "Select mode:",
        options=["📖 Learn Material", "💪 Solve Homework"],
        horizontal=True,
        key="mode_selector",
    )

mode = "homework" if "Homework" in mode_tabs else "tutorial"

# ────────────────────────────────────────────────────────────────────────────────
# TUTORIAL MODE
# ────────────────────────────────────────────────────────────────────────────────

if mode == "tutorial":
    if not hw_list:
        st.warning("No tutorials loaded yet. Add tutorial PDFs to metadata.json")
        st.stop()
    
    # ── HW selector bar ───────────────────────────────────────────────────────────
    hw_labels = {hw: meta.get(hw, {}).get("display_name", hw) for hw in hw_list}

    col_sel, col_clr = st.columns([5, 1])
    with col_sel:
        selected_hw = st.selectbox(
            "hw",
            options=hw_list,
            format_func=lambda hw: "📚  " + hw_labels[hw],
            label_visibility="collapsed",
            key="hw_selector",
        )
    with col_clr:
        if st.button("🗑 Clear", use_container_width=True, help="Clear conversation"):
            st.session_state.chat_history     = []
            st.session_state.display_messages = []
            st.rerun()

    hw_info   = meta.get(selected_hw, {})
    topic_ctx = hw_info.get("topic_context", "")
    disp_name = hw_info.get("display_name", selected_hw)

    # Reset on HW switch
    if st.session_state.get("active_hw") != selected_hw:
        st.session_state.active_hw        = selected_hw
        st.session_state.active_mode      = "tutorial"
        st.session_state.chat_history     = []
        st.session_state.display_messages = []

# ────────────────────────────────────────────────────────────────────────────────
# HOMEWORK MODE
# ────────────────────────────────────────────────────────────────────────────────

elif mode == "homework":
    if not homework_list:
        st.warning("No homework assignments loaded yet. Add homework.json to db/")
        st.stop()
    
    # ── Homework selector bar ─────────────────────────────────────────────────────
    homework_data = load_homework()
    hw_labels_hw = {k: f"Week {homework_data[k].get('week', '?')}: {homework_data[k].get('title', k)}" 
                    for k in homework_list}

    col_sel, col_clr = st.columns([5, 1])
    with col_sel:
        selected_hw = st.selectbox(
            "hw",
            options=homework_list,
            format_func=lambda hw: "💪  " + hw_labels_hw.get(hw, hw),
            label_visibility="collapsed",
            key="hw_selector_hw",
        )
    with col_clr:
        if st.button("🗑 Clear", use_container_width=True, help="Clear conversation"):
            st.session_state.chat_history     = []
            st.session_state.display_messages = []
            st.rerun()

    hw_info = homework_data.get(selected_hw, {})
    disp_name = hw_info.get("title", selected_hw)
    week_num = hw_info.get("week", 1)
    
    # Reset on HW switch
    if st.session_state.get("active_hw") != selected_hw or st.session_state.get("active_mode") != "homework":
        st.session_state.active_hw        = selected_hw
        st.session_state.active_mode      = "homework"
        st.session_state.chat_history     = []
        st.session_state.display_messages = []
    
    # Use homework-specific chain
    topic_ctx = ""  # Not used in homework mode
    
    # ──────────────────────────────────────────────────────────────────────────
    # HOMEWORK MODE: Create two-column layout with problem on left, chat on right
    # ──────────────────────────────────────────────────────────────────────────
    col_prob, col_chat = st.columns([1, 2.5], gap="large")
    
    with col_prob:
        st.markdown(f"### 📝 {disp_name}")
        st.markdown("---")
        
        # Show problem details
        st.markdown(f"**Description:**\n{hw_info.get('description', 'N/A')}")
        st.markdown(f"**Problems:** {hw_info.get('problems', '?')}")
        st.markdown(f"**Topics:** {', '.join(hw_info.get('topics', []))}")
        
        # Show preview of first problem
        if hw_info.get("problem_preview"):
            st.markdown("**Problem Preview:**")
            preview_text = hw_info['problem_preview'][:400]
            st.code(preview_text + ("..." if len(preview_text) > 400 else ""), language="text")
        
        st.markdown("---")
        st.info(
            f"💡 **Focus:** Answer questions about THIS homework only.\n\n"
            f"I will guide you using Socratic questions—not give answers directly."
        )
    
    # Save problem info for scope validation later
    st.session_state.current_hw_key = selected_hw
    st.session_state.current_hw_info = hw_info

else:
    col_prob = None
    col_chat = st

st.divider()

# ── Welcome screen (empty chat) ───────────────────────────────────────────────
if not st.session_state.get("display_messages"):
    lang = st.session_state.language
    welcome_msg = get_text("welcome_tutor", lang)
    if mode == "homework":
        welcome_msg = get_text("welcome_hw", lang) + f"\n\n**{disp_name}**"
    
    st.markdown(
        f"<div style=\"text-align:center;padding:32px 0 20px;color:#475569\">"
        f"<div style=\"font-size:3rem\">{'💪' if mode == 'homework' else '🎓'}</div>"
        f"<h3 style=\"color:#1e293b;margin:10px 0 6px\">{disp_name}</h3>"
        f"<p style=\"margin:0 auto;max-width:480px;line-height:1.6\">"
        f"{welcome_msg}<br>"
        "<b>Ask your first question below.</b>"
        "</p></div>",
        unsafe_allow_html=True,
    )

# ── Render conversation ───────────────────────────────────────────────────────
for msg in st.session_state.get("display_messages", []):
    avatar = "🧑‍🎓" if msg["role"] == "user" else "🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── No API key guard ──────────────────────────────────────────────────────────
if not api_key_ok() and PROVIDER == "openai":
    st.chat_input("Open the sidebar to add your API key…", disabled=True)
    st.info("👈 Open the sidebar (top-left ▸) and add your OpenAI API key to start chatting.")
    st.stop()

# ── Chat input + streaming response ──────────────────────────────────────────
lang = st.session_state.language
placeholder = get_text("ask_question", lang) if mode == "homework" else f"Ask about {disp_name}…"
if user_input := st.chat_input(placeholder):

    # 🔒 HOMEWORK MODE: Validate scope before processing
    if mode == "homework":
        all_homework = load_homework()
        is_valid, error_msg = validate_homework_query(user_input, selected_hw, all_homework)
        
        if not is_valid:
            # Show error message in chat
            with st.chat_message("assistant", avatar="🎓"):
                st.warning(f"⚠️ {error_msg}")
                st.markdown(f"**Let's focus on {disp_name} instead.** What would you like to understand about it?")
            st.stop()

    # 1. Show user message IMMEDIATELY — before any processing
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_input)

    # 2. Use vector search to find related topics (enhances context)
    enhanced_context = topic_ctx
    if mode == "tutorial":
        try:
            related_topics = find_relevant_topics(user_input, top_k=3)
            if related_topics:
                related_names = [t[0] for t in related_topics if t[2] == selected_hw]  # Filter to current tutorial
                if related_names:
                    enhanced_context = topic_ctx + f"\n\n[Related topics from your question: {', '.join(related_names)}]"
        except:
            pass  # Vector search failed; use original context
    
    # 2b. HOMEWORK MODE: Inject curriculum-aware guidance
    elif mode == "homework":
        hw_data = all_homework.get(selected_hw, {})
        curriculum_ref = generate_curriculum_reference(user_input, hw_data.get("week", 1))
        # This will be displayed before the assistant response

    # 3. Build appropriate chain based on mode
    if mode == "homework":
        parts        = build_homework_chain(selected_hw, [], week_num)
    else:
        parts        = build_chain(selected_hw, enhanced_context, disp_name)
    
    llm          = parts["llm"]
    ans_prompt   = parts["answer_prompt"]
    chat_history = trimmed_history(st.session_state.get("chat_history", []))

    with st.chat_message("assistant", avatar="🎓"):
        # Show curriculum reference if homework mode
        if mode == "homework" and "curriculum_ref" in locals():
            st.markdown(curriculum_ref)
            st.divider()
        
        # Build messages and stream response
        messages = ans_prompt.format_messages(
            chat_history=chat_history,
            input=user_input,
        )
        try:
            # Stream token-by-token with cursor, then re-render with math fixed
            _slot  = st.empty()
            _buf   = ""
            for _chunk in llm.stream(messages):
                _buf += _chunk.content
                _slot.markdown(_buf + "\u258c")   # ▌ cursor while streaming
            # Final render: convert \( \) and \[ \] to $ and $$ for KaTeX
            import re as _re
            _fixed = _re.sub(r"\\\[(.+?)\\\]", r"$$\1$$", _buf, flags=_re.DOTALL)
            _fixed = _re.sub(r"\\\((.+?)\\\)",  r"$\1$",   _fixed, flags=_re.DOTALL)
            _slot.markdown(_fixed)
            answer = _fixed
        except Exception as exc:
            answer = f"⚠️ Error calling the model: {exc}"
            st.markdown(answer)

    # 5. Persist to session state, then force a clean re-render from history
    #    (prevents the "immediate render" coexisting with the history loop render)
    st.session_state.setdefault("chat_history", []).extend([
        HumanMessage(content=user_input),
        AIMessage(content=answer),
    ])
    st.session_state.setdefault("display_messages", []).extend([
        {"role": "user",      "content": user_input},
        {"role": "assistant", "content": answer},
    ])
    st.rerun()


