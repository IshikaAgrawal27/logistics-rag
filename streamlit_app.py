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
    page_title="LogiRAG — Logistics Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "dark_mode": True,
    "chat_history": [],
    "docs_ready": False,
    "ingest_log": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Design tokens ──────────────────────────────────────────────────────────────
def theme():
    if st.session_state.dark_mode:
        return dict(
            bg           = "#0d0e14",
            sidebar      = "#0f1018",
            surface      = "#13141c",
            surface2     = "#191a24",
            surface3     = "#1f2030",
            border       = "#27293a",
            border2      = "#333549",
            text         = "#dde0f0",
            subtext      = "#7e82a0",
            muted        = "#4a4d68",
            accent       = "#4f72ff",
            accent2      = "#3556e0",
            accent_glow  = "#4f72ff30",
            accent_soft  = "#4f72ff10",
            user_bubble  = "#1a1f42",
            bot_bubble   = "#13141c",
            success      = "#10b981",
            danger       = "#ef4444",
            warning      = "#f59e0b",
            success_bg   = "#052e1c",
            danger_bg    = "#2d0b0b",
            warning_bg   = "#2d1c05",
            input_bg     = "#13141c",
            scrollbar    = "#27293a",
            glow_btn     = "0 0 18px #4f72ff40",
            shadow       = "0 4px 24px rgba(0,0,0,0.5)",
        )
    else:
        return dict(
            bg           = "#f2f3f8",
            sidebar      = "#ffffff",
            surface      = "#ffffff",
            surface2     = "#edeef6",
            surface3     = "#e4e5f0",
            border       = "#dadbe8",
            border2      = "#c4c6da",
            text         = "#0e0f1a",
            subtext      = "#454668",
            muted        = "#8888a8",
            accent       = "#3556e0",
            accent2      = "#2440ba",
            accent_glow  = "#3556e025",
            accent_soft  = "#3556e010",
            user_bubble  = "#e6eaff",
            bot_bubble   = "#ffffff",
            success      = "#059669",
            danger       = "#dc2626",
            warning      = "#d97706",
            success_bg   = "#ecfdf5",
            danger_bg    = "#fef2f2",
            warning_bg   = "#fffbeb",
            input_bg     = "#ffffff",
            scrollbar    = "#c4c6da",
            glow_btn     = "0 4px 18px #3556e030",
            shadow       = "0 2px 16px rgba(0,0,0,0.08)",
        )


def inject_css(t):
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
    background: {t['bg']} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: {t['text']} !important;
    font-size: 15px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}}

/* ── Hide Streamlit chrome ──────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden !important; }}
.stDeployButton {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}

/* ── Remove default padding from main container ── */
.main .block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: {t['sidebar']} !important;
    border-right: 1px solid {t['border']} !important;
    min-width: 260px !important;
    max-width: 280px !important;
}}
[data-testid="stSidebarContent"] {{
    padding: 1.5rem 1.25rem !important;
}}
section[data-testid="stSidebar"] * {{
    color: {t['text']} !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {t['scrollbar']}; border-radius: 99px; }}

/* ── Typography ── */
h1, h2, h3, h4 {{
    color: {t['text']} !important;
    font-weight: 600 !important;
    letter-spacing: -0.015em;
}}

/* ── Buttons global ── */
.stButton > button {{
    background: {t['accent']} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.005em !important;
    transition: background 0.15s ease, box-shadow 0.15s ease, transform 0.1s ease !important;
    cursor: pointer !important;
    font-family: 'Inter', sans-serif !important;
}}
.stButton > button:hover {{
    background: {t['accent2']} !important;
    box-shadow: {t['glow_btn']} !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
}}

/* Ghost button */
.btn-ghost > button {{
    background: transparent !important;
    color: {t['subtext']} !important;
    border: 1px solid {t['border']} !important;
    box-shadow: none !important;
}}
.btn-ghost > button:hover {{
    background: {t['surface2']} !important;
    color: {t['text']} !important;
    border-color: {t['border2']} !important;
    box-shadow: none !important;
    transform: none !important;
}}

/* Danger button */
.btn-danger > button {{
    background: transparent !important;
    color: {t['danger']} !important;
    border: 1px solid {t['danger']}33 !important;
    padding: 0.28rem 0.6rem !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}}
