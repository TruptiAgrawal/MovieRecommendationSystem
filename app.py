import streamlit as st
try:
    from model import recommend_movies
    HAS_MODEL = True
except Exception:
    HAS_MODEL = False

st.set_page_config(
    page_title="MovieTime",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Session state ─────────────────────────────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.dark_mode = True
    st.session_state.recommendations = []
    st.session_state.searched = False
    st.session_state.error_msg = ""
    st.session_state.query = ""
if "dark_mode"       not in st.session_state: st.session_state.dark_mode       = True
if "recommendations" not in st.session_state: st.session_state.recommendations = []
if "searched"        not in st.session_state: st.session_state.searched        = False
if "error_msg"       not in st.session_state: st.session_state.error_msg       = ""
if "query"           not in st.session_state: st.session_state.query           = ""

# ── Palettes ──────────────────────────────────────────────────────────────────
DARK = {
    "bg":         "#0f0f0f",
    "bg2":        "#161616",
    "nav_bg":     "rgba(15,15,15,0.92)",
    "card":       "#1c1c1c",
    "card_b":     "#2a2a2a",
    "accent":     "#e50914",       # Netflix red
    "accent2":    "#f5a623",
    "text":       "#e8e8e8",
    "text_dim":   "#888",
    "input_bg":   "#1c1c1c",
    "input_b":    "#333",
    "star":       "#f5a623",
    "badge_bg":   "#2a1a1a",
    "glow":       "rgba(229,9,20,0.22)",
    "scrollbar":  "#e50914",
}
LIGHT = {
    "bg":         "#f5f5f5",
    "bg2":        "#ebebeb",
    "nav_bg":     "rgba(245,245,245,0.95)",
    "card":       "#ffffff",
    "card_b":     "#ddd",
    "accent":     "#e50914",
    "accent2":    "#d4850a",
    "text":       "#111",
    "text_dim":   "#666",
    "input_bg":   "#fff",
    "input_b":    "#ccc",
    "star":       "#d4850a",
    "badge_bg":   "#fce8e8",
    "glow":       "rgba(229,9,20,0.10)",
    "scrollbar":  "#e50914",
}

C = DARK if st.session_state.dark_mode else LIGHT

@st.cache_data
def get_trending():
    return TRENDING

# ── Trending / popular movies shown on landing ────────────────────────────────
TRENDING = [
    {"title": "Inception",          "genre": "Sci-Fi",    "year": "2010", "emoji": "🌀", "rating": "8.8"},
    {"title": "The Dark Knight",    "genre": "Action",    "year": "2008", "emoji": "🦇", "rating": "9.0"},
    {"title": "Interstellar",       "genre": "Sci-Fi",    "year": "2014", "emoji": "🚀", "rating": "8.6"},
    {"title": "Parasite",           "genre": "Thriller",  "year": "2019", "emoji": "🏠", "rating": "8.5"},
    {"title": "Dune",               "genre": "Sci-Fi",    "year": "2021", "emoji": "🏜️", "rating": "8.0"},
    {"title": "Everything Everywhere", "genre": "Action", "year": "2022", "emoji": "🥯", "rating": "7.8"},
    {"title": "Oppenheimer",        "genre": "Drama",     "year": "2023", "emoji": "☢️", "rating": "8.3"},
    {"title": "Whiplash",           "genre": "Drama",     "year": "2014", "emoji": "🥁", "rating": "8.5"},
    {"title": "Get Out",            "genre": "Horror",    "year": "2017", "emoji": "👁️", "rating": "7.7"},
    {"title": "Mad Max: Fury Road", "genre": "Action",    "year": "2015", "emoji": "🔥", "rating": "8.1"},
    {"title": "The Godfather",      "genre": "Crime",     "year": "1972", "emoji": "🌹", "rating": "9.2"},
    {"title": "Spirited Away",      "genre": "Animation", "year": "2001", "emoji": "🐉", "rating": "8.6"},
]

MOVIE_EMOJIS = ["🎬","🎥","🍿","🎞️","🌟","💥","🎭","⚡","🔮","🌙","🗡️","🎪"]


# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">', unsafe_allow_html=True)
st.markdown(f"""
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {{
    background: {C["bg"]} !important;
    color: {C["text"]} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* Hide all Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"] {{ display: none !important; }}

/* Remove default block padding */
[data-testid="stMainBlockContainer"],
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: {C["bg"]}; }}
::-webkit-scrollbar-thumb {{ background: {C["accent"]}; border-radius: 3px; }}

/* ── NAVBAR ─────────────────────────────────────────────────────── */
.navbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    height: 60px;
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    background: {C["nav_bg"]};
    backdrop-filter: blur(20px);
    border-bottom: 1px solid {C["card_b"]}55;
}}
.nav-logo {{
    font-family: 'Bebas Neue', cursive;
    font-size: 1.7rem;
    letter-spacing: 2px;
    color: {C["accent"]};
    flex-shrink: 0;
}}
.nav-links {{
    display: flex; gap: 24px;
    font-size: 0.82rem; font-weight: 500;
    color: {C["text_dim"]};
    flex-shrink: 0;
}}
.nav-links span {{ cursor: pointer; transition: color 0.2s; }}
.nav-links span:hover {{ color: {C["text"]}; }}

/* ── SEARCH + TOGGLE inside navbar (Streamlit columns sit here) ── */
.nav-right-area {{
    display: flex; align-items: center; gap: 10px;
    min-width: 0; flex: 1; justify-content: flex-end;
    max-width: 480px; margin-left: auto;
}}

/* Streamlit columns used for the nav-right area */
div[data-testid="stHorizontalBlock"] {{
    gap: 0 !important;
    align-items: center !important;
}}

/* Text input → pill style */
[data-testid="stTextInput"] > div > div {{
    background: {C["input_bg"]} !important;
    border: 1.5px solid {C["input_b"]} !important;
    border-radius: 24px !important;
    padding: 2px 16px !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
    height: 38px !important;
}}
[data-testid="stTextInput"] > div > div:focus-within {{
    border-color: {C["accent"]} !important;
    box-shadow: 0 0 0 3px {C["glow"]} !important;
}}
[data-testid="stTextInput"] input {{
    color: {C["text"]} !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0 !important;
    height: 100% !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: {C["text_dim"]} !important; }}
[data-testid="stTextInput"] label {{ display: none !important; }}
[data-testid="stTextInput"] {{ margin-bottom: 0 !important; }}

/* All buttons */
.stButton > button {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border-radius: 24px !important;
    border: none !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    height: 38px !important;
    white-space: nowrap !important;
    padding: 0 20px !important;
    letter-spacing: 0.3px !important;
    line-height: 38px !important;
}}

/* Search button */
.search-btn .stButton > button {{
    background: {C["accent"]} !important;
    color: #fff !important;
    box-shadow: 0 2px 12px {C["glow"]} !important;
}}
.search-btn .stButton > button:hover {{
    filter: brightness(1.1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px {C["glow"]} !important;
}}

/* Theme toggle button */
.theme-btn .stButton > button {{
    background: {C["card"]} !important;
    color: {C["text"]} !important;
    border: 1.5px solid {C["card_b"]} !important;
    padding: 0 14px !important;
}}
.theme-btn .stButton > button:hover {{
    border-color: {C["accent"]} !important;
    color: {C["accent"]} !important;
}}

/* ── HERO ────────────────────────────────────────────────────────── */
.hero {{
    padding: 140px 40px 60px;
    text-align: center;
    background:
        radial-gradient(ellipse 60% 40% at 50% 0%, {C["glow"]} 0%, transparent 70%),
        {C["bg"]};
    position: relative;
    overflow: hidden;
}}
.hero-tag {{
    display: inline-block;
    background: {C["accent"]}1a;
    color: {C["accent"]};
    border: 1px solid {C["accent"]}44;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 20px;
}}
.hero-title {{
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(3.5rem, 9vw, 7rem);
    line-height: 0.95;
    color: {C["text"]};
    letter-spacing: 3px;
    margin-bottom: 16px;
}}
.hero-title .red {{ color: {C["accent"]}; }}
.hero-sub {{
    font-size: 1rem;
    color: {C["text_dim"]};
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}}

/* ── TRENDING SECTION ────────────────────────────────────────────── */
.section {{
    padding: 48px 40px 64px;
    max-width: 1280px;
    margin: 0 auto;
}}
.section-header {{
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 24px;
}}
.section-title {{
    font-family: 'Bebas Neue', cursive;
    font-size: 1.5rem;
    letter-spacing: 2px;
    color: {C["text"]};
}}
.section-line {{
    flex: 1; height: 1px;
    background: linear-gradient(90deg, {C["card_b"]}, transparent);
}}

/* Horizontal scroll row */
.movie-row {{
    display: flex;
    gap: 14px;
    overflow-x: auto;
    padding-bottom: 8px;
    scroll-snap-type: x mandatory;
    -ms-overflow-style: none;
    scrollbar-width: none;
}}
.movie-row::-webkit-scrollbar {{ display: none; }}

.movie-card {{
    flex: 0 0 160px;
    background: {C["card"]};
    border: 1px solid {C["card_b"]};
    border-radius: 12px;
    padding: 20px 14px 16px;
    text-align: center;
    scroll-snap-align: start;
    transition: all 0.25s cubic-bezier(.34,1.56,.64,1);
    cursor: default;
    position: relative;
    overflow: hidden;
}}
.movie-card::after {{
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, {C["accent"]}08, transparent);
    opacity: 0; transition: opacity 0.25s;
}}
.movie-card:hover {{
    transform: translateY(-6px) scale(1.03);
    border-color: {C["accent"]}66;
    box-shadow: 0 16px 40px {C["glow"]};
}}
.movie-card:hover::after {{ opacity: 1; }}
.card-emoji {{
    font-size: 2.2rem;
    display: block;
    margin-bottom: 12px;
    line-height: 1;
}}
.card-title {{
    font-size: 0.82rem;
    font-weight: 600;
    color: {C["text"]};
    margin-bottom: 4px;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.card-meta {{
    font-size: 0.68rem;
    color: {C["text_dim"]};
    margin-bottom: 10px;
}}
.card-rating {{
    display: inline-flex; align-items: center; gap: 4px;
    background: {C["badge_bg"]};
    color: {C["star"]};
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.68rem;
    font-weight: 600;
}}

/* ── RESULTS SECTION ─────────────────────────────────────────────── */
.results-header {{
    text-align: center;
    padding: 48px 40px 32px;
}}
.results-label {{
    font-size: 0.72rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {C["accent"]};
    margin-bottom: 10px;
}}
.results-title {{
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(2rem, 5vw, 3.5rem);
    letter-spacing: 2px;
    color: {C["text"]};
    line-height: 1;
}}
.results-title .red {{ color: {C["accent"]}; }}

.rec-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
    gap: 18px;
    padding: 0 40px 64px;
    max-width: 1280px;
    margin: 0 auto;
}}
.rec-card {{
    background: {C["card"]};
    border: 1px solid {C["card_b"]};
    border-radius: 14px;
    padding: 24px 16px 20px;
    text-align: center;
    transition: all 0.25s cubic-bezier(.34,1.56,.64,1);
    position: relative;
    overflow: hidden;
    animation: popIn 0.4s ease both;
}}
.rec-card:nth-child(1) {{ animation-delay: 0.05s; }}
.rec-card:nth-child(2) {{ animation-delay: 0.10s; }}
.rec-card:nth-child(3) {{ animation-delay: 0.15s; }}
.rec-card:nth-child(4) {{ animation-delay: 0.20s; }}
.rec-card:nth-child(5) {{ animation-delay: 0.25s; }}
.rec-card:nth-child(6) {{ animation-delay: 0.30s; }}
.rec-card:nth-child(7) {{ animation-delay: 0.35s; }}
.rec-card:nth-child(8) {{ animation-delay: 0.40s; }}
.rec-card::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, {C["accent"]}, {C["accent2"]});
}}
.rec-card:hover {{
    transform: translateY(-7px) scale(1.02);
    border-color: {C["accent"]}55;
    box-shadow: 0 18px 44px {C["glow"]};
}}
.rec-icon {{
    width: 64px; height: 64px; border-radius: 50%;
    background: {C["badge_bg"]};
    border: 2px solid {C["card_b"]};
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    margin: 0 auto 14px;
}}
.rec-num {{
    font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase;
    color: {C["text_dim"]}; margin-bottom: 6px;
}}
.rec-title {{
    font-size: 0.9rem; font-weight: 600;
    color: {C["text"]}; line-height: 1.35; margin-bottom: 8px;
}}
.rec-badge {{
    display: inline-block;
    background: {C["accent"]}1a;
    color: {C["accent"]};
    border: 1px solid {C["accent"]}33;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.65rem; font-weight: 500; letter-spacing: 0.5px;
}}

/* ── ERROR BOX ───────────────────────────────────────────────────── */
.error-box {{
    max-width: 440px; margin: 48px auto;
    background: {C["badge_bg"]};
    border: 1px solid {C["accent"]}44;
    border-radius: 14px;
    padding: 22px 28px;
    text-align: center;
    color: {C["text"]};
    font-size: 0.9rem;
    line-height: 1.5;
}}
.error-box span {{ color: {C["accent"]}; font-weight: 600; }}

/* ── NAVBAR SPACER ───────────────────────────────────────────────── */
.spacer {{ height: 60px; }}

/* ── ANIMATIONS ─────────────────────────────────────────────────── */
@keyframes popIn {{
    from {{ opacity: 0; transform: scale(0.92) translateY(16px); }}
    to   {{ opacity: 1; transform: scale(1)    translateY(0); }}
}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NAVBAR  (pure HTML logo + links, Streamlit widgets for search + toggle)
# We render the HTML nav separately, then absolutely position the Streamlit
# widget row to sit inside it using CSS trickery.
# ─────────────────────────────────────────────────────────────────────────────

# Fixed navbar HTML (logo + links only — no interactive widgets here)
st.markdown(f"""
<div class="navbar">
    <div class="nav-logo">🎬 MovieTime</div>
    <div class="nav-links">
        <span>Discover</span>
        <span>Trending</span>
        <span>Watchlist</span>
    </div>
    <!-- right side widgets injected via Streamlit below -->
</div>
""", unsafe_allow_html=True)

# # Streamlit widget row → pinned to top-right via CSS
# st.markdown("""
# <style>
# /* Target the FIRST stHorizontalBlock after the navbar markdown — pin it to navbar */
# section.main > div > div:nth-child(2) [data-testid="stHorizontalBlock"] {
#     position: fixed !important;
#     top: 11px !important;
#     right: 32px !important;
#     z-index: 99999 !important;
#     width: auto !important;
#     gap: 8px !important;
#     align-items: center !important;
#     background: transparent !important;
# }
# section.main > div > div:nth-child(2) [data-testid="stHorizontalBlock"] > div {
#     flex: none !important;
#     width: auto !important;
#     min-width: 0 !important;st
# }
# /* Make the input column wider */
# section.main > div > div:nth-child(2) [data-testid="stHorizontalBlock"] > div:first-child {
#     width: 260px !important;
# }
# </style>
# """, unsafe_allow_html=True)

# The actual interactive widgets
nav_input_col, nav_btn_col, nav_toggle_col = st.columns([6, 2, 1])

with nav_input_col:
    movie_input = st.text_input(
        "search",
        placeholder="🔍  Search a movie...",
        label_visibility="collapsed",
        key="movie_search_input",
        value=st.session_state.get("query", "")
    )

with nav_btn_col:
    st.markdown('<div class="search-btn">', unsafe_allow_html=True)
    search_clicked = st.button("Search", use_container_width=True, key="search_btn")
    st.markdown('</div>', unsafe_allow_html=True)

with nav_toggle_col:
    st.markdown('<div class="theme-btn">', unsafe_allow_html=True)
    icon = "☀️" if st.session_state.dark_mode else "🌙"
    if st.button(icon, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# # ── Handle search logic ───────────────────────────────────────────────────────
# # Also trigger on Enter key (Streamlit fires a rerun when input changes + button)
# trigger_search = search_clicked or (
#     movie_input.strip() != "" and
#     movie_input.strip() != st.session_state.query and
#     search_clicked
# )

if search_clicked:
    if movie_input.strip():
        st.session_state.query = movie_input.strip()
        if HAS_MODEL:
            recs = recommend_movies(movie_input.strip())
            if recs:
                st.session_state.recommendations = recs
                st.session_state.error_msg = ""
            else:
                st.session_state.recommendations = []
                st.session_state.error_msg = f'No results found for "{movie_input.strip()}". Try a different title.'
        else:
            st.session_state.recommendations = [
                "The Dark Knight", "Inception", "Interstellar",
                "Parasite", "Whiplash", "Dune", "Oppenheimer", "Get Out"
            ]
            st.session_state.error_msg = ""
        st.session_state.searched = True
    else:
        st.session_state.error_msg = "Please type a movie name to search."
        st.session_state.recommendations = []
        st.session_state.searched = True

# ── RENDER PAGE BODY ──────────────────────────────────────────────────────────

if not st.session_state.searched:
    # ── Landing: hero + trending cards ───────────────────────────────────────
    st.markdown(f"""
    <div class="navbar">
        <div class="nav-logo">🎬 MovieTime</div>
        <div class="nav-links">
            <span>Discover</span>
            <span>Trending</span>
            <span>Watchlist</span>
        </div>
    </div>
    <div class="spacer"></div>
    """, unsafe_allow_html=True)

    # Trending row
    cards_html = ""
    for m in get_trending():
        cards_html += f"""
        <div class="movie-card">
            <span class="card-emoji">{m['emoji']}</span>
            <div class="card-title">{m['title']}</div>
            <div class="card-meta">{m['genre']} · {m['year']}</div>
            <div class="card-rating">⭐ {m['rating']}</div>
        </div>"""

    st.markdown(f"""
    <div class="section">
        <div class="section-header">
            <div class="section-title">TRENDING NOW</div>
            <div class="section-line"></div>
        </div>
        <div class="movie-row">{cards_html}</div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.error_msg:
    # ── Error state ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="error-box">
        <span>⚠ {st.session_state.error_msg}</span><br>
        <span style="font-size:0.82rem;color:{C['text_dim']};font-weight:400;">
        Try titles like: Inception, Parasite, The Dark Knight
        </span>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Results ───────────────────────────────────────────────────────────────
    query_display = st.session_state.query

    st.markdown(f"""
    <div class="results-header">
        <div class="results-label">Because you searched for</div>
        <div class="results-title"><span class="red">{query_display}</span></div>
    </div>
    """, unsafe_allow_html=True)

    recs = st.session_state.recommendations
    cards_html = ""
    ordinals = ["1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th",
                "11th","12th","13th","14th","15th"]

    for i, movie in enumerate(recs):
        emoji = MOVIE_EMOJIS[i % len(MOVIE_EMOJIS)]
        num   = ordinals[i] if i < len(ordinals) else f"#{i+1}"
        if isinstance(movie, dict):
            title = movie.get("title", str(movie))
            badge = movie.get("genre", "Similar Pick")
        else:
            title = str(movie)
            badge = "Similar Pick"

        cards_html += f"""
        <div class="rec-card">
            <div class="rec-num">{num} pick</div>
            <div class="rec-icon">{emoji}</div>
            <div class="rec-title">{title}</div>
            <span class="rec-badge">{badge}</span>
        </div>"""

    st.markdown(f'<div class="rec-grid">{cards_html}</div>', unsafe_allow_html=True)

    # Back / search again hint
    st.markdown(f"""
    <div style="text-align:center; padding: 0 0 48px; color:{C['text_dim']}; font-size:0.82rem;">
        Use the search bar above to explore more movies
    </div>
    """, unsafe_allow_html=True)