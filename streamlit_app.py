"""
streamlit_app.py — Logistics RAG Assistant
Run: streamlit run streamlit_app.py
Requires FastAPI backend at http://localhost:8000
"""
import streamlit as st
import requests
from datetime import datetime

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="LogiRAG",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ──────────────────────────────────────────────────────────────
for k, v in {
    "dark_mode": True,
    "chat_history": [],
    "docs_ready": False,
    "ingest_log": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Theme ──────────────────────────────────────────────────────────────────────
def theme():
    if st.session_state.dark_mode:
        return dict(
            bg="#09090b", sidebar="#0f0f12", surface="#18181b",
            surface2="#27272a", border="#3f3f46", border2="#52525b",
            text="#fafafa", subtext="#a1a1aa", muted="#71717a",
            accent="#6366f1", accent_dim="#4338ca", accent_glow="#6366f133",
            user_bubble="#1e1b4b", bot_bubble="#18181b",
            success="#10b981", danger="#ef4444", warning="#f59e0b",
            success_bg="#052e16", danger_bg="#1f0a0a", warning_bg="#1c1207",
            input_bg="#18181b", scrollbar="#3f3f46",
        )
    else:
        return dict(
            bg="#fafafa", sidebar="#ffffff", surface="#ffffff",
            surface2="#f4f4f5", border="#e4e4e7", border2="#d4d4d8",
            text="#09090b", subtext="#52525b", muted="#71717a",
            accent="#4f46e5", accent_dim="#3730a3", accent_glow="#4f46e520",
            user_bubble="#eef2ff", bot_bubble="#ffffff",
            success="#059669", danger="#dc2626", warning="#d97706",
            success_bg="#ecfdf5", danger_bg="#fef2f2", warning_bg="#fffbeb",
            input_bg="#ffffff", scrollbar="#d4d4d8",
        )


def inject_css(t):
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
    background: {t['bg']} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: {t['text']} !important;
    font-size: 14px;
    line-height: 1.6;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {t['sidebar']} !important;
    border-right: 1px solid {t['border']} !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] > div {{
    padding: 0 !important;
}}
[data-testid="stSidebarContent"] {{
    padding: 1.5rem 1.25rem !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ── Main area padding ── */
.main .block-container {{
    padding: 2rem 2.5rem !important;
    max-width: 900px !important;
}}

/* ── Headings ── */
h1, h2, h3, h4 {{ color: {t['text']} !important; font-weight: 700 !important; letter-spacing: -0.02em; }}

/* ── All text in sidebar ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] small {{
    color: {t['text']} !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: {t['accent']} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.1rem !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
    cursor: pointer !important;
    font-family: 'Inter', sans-serif !important;
}}
.stButton > button:hover {{
    background: {t['accent_dim']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
}}

/* ── Ghost button variant ── */
.btn-ghost > button {{
    background: transparent !important;
    color: {t['subtext']} !important;
    border: 1px solid {t['border']} !important;
}}
.btn-ghost > button:hover {{
    background: {t['surface2']} !important;
    color: {t['text']} !important;
    border-color: {t['border2']} !important;
    box-shadow: none !important;
}}

/* ── Danger button ── */
.btn-danger > button {{
    background: transparent !important;
    color: {t['danger']} !important;
    border: 1px solid {t['danger']}44 !important;
    padding: 0.3rem 0.6rem !important;
    font-size: 0.75rem !important;
}}
.btn-danger > button:hover {{
    background: {t['danger_bg']} !important;
    box-shadow: none !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {t['surface']} !important;
    border: 1.5px dashed {t['border2']} !important;
    border-radius: 10px !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {t['accent']} !important;
}}
[data-testid="stFileUploaderDropzoneInput"] {{
    background: transparent !important;
}}

/* ── Text input ── */
.stTextInput > div > div > input {{
    background: {t['input_bg']} !important;
    color: {t['text']} !important;
    border: 1.5px solid {t['border']} !important;
    border-radius: 10px !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.15s !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{
    color: {t['muted']} !important;
}}
.stTextInput label {{ display: none !important; }}

/* ── Spinner ── */
.stSpinner > div {{
    border-top-color: {t['accent']} !important;
}}

/* ── Divider ── */
hr {{
    border: none !important;
    border-top: 1px solid {t['border']} !important;
    margin: 1rem 0 !important;
}}

/* ── Alert / info boxes ── */
[data-testid="stAlert"] {{
    border-radius: 8px !important;
    border: none !important;
    font-size: 0.82rem !important;
    padding: 0.6rem 0.9rem !important;
}}

/* ── Scrollbars ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {t['scrollbar']}; border-radius: 99px; }}

/* ── Custom components ── */
.sidebar-brand {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 1.5rem;
}}
.sidebar-brand-icon {{
    width: 32px; height: 32px;
    background: {t['accent']};
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}}
.sidebar-brand-text {{ line-height: 1.2; }}
.sidebar-brand-name {{
    font-size: 0.95rem; font-weight: 700;
    color: {t['text']}; letter-spacing: -0.01em;
}}
.sidebar-brand-sub {{
    font-size: 0.68rem; color: {t['muted']};
    text-transform: uppercase; letter-spacing: 0.07em;
}}

.section-label {{
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: {t['muted']};
    margin-bottom: 0.6rem; display: block;
}}

.status-dot {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.75rem; font-weight: 500;
    padding: 3px 9px; border-radius: 20px;
}}
.status-online  {{ background:{t['success_bg']}; color:{t['success']}; }}
.status-offline {{ background:{t['danger_bg']};  color:{t['danger']};  }}
.status-warn    {{ background:{t['warning_bg']}; color:{t['warning']}; }}

.doc-row {{
    display: flex; align-items: center; gap: 8px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 7px 10px;
    margin-bottom: 5px;
}}
.doc-row-icon {{ font-size: 13px; flex-shrink: 0; color: {t['accent']}; }}
.doc-row-name {{
    font-size: 0.78rem; font-weight: 500;
    color: {t['text']}; flex: 1; min-width: 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.doc-row-size {{
    font-size: 0.7rem; color: {t['muted']}; flex-shrink: 0;
}}

.theme-pill {{
    display: inline-flex; gap: 2px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 8px; padding: 3px;
}}
.theme-opt {{
    padding: 4px 12px; border-radius: 6px;
    font-size: 0.75rem; font-weight: 500;
    cursor: pointer; border: none;
    transition: all 0.15s; color: {t['muted']};
    background: transparent;
}}
.theme-opt.active {{
    background: {t['surface']};
    color: {t['text']};
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}}

.ingest-result {{
    border-radius: 8px; padding: 8px 11px;
    margin: 4px 0; font-size: 0.78rem;
    display: flex; align-items: flex-start; gap: 7px;
    line-height: 1.4;
}}
.ingest-ok   {{ background:{t['success_bg']}; color:{t['success']}; border:1px solid {t['success']}22; }}
.ingest-fail {{ background:{t['danger_bg']};  color:{t['danger']};  border:1px solid {t['danger']}22; }}
.ingest-result-name {{ font-weight: 600; }}
.ingest-result-detail {{ color: inherit; opacity: 0.75; font-size:0.73rem; }}

/* ── Chat area ── */
.chat-scroll {{
    height: 480px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 1.5rem 0;
    scrollbar-width: thin;
    scrollbar-color: {t['scrollbar']} transparent;
}}

.msg-group {{ display: flex; flex-direction: column; gap: 4px; }}
.msg-meta {{
    font-size: 0.68rem; color: {t['muted']};
    font-weight: 500; letter-spacing: 0.03em;
    padding: 0 2px;
}}
.msg-meta.right {{ text-align: right; }}

.msg-bubble {{
    padding: 0.75rem 1rem;
    border-radius: 14px;
    font-size: 0.875rem;
    line-height: 1.65;
    color: {t['text']};
    max-width: 78%;
    word-break: break-word;
    border: 1px solid {t['border']};
}}
.msg-user {{
    background: {t['user_bubble']};
    border-color: {t['accent']}33;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}}
.msg-bot {{
    background: {t['bot_bubble']};
    margin-right: auto;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}}

.source-row {{
    display: flex; flex-wrap: wrap; gap: 5px;
    margin-top: 8px; padding-top: 8px;
    border-top: 1px solid {t['border']};
}}
.source-tag {{
    display: inline-flex; align-items: center; gap: 4px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.7rem; color: {t['accent']};
    font-weight: 500;
}}

/* ── Landing / gate screen ── */
.gate-wrap {{
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 420px; text-align: center;
    gap: 16px; padding: 2rem;
}}
.gate-icon {{
    width: 64px; height: 64px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; margin-bottom: 4px;
}}
.gate-title {{
    font-size: 1.35rem; font-weight: 700;
    color: {t['text']}; letter-spacing: -0.02em;
}}
.gate-sub {{
    font-size: 0.875rem; color: {t['subtext']};
    max-width: 340px; line-height: 1.6;
}}
.gate-steps {{
    display: flex; gap: 12px; flex-wrap: wrap;
    justify-content: center; margin-top: 8px;
}}
.gate-step {{
    display: flex; align-items: center; gap: 7px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 8px; padding: 7px 13px;
    font-size: 0.78rem; color: {t['subtext']};
    font-weight: 500;
}}
.gate-step-num {{
    width: 20px; height: 20px; border-radius: 50%;
    background: {t['accent']}22; color: {t['accent']};
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 700; flex-shrink: 0;
}}

/* ── Chat header bar ── */
.chat-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1rem;
    border-bottom: 1px solid {t['border']};
    margin-bottom: 0.25rem;
}}
.chat-header-left {{ display: flex; align-items: center; gap: 10px; }}
.chat-header-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: {t['success']};
    box-shadow: 0 0 0 2px {t['success']}33;
}}
.chat-header-title {{
    font-size: 0.85rem; font-weight: 600; color: {t['text']};
}}
.chat-header-sub {{
    font-size: 0.72rem; color: {t['muted']};
}}
.doc-count-pill {{
    background: {t['surface2']}; border: 1px solid {t['border']};
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.72rem; font-weight: 600; color: {t['subtext']};
}}