.btn-danger > button:hover {{
    background: {t['danger_bg']} !important;
    border-color: {t['danger']}55 !important;
    box-shadow: none !important;
    transform: none !important;
}}

/* Send button */
.btn-send > button {{
    background: {t['accent']} !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    height: 48px !important;
    width: 100% !important;
    box-shadow: none !important;
    padding: 0 !important;
    letter-spacing: 0.01em !important;
}}
.btn-send > button:hover {{
    background: {t['accent2']} !important;
    box-shadow: {t['glow_btn']} !important;
    transform: translateY(-1px) !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {t['surface2']} !important;
    border: 1.5px dashed {t['border2']} !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {t['accent']} !important;
}}

/* ── Text input ── */
.stTextInput > div > div > input {{
    background: {t['input_bg']} !important;
    color: {t['text']} !important;
    border: 1.5px solid {t['border']} !important;
    border-radius: 8px !important;
    padding: 0 1rem !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
    height: 48px !important;
    line-height: 48px !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{
    color: {t['muted']} !important;
    font-size: 0.92rem !important;
}}
.stTextInput label {{ display: none !important; }}

/* Remove the red border Streamlit adds on inputs with no label */
.stTextInput > div {{ border: none !important; box-shadow: none !important; }}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: {t['accent']} !important; }}

/* ── Divider ── */
hr {{
    border: none !important;
    border-top: 1px solid {t['border']} !important;
    margin: 1.1rem 0 !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    gap: 0 !important;
    border-bottom: 1px solid {t['border']} !important;
    padding: 0 2rem !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {t['muted']} !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.7rem 1.1rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    transition: color 0.15s !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.01em !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {t['text']} !important;
    background: transparent !important;
}}
.stTabs [aria-selected="true"] {{
    color: {t['accent']} !important;
    border-bottom-color: {t['accent']} !important;
    background: transparent !important;
    font-weight: 600 !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}
.stTabs [data-baseweb="tab-panel"] {{
    padding: 0 !important;
    background: transparent !important;
}}

/* ════════════════════════════════════════════
   HEADER
════════════════════════════════════════════ */
.app-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.5rem;
    height: 58px;
    background: {t['surface']};
    border-bottom: 1px solid {t['border']};
    position: sticky;
    top: 0;
    z-index: 200;
}}
.header-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.header-logo {{
    width: 28px;
    height: 28px;
    background: {t['accent']};
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.header-logo svg {{
    width: 16px;
    height: 16px;
    fill: none;
    stroke: #fff;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
}}
.header-name {{
    font-size: 0.95rem;
    font-weight: 700;
    color: {t['text']};
    letter-spacing: -0.01em;
}}
.header-divider {{
    width: 1px;
    height: 18px;
    background: {t['border']};
    margin: 0 12px;
}}
.header-sub {{
    font-size: 0.78rem;
    color: {t['muted']};
    font-weight: 400;
    letter-spacing: 0.01em;
}}

/* Status pill */
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 20px;
    letter-spacing: 0.01em;
}}
.status-online  {{ background:{t['success_bg']}; color:{t['success']}; border:1px solid {t['success']}25; }}
.status-offline {{ background:{t['danger_bg']};  color:{t['danger']};  border:1px solid {t['danger']}25; }}
.status-warn    {{ background:{t['warning_bg']}; color:{t['warning']}; border:1px solid {t['warning']}25; }}
.status-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}}
.status-dot-online  {{ background:{t['success']}; }}
.status-dot-offline {{ background:{t['danger']};  }}
.status-dot-warn    {{ background:{t['warning']}; }}

/* ════════════════════════════════════════════
   CHAT LAYOUT
════════════════════════════════════════════ */
.chat-outer {{
    display: flex;
    flex-direction: column;
    height: calc(100vh - 108px);
    background: {t['bg']};
}}

.chat-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 2rem 0;
    display: flex;
    flex-direction: column;
    gap: 0;
    scrollbar-width: thin;
    scrollbar-color: {t['scrollbar']} transparent;
}}

/* Single message row */
.msg-row {{
    padding: 0.55rem 2.5rem;
    display: flex;
    flex-direction: column;
    gap: 2px;
}}
.msg-row:hover {{
    background: {t['surface']}80;
}}

