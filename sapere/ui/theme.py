"""Estilos globales de Sapere — Dark theme premium, alta legibilidad."""

GLOBAL_CSS = """
<style>
:root {
    --bg: #090c10;
    --surface: #131922;
    --border: #202835;
    --text: #e6edf3;
    --text-bright: #ffffff;
    --text-dim: #8b949e;
    --blue: #58a6ff;
    --green: #3fb950;
    --orange: #d29922;
    --red: #f85149;
    --purple: #bc8cff;
    --blue-glow: rgba(88,166,255,0.15);
    --green-glow: rgba(63,185,80,0.2);
    --red-glow: rgba(248,81,73,0.2);
}

.stApp { background: var(--bg); }

/* Headers */
h1 { color: var(--text-bright) !important; font-size: 1.8rem !important; font-weight: 700 !important; }
h2 { color: var(--text-bright) !important; font-size: 1.3rem !important; font-weight: 600 !important; }
h3 { color: var(--text) !important; font-size: 1.1rem !important; font-weight: 600 !important; }
h4 { color: var(--text-bright) !important; font-size: 1rem !important; font-weight: 600 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown {
    color: var(--text) !important;
}

/* Cards (border=True containers) */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 18px 22px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    border-color: rgba(88,166,255,0.3) !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.3) !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: var(--text-bright) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    color: var(--text-dim) !important;
    font-weight: 400 !important;
}

/* BUTTONS - BIG AND VISIBLE */
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.15s !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
div.stButton > button:hover {
    border-color: var(--blue) !important;
    color: var(--text-bright) !important;
}
div.stButton > button[kind="primary"] {
    background: #238636 !important;
    border: 1px solid #2ea043 !important;
    color: #ffffff !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.4rem !important;
    box-shadow: 0 2px 8px var(--green-glow) !important;
}
div.stButton > button[kind="primary"]:hover {
    background: #2ea043 !important;
    box-shadow: 0 4px 16px var(--green-glow) !important;
    transform: translateY(-1px) !important;
}

/* Progress bars */
div[data-testid="stProgress"] > div {
    background: rgba(88,166,255,0.08) !important;
    border-radius: 4px !important;
    height: 6px !important;
}
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #58a6ff, #79c0ff) !important;
    border-radius: 4px !important;
}

/* TABS - bright and clear */
div[data-testid="stTabs"] {
    margin-bottom: 16px !important;
}
div[data-testid="stTabs"] button {
    color: var(--text) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
    background: transparent !important;
    border: none !important;
}
div[data-testid="stTabs"] button:hover {
    color: var(--text-bright) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #58a6ff !important;
    font-weight: 700 !important;
    border-bottom: 3px solid #58a6ff !important;
    background: rgba(88,166,255,0.06) !important;
}

/* Inputs */
textarea, input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-size: 0.95rem !important;
    padding: 10px 14px !important;
}
textarea:focus, input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px var(--blue-glow) !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    padding: 14px 18px !important;
}
div[data-testid="stAlert"] p {
    font-size: 0.95rem !important;
}

/* Select/Slider/Radio polish */
.stSelectbox > div > div { border-radius: 10px !important; }
.stRadio > div { gap: 4px !important; }
.stRadio label { padding: 8px 14px !important; border-radius: 8px !important; font-size: 0.9rem !important; }

/* Caption text */
.stCaption, .stMarkdown p, p {
    color: var(--text) !important;
    font-size: 0.9rem !important;
}

/* Checkbox */
.stCheckbox label {
    font-size: 0.9rem !important;
    color: var(--text) !important;
}

/* Expander */
div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    background: var(--surface) !important;
}

/* Mobile responsive */
@media (max-width: 768px) {
    h1 { font-size: 1.3rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 0.95rem !important; }
    div.stButton > button { font-size: 0.85rem !important; padding: 0.5rem 1rem !important; }
}
</style>
"""

PAGE_CONFIG = {
    "page_title": "Sapere",
    "page_icon": "🧠",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
