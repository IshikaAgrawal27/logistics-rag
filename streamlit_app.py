"""
streamlit_app.py - Streamlit frontend for Logistics RAG System
Run: streamlit run streamlit_app.py
Requires the FastAPI backend running at http://localhost:8000
"""
import streamlit as st
import requests
import time
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Logistics RAG Assistant",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# THEME TOGGLE
# ─────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []


def get_css(dark: bool) -> str:
    if dark:
        bg       = "#0f1117"
        surface  = "#1a1d27"
        surface2 = "#222537"
        border   = "#2e3148"
        text     = "#e8eaf0"
        subtext  = "#8b8fa8"
        accent   = "#5b7cf6"
        accent2  = "#7c9fff"
        success  = "#2ecc71"
        warning  = "#f39c12"
        danger   = "#e74c3c"
        user_bg  = "#1e2a4a"
        bot_bg   = "#1a1d27"
        input_bg = "#1a1d27"
        tag_bg   = "#2a2f4a"
    else:
        bg       = "#f5f6fa"
        surface  = "#ffffff"
        surface2 = "#eef0f8"
        border   = "#dde1f0"
        text     = "#1a1d2e"
        subtext  = "#6b7094"
        accent   = "#4361ee"
        accent2  = "#3a56d4"
        success  = "#27ae60"
        warning  = "#e67e22"
        danger   = "#c0392b"
        user_bg  = "#dde8ff"
        bot_bg   = "#ffffff"
        input_bg = "#ffffff"
        tag_bg   = "#e8ecff"

    return f"""
<style>
/* ── Global ── */
.stApp {{
    background-color: {bg};
    color: {text};
    font-family: 'Inter', -apple-system, sans-serif;
}}
section[data-testid="stSidebar"] {{
    background-color: {surface};
    border-right: 1px solid {border};
}}
section[data-testid="stSidebar"] * {{ color: {text}; }}

/* ── Headers ── */
h1, h2, h3 {{ color: {text}; font-weight: 700; }}

/* ── Buttons ── */
.stButton > button {{
    background: {accent};
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    transition: all 0.2s;
    width: 100%;
}}
.stButton > button:hover {{
    background: {accent2};
    transform: translateY(-1px);
    box-shadow: 0 4px 12px {accent}55;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {surface2};
    border: 2px dashed {border};
    border-radius: 12px;
    padding: 1rem;
    transition: border-color 0.2s;
}}
[data-testid="stFileUploader"]:hover {{ border-color: {accent}; }}

/* ── Chat messages ── */
.chat-wrapper {{ display: flex; flex-direction: column; gap: 1rem; padding: 0.5rem 0; }}

.user-msg {{
    background: {user_bg};
    border-radius: 16px 16px 4px 16px;
    padding: 0.85rem 1.1rem;
    max-width: 80%;
    align-self: flex-end;
    border: 1px solid {border};
    color: {text};
    font-size: 0.95rem;
    line-height: 1.5;
}}
.bot-msg {{
    background: {bot_bg};
    border-radius: 16px 16px 16px 4px;
    padding: 0.85rem 1.1rem;
    max-width: 85%;
    align-self: flex-start;
    border: 1px solid {border};
    color: {text};
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}
.msg-meta {{
    font-size: 0.72rem;
    color: {subtext};
    margin-top: 0.3rem;
}}
.msg-label {{
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: {subtext};
    margin-bottom: 0.3rem;
}}

/* ── Source chips ── */
.sources-box {{
    margin-top: 0.6rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}}
.source-chip {{
    background: {tag_bg};
    border: 1px solid {border};
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.73rem;
    color: {accent};
    font-weight: 500;
}}

/* ── Doc list items ── */
.doc-item {{
    background: {surface2};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 0.55rem 0.8rem;
    margin: 0.3rem 0;
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}}

/* ── Status badges ── */
.badge-ok  {{ background:#1a3a2a; color:{success}; border-radius:6px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}
.badge-err {{ background:#3a1a1a; color:{danger};  border-radius:6px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}
.badge-warn {{ background:#3a2e1a; color:{warning}; border-radius:6px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}

/* ── Dividers ── */
hr {{ border-color: {border}; }}

/* ── Input ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {input_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {accent};
    box-shadow: 0 0 0 2px {accent}33;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background: {surface2};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 0.7rem 1rem;
}}
[data-testid="stMetricValue"] {{ color: {accent}; font-weight: 700; }}
[data-testid="stMetricLabel"] {{ color: {subtext}; }}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: {surface2};
    border-radius: 8px;
    color: {text};
}}

/* ── Scrollable chat area ── */
.chat-container {{
    max-height: 520px;
    overflow-y: auto;
    padding-right: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: {border} transparent;
}}

/* ── Empty state ── */
.empty-state {{
    text-align: center;
    padding: 3rem 1rem;
    color: {subtext};
}}
.empty-state .icon {{ font-size: 3rem; margin-bottom: 1rem; }}
.empty-state p {{ font-size: 0.95rem; }}

/* ── Logo / Brand ── */
.brand {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.5rem;
}}
.brand-icon {{ font-size: 2rem; }}
.brand-name {{
    font-size: 1.25rem;
    font-weight: 800;
    color: {accent};
    letter-spacing: -0.02em;
}}
.brand-sub {{ font-size: 0.72rem; color: {subtext}; text-transform: uppercase; letter-spacing: 0.08em; }}

/* ── Toggle button ── */
.theme-btn > button {{
    background: {surface2} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
    border-radius: 20px !important;
    padding: 0.3rem 1rem !important;
    font-size: 0.8rem !important;
    width: auto !important;
}}
</style>
"""