.msg-sender {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {t['muted']};
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.sender-you  {{ color: {t['accent']}; }}
.sender-time {{
    font-weight: 400;
    text-transform: none;
    letter-spacing: 0;
    color: {t['muted']};
    font-size: 0.72rem;
}}

.msg-body {{
    font-size: 0.96rem;
    line-height: 1.72;
    color: {t['text']};
    white-space: pre-wrap;
    word-break: break-word;
    max-width: 720px;
}}

.msg-user-row .msg-body {{
    color: {t['text']};
    background: {t['user_bubble']};
    border: 1px solid {t['accent']}2a;
    border-radius: 10px;
    padding: 0.72rem 1rem;
    display: inline-block;
    margin-left: auto;
    max-width: 640px;
}}
.msg-user-row {{
    align-items: flex-end;
}}
.msg-user-row .msg-sender {{
    text-align: right;
    justify-content: flex-end;
}}

/* Separator line between conversation turns */
.msg-divider {{
    height: 1px;
    background: {t['border']};
    margin: 0.25rem 2.5rem;
    opacity: 0.5;
}}

/* ── Sources disclosure ── */
.sources-disclosure {{
    margin-top: 8px;
    display: inline-block;
}}
.sources-disclosure summary {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    font-size: 0.78rem;
    font-weight: 500;
    color: {t['subtext']};
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 3px 12px;
    list-style: none;
    user-select: none;
    letter-spacing: 0.01em;
    transition: color 0.15s, background 0.15s, border-color 0.15s;
}}
.sources-disclosure summary::-webkit-details-marker {{ display: none; }}
.sources-disclosure summary:hover {{
    color: {t['accent']};
    background: {t['surface3']};
    border-color: {t['accent']}40;
}}
.sources-disclosure[open] summary {{
    color: {t['accent']};
    background: {t['accent_soft']};
    border-color: {t['accent']}40;
}}
.sources-panel {{
    margin-top: 8px;
    padding: 10px 14px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    max-width: 560px;
}}
.source-chip {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: {t['surface3']};
    border: 1px solid {t['border2']};
    border-radius: 5px;
    padding: 3px 10px;
    font-size: 0.78rem;
    color: {t['subtext']};
    font-weight: 500;
}}

/* ── Chat input bar ── */
.chat-input-wrap {{
    border-top: 1px solid {t['border']};
    padding: 0.9rem 2.5rem;
    background: {t['surface']};
    display: flex;
    align-items: center;
    gap: 10px;
}}

/* Force Streamlit layout inside our flex container */
.chat-input-wrap > div[data-testid="stHorizontalBlock"] {{
    width: 100% !important;
    align-items: center !important;
    gap: 10px !important;
}}
.chat-input-wrap [data-testid="column"] {{
    display: flex !important;
    align-items: center !important;
    padding: 0 !important;
}}
.chat-input-wrap [data-testid="column"]:first-child {{
    flex: 1 !important;
}}
.chat-input-wrap .stTextInput > div > div > input {{
    height: 48px !important;
}}
.chat-input-wrap .btn-send {{
    display: flex !important;
    align-items: center !important;
}}
.chat-input-wrap .btn-send > button {{
    height: 48px !important;
    min-width: 90px !important;
}}

/* ── Empty state ── */
.empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    gap: 10px;
    padding: 4rem 2rem;
    text-align: center;
    color: {t['muted']};
}}
.empty-icon {{
    width: 48px; height: 48px;
    border: 1.5px solid {t['border2']};
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 8px;
    opacity: 0.6;
}}
.empty-icon svg {{
    width: 22px; height: 22px;
    stroke: {t['muted']};
    fill: none;
    stroke-width: 1.5;
    stroke-linecap: round;
    stroke-linejoin: round;
}}
.empty-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: {t['subtext']};
}}
.empty-sub {{
    font-size: 0.85rem;
    color: {t['muted']};
    max-width: 340px;
    line-height: 1.6;
}}

