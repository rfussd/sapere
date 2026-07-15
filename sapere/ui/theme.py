"""Estilos globales de Sapere — Dark theme profesional con glassmorphism."""

GLOBAL_CSS = """
<style>
/* === BASE === */
.stApp { background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); }

/* === HEADERS === */
h1 { color: #58a6ff !important; font-weight: 700 !important; letter-spacing: -0.5px; }
h2 { color: #c9d1d9 !important; font-weight: 600 !important; }
h3 { color: #8b949e !important; font-weight: 500 !important; }

/* === CARDS === */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: linear-gradient(145deg, rgba(22,27,34,0.9) 0%, rgba(13,17,23,0.95) 100%) !important;
    border: 1px solid rgba(88,166,255,0.15) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(12px) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(88,166,255,0.08) !important;
}

/* === METRICS === */
[data-testid="stMetricValue"] { font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
    border-right: 1px solid rgba(48,54,61,0.5) !important;
}

/* === BUTTONS === */
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    letter-spacing: -0.3px !important;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(35,134,54,0.3) !important;
}
div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(35,134,54,0.4) !important;
    transform: translateY(-1px) !important;
}

/* === PROGRESS BARS === */
div[data-testid="stProgress"] > div {
    background: rgba(88,166,255,0.15) !important;
    border-radius: 6px !important;
}
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #58a6ff, #79c0ff) !important;
    border-radius: 6px !important;
}

/* === TABS === */
div[data-testid="stTabs"] button {
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: rgba(88,166,255,0.12) !important;
    border-bottom: 2px solid #58a6ff !important;
    color: #58a6ff !important;
}

/* === TEXT AREAS === */
textarea { border-radius: 10px !important; border: 1px solid #30363d !important; }

/* === SELECT BOX === */
div[data-testid="stSelectbox"] > div { border-radius: 10px !important; }

/* === SUCCESS/ERROR === */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(48,54,61,0.5) !important;
}

/* === BALLOONS === */
@keyframes floatUp {
    0% { opacity: 0; transform: translateY(100vh) scale(0.5); }
    50% { opacity: 1; }
    100% { opacity: 0; transform: translateY(-10vh) scale(1.2); }
}

/* === SESSION BADGE === */
.session-active {
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(88,166,255,0.4); }
    50% { box-shadow: 0 0 0 8px rgba(88,166,255,0); }
}
</style>
"""

PAGE_CONFIG = {
    "page_title": "Sapere",
    "page_icon": "🧠",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