# ─────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────
def api_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def api_documents():
    try:
        r = requests.get(f"{API_BASE}/documents", timeout=5)
        return r.json().get("documents", []) if r.status_code == 200 else []
    except Exception:
        return []


def api_upload(files):
    try:
        file_tuples = [("files", (f.name, f.getvalue(), "application/pdf")) for f in files]
        r = requests.post(f"{API_BASE}/upload", files=file_tuples, timeout=120)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Cannot connect to backend. Is the FastAPI server running?"}
    except Exception as e:
        return 500, {"detail": str(e)}


def api_chat(question: str):
    try:
        r = requests.post(
            f"{API_BASE}/chat",
            json={"question": question, "include_sources": True},
            timeout=60
        )
        if r.status_code == 200:
            return r.json()
        else:
            detail = r.json().get("detail", "Unknown error")
            return {"answer": f"Error: {detail}", "sources": []}
    except requests.exceptions.ConnectionError:
        return {"answer": "Cannot connect to backend. Is the FastAPI server running?", "sources": []}
    except Exception as e:
        return {"answer": f"Request failed: {str(e)}", "sources": []}


def api_delete(filename: str):
    try:
        r = requests.delete(f"{API_BASE}/documents/{filename}", timeout=60)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}


# ─────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────
st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="brand">
        <span class="brand-icon">🚚</span>
        <div>
            <div class="brand-name">LogiRAG</div>
            <div class="brand-sub">Logistics Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Theme toggle
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        moon = "🌙 Dark" if not st.session_state.dark_mode else "🌙 Dark ✓"
        if st.button(moon, key="dark_btn"):
            st.session_state.dark_mode = True
            st.rerun()
    with col_t2:
        sun = "☀️ Light ✓" if not st.session_state.dark_mode else "☀️ Light"
        if st.button(sun, key="light_btn"):
            st.session_state.dark_mode = False
            st.rerun()

    st.markdown("---")

    # Backend status
    health = api_health()
    if health:
        vs_ready = health.get("vectorstore_initialized", False)
        st.markdown(
            f'<span class="badge-ok">● Backend Online</span>&nbsp;'
            f'<span class="{"badge-ok" if vs_ready else "badge-warn"}">'
            f'{"● Docs Ready" if vs_ready else "⚠ No Docs"}</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<span class="badge-err">● Backend Offline</span>', unsafe_allow_html=True)
        st.warning("Start the FastAPI server:\n```\nuvicorn app:app --reload\n```")

    st.markdown("---")

    # Upload section
    st.markdown("### 📤 Upload Documents")
    st.caption("Only logistics/transport PDFs are accepted. Multiple files supported.")

    uploaded_files = st.file_uploader(
        "Drop PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.caption(f"{len(uploaded_files)} file(s) selected")
        if st.button("🔄 Process & Ingest", key="ingest_btn"):
            with st.spinner("Classifying and ingesting documents…"):
                status_code, result = api_upload(uploaded_files)

            if status_code == 200:
                accepted = result.get("files_processed", [])
                rejected = result.get("files_rejected", [])

                if accepted:
                    for f in accepted:
                        st.success(f"✓ {f['filename']} ({f['chunks']} chunks)")
                if rejected:
                    for f in rejected:
                        st.error(f"✗ {f['filename']}: {f['reason']}")
                st.rerun()
            elif status_code == 422:
                detail = result.get("detail", {})
                st.error("All files rejected — not logistics documents.")
                for f in detail.get("rejected", []):
                    st.caption(f"✗ {f['filename']}: {f['reason']}")
            elif status_code == 503:
                st.error(result.get("detail", "Backend unavailable"))
            else:
                st.error(f"Upload failed ({status_code})")

    st.markdown("---")

    # Document list
    st.markdown("### 📂 Loaded Documents")
    docs = api_documents()
    if docs:
        for doc in docs:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(
                    f'<div class="doc-item">📄 {doc["filename"]}'
                    f'<span style="margin-left:auto;font-size:0.7rem;color:#888">'
                    f'{doc["size_kb"]} KB</span></div>',
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("🗑", key=f"del_{doc['filename']}", help="Delete"):
                    status_code, result = api_delete(doc["filename"])
                    if status_code == 200:
                        st.success("Deleted")
                        st.rerun()
                    else:
                        st.error("Delete failed")
    else:
        st.caption("No documents loaded yet.")

    st.markdown("---")

    # Clear chat
    if st.button("🗑 Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

    # Stats
    if st.session_state.chat_history:
        st.metric("Messages", len(st.session_state.chat_history))


# ── MAIN AREA ──
st.markdown("## 💬 Ask your Logistics Documents")
st.caption("Powered by Gemini · Answers grounded in your uploaded PDFs only")
st.markdown("---")

# Chat history display
chat_html = '<div class="chat-container"><div class="chat-wrapper">'

if not st.session_state.chat_history:
    chat_html += """
    <div class="empty-state">
        <div class="icon">🗂️</div>
        <p><strong>No conversation yet.</strong><br/>
        Upload a logistics PDF from the sidebar, then ask a question below.</p>
    </div>"""
else:
    for msg in st.session_state.chat_history:
        ts = msg.get("time", "")
        if msg["role"] == "user":
            chat_html += f"""
            <div>
                <div class="msg-label">You</div>
                <div class="user-msg">{msg["content"]}</div>
                <div class="msg-meta">{ts}</div>
            </div>"""
        else:
            content_escaped = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            sources_html = ""
            if msg.get("sources"):
                chips = "".join(
                    f'<span class="source-chip">📄 {s["filename"]} p.{s["page"]}</span>'
                    for s in msg["sources"]
                )
                sources_html = f'<div class="sources-box">{chips}</div>'
            chat_html += f"""
            <div>
                <div class="msg-label">🤖 LogiRAG</div>
                <div class="bot-msg">{content_escaped}{sources_html}</div>
                <div class="msg-meta">{ts}</div>
            </div>"""

chat_html += "</div></div>"
st.markdown(chat_html, unsafe_allow_html=True)

# Input area
st.markdown("---")
col_input, col_send = st.columns([5, 1])

with col_input:
    question = st.text_input(
        "Your question",
        placeholder="e.g. What is the estimated delivery time for shipment #12345?",
        label_visibility="collapsed",
        key="question_input"
    )

with col_send:
    send = st.button("Send ➤", key="send_btn")

# Handle send
if send and question.strip():
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": question.strip(),
        "time": datetime.now().strftime("%H:%M")
    })

    # Get answer
    with st.spinner("Searching documents…"):
        result = api_chat(question.strip())

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result.get("answer", "No answer returned."),
        "sources": result.get("sources", []),
        "time": datetime.now().strftime("%H:%M")
    })
    st.rerun()
elif send and not question.strip():
    st.warning("Please enter a question.")