/* ── Gate screen ── */
.gate-wrap {{
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 60vh; text-align: center;
    gap: 20px; padding: 3rem 2rem;
}}
.gate-title {{
    font-size: 1.3rem; font-weight: 700;
    color: {t['text']}; letter-spacing: -0.02em;
}}
.gate-sub {{
    font-size: 0.9rem; color: {t['subtext']};
    max-width: 380px; line-height: 1.65;
}}
.gate-steps {{
    display: flex; gap: 8px; flex-wrap: wrap;
    justify-content: center; margin-top: 6px;
}}
.gate-step {{
    display: flex; align-items: center; gap: 9px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 8px; padding: 9px 16px;
    font-size: 0.84rem; color: {t['subtext']};
    font-weight: 500;
}}
.gate-step-num {{
    width: 22px; height: 22px; border-radius: 50%;
    background: {t['accent_soft']};
    color: {t['accent']};
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
    border: 1px solid {t['accent']}30;
}}

/* ── Section label ── */
.section-label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {t['muted']};
    margin-bottom: 0.6rem;
    display: block;
}}

/* ── Sidebar doc items ── */
.doc-item {{
    display: flex; align-items: center; gap: 8px;
    padding: 8px 10px;
    border-radius: 7px;
    margin-bottom: 2px;
    transition: background 0.12s;
}}
.doc-item:hover {{ background: {t['surface2']}; }}
.doc-item-icon {{
    width: 28px; height: 28px;
    border-radius: 6px;
    background: {t['surface3']};
    border: 1px solid {t['border']};
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 11px;
    color: {t['subtext']};
    font-weight: 600;
}}
.doc-item-name {{
    font-size: 0.8rem; font-weight: 500;
    color: {t['text']}; flex: 1; min-width: 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.doc-item-size {{ font-size: 0.7rem; color: {t['muted']}; flex-shrink: 0; }}

/* ── Offline notice ── */
.offline-warn {{
    background: {t['danger_bg']};
    border: 1px solid {t['danger']}25;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.8rem;
    color: {t['subtext']};
    margin-top: 8px;
    line-height: 1.6;
}}

/* ── Upload panel ── */
.panel {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 12px;
    padding: 2rem;
    margin: 1.75rem 2.5rem;
}}
.panel-title {{
    font-size: 0.95rem;
    font-weight: 700;
    color: {t['text']};
    margin-bottom: 4px;
    letter-spacing: -0.01em;
}}
.panel-sub {{
    font-size: 0.84rem;
    color: {t['muted']};
    margin-bottom: 1.4rem;
    line-height: 1.55;
}}

/* ── Ingest results ── */
.ingest-row {{
    display: flex; align-items: flex-start; gap: 10px;
    border-radius: 8px; padding: 10px 14px;
    margin: 4px 0; font-size: 0.85rem; line-height: 1.5;
}}
.ingest-ok   {{ background:{t['success_bg']}; color:{t['success']}; border:1px solid {t['success']}25; }}
.ingest-fail {{ background:{t['danger_bg']};  color:{t['danger']};  border:1px solid {t['danger']}25; }}
.ingest-row-name {{ font-weight: 600; }}
.ingest-row-detail {{ opacity: 0.75; font-size: 0.78rem; margin-top: 1px; }}

/* ── Docs panel ── */
.docs-panel {{ padding: 1.75rem 2.5rem; }}
.docs-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.25rem;
}}
.docs-title {{ font-size: 0.95rem; font-weight: 700; color: {t['text']}; }}
.docs-count {{
    background: {t['surface2']};
    color: {t['subtext']};
    border: 1px solid {t['border']};
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.76rem;
    font-weight: 600;
}}
.doc-card {{
    display: flex; align-items: center; gap: 12px;
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    transition: border-color 0.15s;
}}
.doc-card:hover {{ border-color: {t['border2']}; }}
.doc-card-icon {{
    width: 36px; height: 36px;
    background: {t['surface2']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700;
    color: {t['subtext']}; flex-shrink: 0;
    letter-spacing: 0.05em;
}}
.doc-card-body {{ flex: 1; min-width: 0; }}
.doc-card-name {{
    font-size: 0.88rem; font-weight: 600;
    color: {t['text']}; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
}}
.doc-card-meta {{ font-size: 0.74rem; color: {t['muted']}; margin-top: 2px; }}

/* ── Sidebar brand ── */
.sidebar-logo-row {{
    display: flex; align-items: center; gap: 9px;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid {t['border']};
    margin-bottom: 1.25rem;
}}
.sidebar-logo {{
    width: 30px; height: 30px;
    background: {t['accent']};
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}}
.sidebar-logo svg {{
    width: 16px; height: 16px;
    fill: none; stroke: #fff;
    stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
}}
.sidebar-name {{
    font-size: 0.9rem; font-weight: 700;
    color: {t['text']}; letter-spacing: -0.02em;
}}
.sidebar-sub {{
    font-size: 0.67rem; color: {t['muted']};
    letter-spacing: 0.04em;
}}

/* Theme toggle buttons override */
.theme-col-active > div > button {{
    background: {t['surface3']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['border2']} !important;
    box-shadow: none !important;
}}
.theme-col-inactive > div > button {{
    background: transparent !important;
    color: {t['muted']} !important;
    border: 1px solid {t['border']} !important;
    box-shadow: none !important;
}}
.theme-col-inactive > div > button:hover {{
    background: {t['surface2']} !important;
    color: {t['text']} !important;
    transform: none !important;
    box-shadow: none !important;
}}
</style>""", unsafe_allow_html=True)


# ── SVG icons ─────────────────────────────────────────────────────────────────
TRUCK_ICON = """<svg viewBox="0 0 24 24"><path d="M1 3h15v13H1zM16 8h4l3 3v5h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>"""
MSG_ICON   = """<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""


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


# ── Bootstrap ──────────────────────────────────────────────────────────────────
t      = theme()
inject_css(t)
health = api_health()
docs   = api_documents()

if docs and not st.session_state.docs_ready:
    st.session_state.docs_ready = True
if not docs and st.session_state.docs_ready:
    st.session_state.docs_ready = False


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo-row">
        <div class="sidebar-logo">{TRUCK_ICON}</div>
        <div>
            <div class="sidebar-name">LogiRAG</div>
            <div class="sidebar-sub">Logistics Intelligence</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Status
    st.markdown('<span class="section-label">Status</span>', unsafe_allow_html=True)
    if health:
        vs_ready = health.get("vectorstore_initialized", False)
        st.markdown(
            '<span class="status-pill status-online"><span class="status-dot status-dot-online"></span>Backend connected</span>',
            unsafe_allow_html=True,
        )
        lbl = "index ready" if vs_ready else "no documents"
        cls = "status-online" if vs_ready else "status-warn"
        dcl = "status-dot-online" if vs_ready else "status-dot-warn"
        st.markdown(
            f'<span class="status-pill {cls}" style="margin-top:5px;display:inline-flex"><span class="status-dot {dcl}"></span>{lbl}</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-pill status-offline"><span class="status-dot status-dot-offline"></span>Backend offline</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"""<div class="offline-warn">
            Start the backend server:<br/>
            <code style="color:{t['accent']};font-size:0.78rem;">uvicorn app:app --reload</code>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Documents
    st.markdown('<span class="section-label">Documents</span>', unsafe_allow_html=True)
    if docs:
        for doc in docs:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"""
                <div class="doc-item">
                    <div class="doc-item-icon">PDF</div>
                    <span class="doc-item-name" title="{doc['filename']}">{doc['filename']}</span>
                    <span class="doc-item-size">{doc['size_kb']}k</span>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("x", key=f"del_{doc['filename']}", help=f"Remove {doc['filename']}"):
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
            f'<p style="font-size:0.82rem;color:{t["muted"]};padding:2px 0;">No documents loaded.</p>',
            unsafe_allow_html=True,
        )

    # Clear chat
    if st.session_state.docs_ready and st.session_state.chat_history:
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("Clear conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Theme toggle
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<span class="section-label">Appearance</span>', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button("Dark", key="btn_dark"):
            st.session_state.dark_mode = True
            st.rerun()
    with tc2:
        if st.button("Light", key="btn_light"):
            st.session_state.dark_mode = False
            st.rerun()

    # Highlight active theme button
    active_n  = 1 if st.session_state.dark_mode else 2
    passive_n = 2 if st.session_state.dark_mode else 1
    st.markdown(f"""<style>
    div[data-testid="stSidebar"] div[data-testid="column"]:nth-child({active_n}) .stButton > button {{
        background: {t['surface3']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['border2']} !important;
        box-shadow: none !important;
    }}
    div[data-testid="stSidebar"] div[data-testid="column"]:nth-child({passive_n}) .stButton > button {{
        background: transparent !important;
        color: {t['muted']} !important;
        border: 1px solid {t['border']} !important;
        box-shadow: none !important;
    }}
    div[data-testid="stSidebar"] div[data-testid="column"]:nth-child({passive_n}) .stButton > button:hover {{
        background: {t['surface2']} !important;
        color: {t['text']} !important;
        transform: none !important;
        box-shadow: none !important;
    }}
    </style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
if health:
    vs_ready = health.get("vectorstore_initialized", False)
    if vs_ready:
        status_html = f'<span class="status-pill status-online"><span class="status-dot status-dot-online"></span>Ready &mdash; {len(docs)} document{"s" if len(docs) != 1 else ""}</span>'
    else:
        status_html = '<span class="status-pill status-warn"><span class="status-dot status-dot-warn"></span>No documents loaded</span>'
else:
    status_html = '<span class="status-pill status-offline"><span class="status-dot status-dot-offline"></span>Backend offline</span>'

st.markdown(f"""
<div class="app-header">
    <div class="header-brand">
        <div class="header-logo">{TRUCK_ICON}</div>
        <span class="header-name">LogiRAG</span>
        <div class="header-divider"></div>
        <span class="header-sub">Logistics Document Intelligence</span>
    </div>
    {status_html}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_chat, tab_upload, tab_docs = st.tabs(["Chat", "Upload Documents", "Manage Documents"])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — CHAT
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:

    if not st.session_state.docs_ready:
        # Gate screen — no documents uploaded yet
        st.markdown(f"""
        <div class="gate-wrap">
            <div style="font-size:0.75rem;font-weight:600;letter-spacing:0.1em;
                        text-transform:uppercase;color:{t['muted']};margin-bottom:4px;">
                Getting Started
            </div>
            <div class="gate-title">No Documents Loaded</div>
            <div class="gate-sub">
                Upload logistics PDF files to begin asking questions.
                Non-logistics documents are automatically rejected.
            </div>
            <div class="gate-steps">
                <div class="gate-step">
                    <div class="gate-step-num">1</div>
                    Open <strong>Upload Documents</strong>
                </div>
                <div class="gate-step">
                    <div class="gate-step-num">2</div>
                    Select and ingest PDF files
                </div>
                <div class="gate-step">
                    <div class="gate-step-num">3</div>
                    Return here and chat
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    else:
        # ── Build messages HTML ──────────────────────────────────────────────
        msgs_html = '<div class="chat-messages" id="chat-scroll">'

        if not st.session_state.chat_history:
            msgs_html += f"""
            <div class="empty-state">
                <div class="empty-icon">{MSG_ICON}</div>
                <div class="empty-title">Start a conversation</div>
                <div class="empty-sub">
                    Ask anything about your logistics documents — shipments, carriers,
                    routes, timelines, compliance, and more.
                </div>
            </div>"""
        else:
            for i, msg in enumerate(st.session_state.chat_history):
                ts      = msg.get("time", "")
                role    = msg["role"]
                content = msg["content"].replace("<", "&lt;").replace(">", "&gt;")

                if role == "user":
                    msgs_html += f"""
                    <div class="msg-row msg-user-row">
                        <div class="msg-sender sender-you">You <span class="sender-time">{ts}</span></div>
                        <div class="msg-body">{content}</div>
                    </div>"""
                else:
                    # Sources collapsible — outside the bubble, clean pill
                    sources_html = ""
                    sources = msg.get("sources", [])
                    if sources:
                        count = len(sources)
                        chips = "".join(
                            f'<span class="source-chip">{s["filename"]} &nbsp;&middot;&nbsp; p.{s["page"]}</span>'
                            for s in sources
                        )
                        sources_html = f"""
                        <details class="sources-disclosure">
                            <summary>{count} source{"s" if count != 1 else ""}</summary>
                            <div class="sources-panel">{chips}</div>
                        </details>"""

                    msgs_html += f"""
                    <div class="msg-row">
                        <div class="msg-sender">LogiRAG <span class="sender-time">{ts}</span></div>
                        <div class="msg-body">{content}</div>
                        {sources_html}
                    </div>"""

                # Separator between turns (not after last)
                if i < len(st.session_state.chat_history) - 1:
                    msgs_html += '<div class="msg-divider"></div>'

        msgs_html += "</div>"
        msgs_html += """<script>
            (function(){
                var el = document.getElementById('chat-scroll');
                if(el) el.scrollTop = el.scrollHeight;
            })();
        </script>"""

        st.markdown(msgs_html, unsafe_allow_html=True)

        # ── Input bar ──────────────────────────────────────────────────────
        st.markdown('<div class="chat-input-wrap">', unsafe_allow_html=True)
        col_q, col_btn = st.columns([10, 1])

        with col_q:
            question = st.text_input(
                "question",
                placeholder="Ask a question about your logistics documents…",
                label_visibility="collapsed",
                key="q_input",
            )
        with col_btn:
            st.markdown('<div class="btn-send">', unsafe_allow_html=True)
            send = st.button("Send", key="send_btn")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Handle submission ──────────────────────────────────────────────
        if send and question.strip():
            st.session_state.chat_history.append({
                "role": "user",
                "content": question.strip(),
                "time": datetime.now().strftime("%H:%M"),
            })
            with st.spinner("Searching documents…"):
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
                f'<p style="font-size:0.84rem;color:{t["warning"]};padding:4px 2.5rem 0;">Please enter a question first.</p>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
with tab_upload:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Upload Logistics Documents</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-sub">Upload one or more PDF files. Only logistics and transport-related documents are accepted; others will be automatically rejected.</div>',
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Drop PDF files here or click to browse",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="visible",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        st.markdown(
            f'<p style="font-size:0.86rem;color:{t["subtext"]};margin:6px 2.5rem 14px;">'
            f'<strong>{len(uploaded_files)}</strong> file{"s" if len(uploaded_files) > 1 else ""} selected</p>',
            unsafe_allow_html=True,
        )
        col_btn, _ = st.columns([2, 6])
        with col_btn:
            if st.button("Process and Ingest", key="ingest_btn"):
                log = []
                with st.spinner("Classifying and embedding documents…"):
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
                    log.append(("fail", "Connection error", result.get("detail", "Backend unreachable")))
                else:
                    log.append(("fail", "Upload failed", f"HTTP {status_code}"))

                st.session_state.ingest_log = log
                st.rerun()

    if st.session_state.ingest_log:
        st.markdown('<div style="padding:0 2.5rem;margin-top:8px;">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Ingest Results</span>', unsafe_allow_html=True)
        for kind, name, detail in st.session_state.ingest_log:
            cls  = "ingest-ok" if kind == "ok" else "ingest-fail"
            icon = "+" if kind == "ok" else "-"
            st.markdown(f"""
            <div class="ingest-row {cls}">
                <span style="font-size:1rem;font-weight:700;flex-shrink:0;">{icon}</span>
                <div>
                    <div class="ingest-row-name">{name}</div>
                    <div class="ingest-row-detail">{detail}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — MANAGE DOCUMENTS
# ─────────────────────────────────────────────────────────────────────────────
with tab_docs:
    st.markdown('<div class="docs-panel">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="docs-header">
        <div class="docs-title">Indexed Documents</div>
        <span class="docs-count">{len(docs)} document{"s" if len(docs) != 1 else ""}</span>
    </div>""", unsafe_allow_html=True)

    if docs:
        for doc in docs:
            col_card, col_action = st.columns([6, 1])
            with col_card:
                st.markdown(f"""
                <div class="doc-card">
                    <div class="doc-card-icon">PDF</div>
                    <div class="doc-card-body">
                        <div class="doc-card-name" title="{doc['filename']}">{doc['filename']}</div>
                        <div class="doc-card-meta">{doc['size_kb']} KB &nbsp;&middot;&nbsp; PDF</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_action:
                st.markdown('<div class="btn-danger" style="padding-top:8px;">', unsafe_allow_html=True)
                if st.button("Remove", key=f"main_del_{doc['filename']}", help=f"Delete {doc['filename']}"):
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
        st.markdown(f"""
        <div style="text-align:center;padding:4rem 1rem;color:{t['muted']};">
            <div style="font-size:0.95rem;font-weight:600;color:{t['subtext']};margin-bottom:8px;">
                No documents indexed
            </div>
            <div style="font-size:0.85rem;line-height:1.65;">
                Upload PDF files in the <strong>Upload Documents</strong> tab to get started.
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)