/* ── Page header ── */
.page-header {{
    margin-bottom: 1.75rem;
}}
.page-title {{
    font-size: 1.5rem; font-weight: 700;
    color: {t['text']}; letter-spacing: -0.025em;
    margin-bottom: 3px;
}}
.page-sub {{
    font-size: 0.82rem; color: {t['muted']};
}}
</style>""", unsafe_allow_html=True)


# ── API helpers ────────────────────────────────────────────────────────────────
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
        r = requests.post(f"{API_BASE}/upload", files=file_tuples, timeout=180)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Cannot connect to backend."}
    except Exception as e:
        return 500, {"detail": str(e)}

def api_chat(question: str):
    try:
        r = requests.post(
            f"{API_BASE}/chat",
            json={"question": question, "include_sources": True},
            timeout=60,
        )
        return r.json() if r.status_code == 200 else {"answer": r.json().get("detail", "Error"), "sources": []}
    except requests.exceptions.ConnectionError:
        return {"answer": "Cannot connect to backend.", "sources": []}
    except Exception as e:
        return {"answer": f"Request failed: {e}", "sources": []}

def api_delete(filename: str):
    try:
        r = requests.delete(f"{API_BASE}/documents/{filename}", timeout=60)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}


# ── Inject styles ──────────────────────────────────────────────────────────────
t = theme()
inject_css(t)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand
    st.markdown(f"""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">⬡</div>
        <div class="sidebar-brand-text">
            <div class="sidebar-brand-name">LogiRAG</div>
            <div class="sidebar-brand-sub">Logistics Intelligence</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Theme toggle (pill style via columns trick)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "🌙  Dark",
            key="btn_dark",
            help="Switch to dark mode",
        ):
            st.session_state.dark_mode = True
            st.rerun()
    with c2:
        if st.button(
            "☀️  Light",
            key="btn_light",
            help="Switch to light mode",
        ):
            st.session_state.dark_mode = False
            st.rerun()

    # Style the active/inactive theme buttons
    active_col = "c1" if st.session_state.dark_mode else "c2"
    st.markdown(f"""<style>
    div[data-testid="column"]:nth-child({"1" if st.session_state.dark_mode else "2"}) .stButton > button {{
        background: {t['surface']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['border2']} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="column"]:nth-child({"2" if st.session_state.dark_mode else "1"}) .stButton > button {{
        background: transparent !important;
        color: {t['muted']} !important;
        border: 1px solid {t['border']} !important;
        box-shadow: none !important;
    }}
    div[data-testid="column"]:nth-child({"2" if st.session_state.dark_mode else "1"}) .stButton > button:hover {{
        background: {t['surface2']} !important;
        color: {t['text']} !important;
    }}
    </style>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Backend status
    st.markdown('<span class="section-label">System Status</span>', unsafe_allow_html=True)
    health = api_health()
    if health:
        vs_ready = health.get("vectorstore_initialized", False)
        st.markdown(
            f'<span class="status-dot status-online">● Backend online</span>',
            unsafe_allow_html=True,
        )
        if vs_ready:
            st.markdown(
                f'<span class="status-dot status-online" style="margin-top:4px;display:inline-flex">● Documents ready</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<span class="status-dot status-warn" style="margin-top:4px;display:inline-flex">◎ No documents loaded</span>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<span class="status-dot status-offline">● Backend offline</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"""<div style="background:{t['danger_bg']};border:1px solid {t['danger']}33;
            border-radius:8px;padding:10px 12px;margin-top:8px;font-size:0.78rem;color:{t['subtext']};">
            Start the backend first:<br/>
            <code style="color:{t['accent']};font-size:0.75rem;">uvicorn app:app --reload</code>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Upload ──
    st.markdown('<span class="section-label">Upload Documents</span>', unsafe_allow_html=True)
    st.markdown(f"""<p style="font-size:0.75rem;color:{t['muted']};margin-bottom:8px;line-height:1.5;">
        Only logistics & transport PDFs are accepted.<br/>Multiple files supported.
    </p>""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "upload",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.markdown(
            f'<p style="font-size:0.75rem;color:{t["muted"]};margin:6px 0 8px;">'
            f'{len(uploaded_files)} file{"s" if len(uploaded_files)>1 else ""} selected</p>',
            unsafe_allow_html=True,
        )
        if st.button("⬆  Process & Ingest", key="ingest_btn"):
            log = []
            with st.spinner("Classifying and embedding…"):
                status_code, result = api_upload(uploaded_files)

            if status_code == 200:
                for f in result.get("files_processed", []):
                    log.append(("ok", f["filename"], f"{f['chunks']} chunks indexed"))
                for f in result.get("files_rejected", []):
                    log.append(("fail", f["filename"], f["reason"]))
                if result.get("files_processed"):
                    st.session_state.docs_ready = True
            elif status_code == 422:
                detail = result.get("detail", {})
                for f in detail.get("rejected", []):
                    log.append(("fail", f["filename"], f["reason"]))
            elif status_code == 503:
                log.append(("fail", "Connection", result.get("detail", "Backend unreachable")))
            else:
                log.append(("fail", "Upload", f"HTTP {status_code}"))

            st.session_state.ingest_log = log
            st.rerun()

    # Show ingest results
    if st.session_state.ingest_log:
        st.markdown("<div style='margin-top:6px;'>", unsafe_allow_html=True)
        for kind, name, detail in st.session_state.ingest_log:
            cls = "ingest-ok" if kind == "ok" else "ingest-fail"
            icon = "✓" if kind == "ok" else "✗"
            st.markdown(f"""
            <div class="ingest-result {cls}">
                <span>{icon}</span>
                <div>
                    <div class="ingest-result-name">{name}</div>
                    <div class="ingest-result-detail">{detail}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Loaded docs ──
    st.markdown('<span class="section-label">Loaded Documents</span>', unsafe_allow_html=True)
    docs = api_documents()

    # Sync docs_ready with actual backend state
    if docs and not st.session_state.docs_ready:
        st.session_state.docs_ready = True

    if docs:
        for doc in docs:
            col_doc, col_del = st.columns([5, 1])
            with col_doc:
                st.markdown(f"""
                <div class="doc-row">
                    <span class="doc-row-icon">⬡</span>
                    <span class="doc-row-name" title="{doc['filename']}">{doc['filename']}</span>
                    <span class="doc-row-size">{doc['size_kb']}k</span>
                </div>""", unsafe_allow_html=True)
            with col_del:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_{doc['filename']}", help=f"Remove {doc['filename']}"):
                    sc, _ = api_delete(doc["filename"])
                    if sc == 200:
                        remaining = api_documents()
                        if not remaining:
                            st.session_state.docs_ready = False
                            st.session_state.chat_history = []
                            st.session_state.ingest_log = []
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<p style="font-size:0.78rem;color:{t["muted"]};font-style:italic;">No documents loaded.</p>',
            unsafe_allow_html=True,
        )

    # ── Clear chat ──
    if st.session_state.docs_ready and st.session_state.chat_history:
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("Clear conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PANEL
# ══════════════════════════════════════════════════════════════════════════════

# Page header
st.markdown(f"""
<div class="page-header">
    <div class="page-title">Logistics Document Assistant</div>
    <div class="page-sub">Ask questions grounded in your uploaded documents · Powered by Gemini</div>
</div>""", unsafe_allow_html=True)


# ── GATE: show landing screen until docs are ready ───────────────────────────
if not st.session_state.docs_ready:
    st.markdown(f"""
    <div class="gate-wrap">
        <div class="gate-icon">🗂</div>
        <div class="gate-title">No documents loaded</div>
        <div class="gate-sub">
            Upload one or more logistics PDFs from the sidebar to get started.
            Non-logistics documents are automatically rejected.
        </div>
        <div class="gate-steps">
            <div class="gate-step">
                <div class="gate-step-num">1</div>
                Select PDF files in the sidebar
            </div>
            <div class="gate-step">
                <div class="gate-step-num">2</div>
                Click Process & Ingest
            </div>
            <div class="gate-step">
                <div class="gate-step-num">3</div>
                Chat with your documents
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ── CHAT UI ──────────────────────────────────────────────────────────────────

# Header bar
doc_count = len(api_documents())
st.markdown(f"""
<div class="chat-header">
    <div class="chat-header-left">
        <div class="chat-header-dot"></div>
        <div>
            <div class="chat-header-title">Chat</div>
            <div class="chat-header-sub">Answers sourced from your documents only</div>
        </div>
    </div>
    <div class="doc-count-pill">{doc_count} document{"s" if doc_count != 1 else ""}</div>
</div>""", unsafe_allow_html=True)

# Chat messages
msgs_html = '<div class="chat-scroll" id="chat-scroll">'

if not st.session_state.chat_history:
    msgs_html += f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
        height:100%;gap:10px;color:{t['muted']};text-align:center;padding:2rem;">
        <div style="font-size:2rem;opacity:0.4;">💬</div>
        <div style="font-size:0.875rem;font-weight:500;color:{t['subtext']};">Start the conversation</div>
        <div style="font-size:0.78rem;max-width:280px;line-height:1.6;">
            Ask anything about your logistics documents — shipments, routes, carriers, timelines and more.
        </div>
    </div>"""
else:
    for msg in st.session_state.chat_history:
        ts  = msg.get("time", "")
        rol = msg["role"]
        content = msg["content"].replace("<", "&lt;").replace(">", "&gt;")

        if rol == "user":
            msgs_html += f"""
            <div class="msg-group" style="align-items:flex-end;">
                <div class="msg-meta right">You · {ts}</div>
                <div class="msg-bubble msg-user">{content}</div>
            </div>"""
        else:
            sources_html = ""
            if msg.get("sources"):
                chips = "".join(
                    f'<span class="source-tag">⬡ {s["filename"]} · p.{s["page"]}</span>'
                    for s in msg["sources"]
                )
                sources_html = f'<div class="source-row">{chips}</div>'
            msgs_html += f"""
            <div class="msg-group" style="align-items:flex-start;">
                <div class="msg-meta">LogiRAG · {ts}</div>
                <div class="msg-bubble msg-bot">{content}{sources_html}</div>
            </div>"""

msgs_html += "</div>"

# Auto-scroll to bottom
msgs_html += """<script>
    const el = document.getElementById('chat-scroll');
    if(el) el.scrollTop = el.scrollHeight;
</script>"""

st.markdown(msgs_html, unsafe_allow_html=True)

# ── Input row ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
col_q, col_send = st.columns([6, 1])

with col_q:
    question = st.text_input(
        "q",
        placeholder="Ask a question about your logistics documents…",
        label_visibility="collapsed",
        key="q_input",
    )

with col_send:
    send = st.button("Send", key="send_btn")

# Handle submission
if send and question.strip():
    st.session_state.chat_history.append({
        "role": "user",
        "content": question.strip(),
        "time": datetime.now().strftime("%H:%M"),
    })
    with st.spinner("Searching…"):
        result = api_chat(question.strip())
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result.get("answer", "No answer returned."),
        "sources": result.get("sources", []),
        "time": datetime.now().strftime("%H:%M"),
    })
    st.rerun()
elif send and not question.strip():
    st.markdown(
        f'<p style="font-size:0.78rem;color:{t["warning"]};margin-top:4px;">Please enter a question.</p>',
        unsafe_allow_html=True,
    )