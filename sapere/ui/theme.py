"""Estilos globales de Sapere — Dark theme premium."""

GLOBAL_CSS = """
<style>
:root {
    --bg: #0a0e14;
    --surface: #131820;
    --border: #1e2733;
    --text: #bfc6d0;
    --text-dim: #6e7681;
    --blue: #58a6ff;
    --green: #3fb950;
    --orange: #d29922;
    --red: #f85149;
    --purple: #bc8cff;
}

.stApp { background: var(--bg); }

h1, h2, h3 { font-weight: 600 !important; letter-spacing: -0.3px !important; }
h1 { font-size: 2rem !important; }
h2 { font-size: 1.3rem !important; color: var(--text) !important; }
h3 { font-size: 1.1rem !important; color: var(--text-dim) !important; }

section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    border-color: rgba(88,166,255,0.25) !important;
}

[data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 700 !important; color: var(--text) !important; }
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: var(--text-dim) !important; }
[data-testid="stMetricDelta"] { display: none !important; }

div.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: all 0.15s !important;
    padding: 0.4rem 1rem !important;
}
div.stButton > button[kind="primary"] {
    background: #238636 !important;
    border: 1px solid rgba(63,185,80,0.3) !important;
    color: white !important;
}
div.stButton > button[kind="primary"]:hover {
    background: #2ea043 !important;
}

div[data-testid="stProgress"] > div {
    background: rgba(88,166,255,0.1) !important;
    border-radius: 3px !important;
}
div[data-testid="stProgress"] > div > div {
    background: var(--blue) !important;
    border-radius: 3px !important;
}

div[data-testid="stTabs"] button {
    color: var(--text-dim) !important;
    font-weight: 500 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
}

textarea, input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
}

.stSelectbox > div > div { border-radius: 8px !important; }
.stRadio > div { gap: 2px !important; }
.stRadio label { padding: 6px 12px !important; border-radius: 6px !important; font-size: 0.85rem !important; }

.caption { font-size: 0.8rem; color: var(--text-dim); }

@media (max-width: 768px) {
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1rem !important; }
}
</style>
"""

PAGE_CONFIG = {
    "page_title": "Sapere",
    "page_icon": "🧠",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
