import streamlit as st
import requests, time
import pandas as pd
import plotly.graph_objects as go

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="SmartHome — Energy Management",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Palette
   bg:        #0d1117   (near-black slate)
   surface:   #161b22   (card background)
   border:    #21262d   (subtle borders)
   accent:    #2dd4bf   (teal)
   accent2:   #0d9488   (teal darker)
   text:      #e6edf3   (primary text)
   muted:     #7d8590   (secondary text)
   green:     #3fb950
   amber:     #d29922
   red:       #f85149
── */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
[data-testid="stAppViewContainer"] {
    background: #0d1117;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #7d8590 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.88rem;
    padding: 5px 0;
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #2dd4bf !important; }

/* ── Main content ── */
.block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
    background: #0d1117;
}

/* ── Page header ── */
.page-header {
    border-bottom: 1px solid #21262d;
    padding-bottom: 14px;
    margin-bottom: 24px;
}
.page-header h2 {
    font-size: 1.45rem;
    font-weight: 700;
    color: #e6edf3;
    margin: 0;
    letter-spacing: -0.02em;
}
.page-header p {
    font-size: 0.82rem;
    color: #7d8590;
    margin: 5px 0 0 0;
}

/* ── Section label ── */
.section-title {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #2dd4bf;
    margin: 28px 0 12px 0;
    border-left: 3px solid #2dd4bf;
    padding-left: 8px;
}

/* ── Floor plan ── */
.floorplan-wrap {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 24px;
}
.compass {
    text-align: center;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: #2dd4bf;
    margin-bottom: 8px;
}
.wall { background: #30363d; }
.room-cell {
    background: #0d1117;
    border: 1.5px solid #21262d;
    padding: 12px 8px;
    text-align: center;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 4px;
    transition: border-color 0.2s, background 0.2s;
}
.room-cell:hover { border-color: #2dd4bf; background: #0d1f1e; }
.room-cell.warn  { border-color: #d29922; background: #1a1500; }
.room-cell.alert { border-color: #f85149; background: #1a0a0a; }
.room-name  { font-size: 0.78rem; font-weight: 700; color: #e6edf3; }
.room-temp  { font-size: 0.72rem; color: #7d8590; }
.room-power { font-size: 0.72rem; font-weight: 600; }
.room-apps  { font-size: 0.65rem; color: #484f58; }
.entrance-gap {
    width: 56px; height: 5px;
    background: #0d1117;
    border-bottom: 2px dashed #2dd4bf;
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.badge-on  { background: rgba(63,185,80,0.15);  color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
.badge-off { background: rgba(248,81,73,0.12);  color: #f85149; border: 1px solid rgba(248,81,73,0.3); }

/* ── Alert boxes ── */
.alert-box {
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.84rem;
    font-weight: 500;
    margin-top: 8px;
    line-height: 1.5;
}
.alert-danger  { background: rgba(248,81,73,0.1);  border: 1px solid rgba(248,81,73,0.35);  color: #ffa198; }
.alert-warning { background: rgba(210,153,34,0.1); border: 1px solid rgba(210,153,34,0.35); color: #e3b341; }
.alert-info    { background: rgba(45,212,191,0.08);border: 1px solid rgba(45,212,191,0.3);  color: #2dd4bf; }
.alert-success { background: rgba(63,185,80,0.1);  border: 1px solid rgba(63,185,80,0.3);   color: #3fb950; }

/* ── Level badge ── */
.level-badge {
    display: inline-block;
    padding: 6px 22px;
    border-radius: 6px;
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}
.level-low    { background: rgba(63,185,80,0.15);  color: #3fb950; }
.level-normal { background: rgba(45,212,191,0.12); color: #2dd4bf; }
.level-high   { background: rgba(248,81,73,0.15);  color: #f85149; }

/* ── Auth card ── */
.auth-wrap {
    max-width: 420px;
    margin: 60px auto 0 auto;
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 14px;
    padding: 36px 40px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.auth-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #e6edf3;
    text-align: center;
    margin-bottom: 4px;
}
.auth-sub {
    font-size: 0.8rem;
    color: #7d8590;
    text-align: center;
    margin-bottom: 28px;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    font-size: 1rem;
    font-weight: 700;
    color: #2dd4bf !important;
    letter-spacing: -0.01em;
    padding: 8px 0 2px 0;
}
.sidebar-user {
    font-size: 0.75rem;
    color: #484f58 !important;
    margin-bottom: 16px;
}

/* ── Streamlit overrides ── */
.stButton > button {
    background: #0d9488;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 10px 20px;
    transition: background 0.2s;
}
.stButton > button:hover { background: #0f766e; }

div[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    color: #7d8590 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    color: #e6edf3 !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

.stDataFrame { border-radius: 8px; overflow: hidden; }
.stDataFrame thead tr th {
    background: #161b22 !important;
    color: #7d8590 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.stDataFrame tbody tr td { color: #c9d1d9 !important; font-size: 0.84rem !important; }
.stDataFrame tbody tr:hover td { background: #1c2128 !important; }

.stExpander {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
}
.stExpander summary { color: #c9d1d9 !important; font-weight: 600; }

.stMultiSelect [data-baseweb="tag"] {
    background: rgba(45,212,191,0.15) !important;
    color: #2dd4bf !important;
}
.stTabs [data-baseweb="tab"] { color: #7d8590 !important; }
.stTabs [aria-selected="true"] { color: #2dd4bf !important; border-bottom-color: #2dd4bf !important; }

input, textarea, select {
    background: #0d1117 !important;
    color: #e6edf3 !important;
    border-color: #21262d !important;
}
</style>
"""

# ── Session state ─────────────────────────────────────────────────────────────
for key, val in [("logged_in", False), ("username", ""), ("history", [])]:
    if key not in st.session_state:
        st.session_state[key] = val


# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_snapshot():
    try:
        r = requests.get(f"{API}/generate", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def power_color(w):
    if w > 6000: return "#f85149"
    if w > 3000: return "#d29922"
    return "#3fb950"

def temp_color(t):
    if t > 30: return "#f85149"
    if t > 27: return "#d29922"
    return "#3fb950"

def room_class(p):
    if p > 6000: return "alert"
    if p > 3000: return "warn"
    return ""

def inject_style():
    st.markdown(STYLE, unsafe_allow_html=True)

def page_header(title, subtitle=""):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="page-header">
      <h2>{title}</h2>
      {sub}
    </div>""", unsafe_allow_html=True)

def section(label):
    st.markdown(f'<div class="section-title">{label}</div>', unsafe_allow_html=True)


# ── Auth page ─────────────────────────────────────────────────────────────────
def auth_page():
    inject_style()
    st.markdown("""
    <div class="auth-wrap">
      <div class="auth-title">SmartHome Platform</div>
      <div class="auth-sub">AI-Driven Energy Management &amp; Digital Twin</div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                uname = st.text_input("Username")
                pwd   = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                if not uname or not pwd:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        r = requests.post(f"{API}/login",
                            json={"username": uname, "password": pwd}, timeout=5)
                        if r.status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.username  = uname
                            st.rerun()
                        elif r.status_code == 401:
                            st.error("Invalid credentials. Please create an account if you are new.")
                        else:
                            st.error(r.json().get("detail", "Login failed."))
                    except Exception:
                        st.error("Cannot reach backend. Ensure the API server is running.")

        with tab_signup:
            with st.form("signup_form"):
                new_uname = st.text_input("Username")
                new_pwd   = st.text_input("Password", type="password")
                new_pwd2  = st.text_input("Confirm Password", type="password")
                submitted2 = st.form_submit_button("Create Account", use_container_width=True)
            if submitted2:
                if not new_uname or not new_pwd:
                    st.error("Please fill in all fields.")
                elif new_pwd != new_pwd2:
                    st.error("Passwords do not match.")
                else:
                    try:
                        r = requests.post(f"{API}/signup",
                            json={"username": new_uname, "password": new_pwd}, timeout=5)
                        if r.status_code == 200:
                            st.success("Account created. Please sign in.")
                        else:
                            st.error(r.json().get("detail", "Signup failed."))
                    except Exception:
                        st.error("Cannot reach backend.")


# ── Page 1: Digital Twin ──────────────────────────────────────────────────────
def page_digital_twin():
    inject_style()
    page_header("Digital Twin", "Real-time floor plan with live sensor data")

    snap = fetch_snapshot()
    if not snap:
        st.error("Backend unreachable. Start the FastAPI server and refresh.")
        return

    rooms = snap["rooms"]
    total = snap["total_power"]
    st.session_state.history.append(total)
    if len(st.session_state.history) > 60:
        st.session_state.history = st.session_state.history[-60:]

    # KPI row
    lr_temp = rooms["Living Room"]["temperature"]
    apps_on = sum(
        1 for r in rooms.values()
        for a in r["appliances"].values() if a["is_on"]
    )
    total_apps = sum(len(r["appliances"]) for r in rooms.values())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Power", f"{total:.0f} W")
    c2.metric("Living Room Temp", f"{lr_temp} °C")
    c3.metric("Appliances Active", f"{apps_on} / {total_apps}")
    c4.metric("Logged In As", st.session_state.username)

    section("FLOOR PLAN — NORTH ENTRANCE")

    # SVG icons for each room (inline, 28x28, stroke-based)
    ROOM_ICONS = {
        "Living Room": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/></svg>',
        "Bedroom 1":   '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5"><path d="M2 9h20v11H2z"/><path d="M2 9V7a2 2 0 012-2h16a2 2 0 012 2v2"/><path d="M12 9V5"/><circle cx="7" cy="14" r="1.5"/><circle cx="17" cy="14" r="1.5"/></svg>',
        "Bedroom 2":   '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5"><path d="M2 9h20v11H2z"/><path d="M2 9V7a2 2 0 012-2h16a2 2 0 012 2v2"/><path d="M12 9V5"/><circle cx="7" cy="14" r="1.5"/><circle cx="17" cy="14" r="1.5"/></svg>',
        "Kitchen":     '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 9h20"/><circle cx="7" cy="6" r="1"/><circle cx="12" cy="6" r="1"/></svg>',
        "Washroom":    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5"><path d="M4 12h16v4a4 4 0 01-4 4H8a4 4 0 01-4-4v-4z"/><path d="M4 12V6a2 2 0 012-2h1a2 2 0 012 2v6"/><path d="M20 12V8"/></svg>',
        "Utility":     '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="12" cy="12" r="4"/><path d="M12 8v1M12 15v1M8 12h1M15 12h1"/></svg>',
    }

    # Appliance mini-icons (tiny SVG dots per appliance type)
    def appliance_dots(appliances):
        dots = []
        for app, adata in appliances.items():
            color = "#3fb950" if adata["is_on"] else "#30363d"
            dots.append(f'<span title="{app}" style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{color};margin:1px"></span>')
        return "".join(dots)

    def room_cell(key, label, data):
        t   = data["temperature"]
        p   = data["total_power"]
        tc  = temp_color(t)
        pc  = power_color(p)
        rc  = room_class(p)
        on  = sum(1 for a in data["appliances"].values() if a["is_on"])
        tot = len(data["appliances"])
        icon = ROOM_ICONS.get(label, "")
        dots = appliance_dots(data["appliances"])
        return f"""<div class="room-cell {rc}">
          <div style="margin-bottom:4px">{icon}</div>
          <div class="room-name">{label}</div>
          <div class="room-temp" style="color:{tc}">&#x1F321; {t} °C</div>
          <div class="room-power" style="color:{pc}">&#x26A1; {p:.0f} W</div>
          <div style="margin-top:5px">{dots}</div>
          <div class="room-apps">{on}/{tot} appliances on</div>
        </div>"""

    fp = f"""
    <div class="floorplan-wrap">
      <div class="compass">N  (ENTRANCE)</div>
      <div style="display:flex;align-items:center;margin-bottom:0">
        <div style="flex:1;height:5px" class="wall"></div>
        <div class="entrance-gap"></div>
        <div style="flex:1;height:5px" class="wall"></div>
      </div>
      <div style="display:flex">
        <div style="width:5px" class="wall"></div>
        <div style="flex:1">{room_cell("lr",  "Living Room", rooms["Living Room"])}</div>
        <div style="width:5px" class="wall"></div>
      </div>
      <div style="display:flex">
        <div style="width:5px" class="wall"></div>
        <div style="flex:2;height:5px" class="wall"></div>
        <div style="width:40px;height:5px;background:#0d1117"></div>
        <div style="flex:3;height:5px" class="wall"></div>
        <div style="width:5px" class="wall"></div>
      </div>
      <div style="display:flex">
        <div style="width:5px" class="wall"></div>
        <div style="flex:1">{room_cell("b1",  "Bedroom 1",  rooms["Bedroom 1"])}</div>
        <div style="width:5px" class="wall"></div>
        <div style="flex:1">{room_cell("b2",  "Bedroom 2",  rooms["Bedroom 2"])}</div>
        <div style="width:5px" class="wall"></div>
        <div style="flex:1">{room_cell("kit", "Kitchen",    rooms["Kitchen"])}</div>
        <div style="width:5px" class="wall"></div>
        <div style="flex:1">{room_cell("wsh", "Washroom",   rooms["Washroom"])}</div>
        <div style="width:5px" class="wall"></div>
        <div style="flex:1">{room_cell("utl", "Utility",    rooms["Utility"])}</div>
        <div style="width:5px" class="wall"></div>
      </div>
      <div style="height:5px" class="wall"></div>
      <div class="compass" style="margin-top:6px">S</div>
    </div>"""
    st.markdown(fp, unsafe_allow_html=True)

    section("ROOM DETAILS")

    # Appliance SVG icons
    APP_ICONS = {
        "AC":              '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="20" height="10" rx="2"/><path d="M6 16v3M18 16v3M8 11h8"/></svg>',
        "TV":              '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 20h8M12 18v2"/></svg>',
        "Iron Box":        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 17h18l-3-8H6L3 17z"/><path d="M6 17v2"/><path d="M18 17v2"/></svg>',
        "Lights":          '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 18h6M10 22h4M12 2a7 7 0 017 7c0 2.5-1.3 4.7-3.3 6H8.3A7 7 0 0112 2z"/></svg>',
        "Fridge":          '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M5 10h14"/><path d="M10 6v2M10 14v3"/></svg>',
        "Grinder":         '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3h8l2 6H6L8 3z"/><rect x="6" y="9" width="12" height="12" rx="2"/><circle cx="12" cy="15" r="2"/></svg>',
        "Mixer":           '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3h8l2 6H6L8 3z"/><rect x="6" y="9" width="12" height="12" rx="2"/><path d="M9 15h6"/></svg>',
        "Microwave":       '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="5" width="20" height="14" rx="2"/><rect x="5" y="8" width="11" height="8" rx="1"/><circle cx="19" cy="12" r="1"/></svg>',
        "Geyser":          '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="7" y="2" width="10" height="16" rx="2"/><path d="M10 18v4M14 18v4"/><path d="M10 8a2 2 0 004 0"/></svg>',
        "Washing Machine": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="2" width="18" height="20" rx="2"/><circle cx="12" cy="13" r="4"/><path d="M6 6h2"/></svg>',
    }

    for rname, rdata in rooms.items():
        with st.expander(f"{rname}  —  {rdata['total_power']:.0f} W  |  {rdata['temperature']} °C"):
            cols = st.columns(min(len(rdata["appliances"]), 5))
            for i, (app, adata) in enumerate(rdata["appliances"].items()):
                with cols[i % len(cols)]:
                    icon_svg = APP_ICONS.get(app, '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/></svg>')
                    icon_color = "#2dd4bf" if adata["is_on"] else "#484f58"
                    badge_cls  = "badge-on" if adata["is_on"] else "badge-off"
                    badge_txt  = "ON" if adata["is_on"] else "OFF"
                    pw_color   = "#2dd4bf" if adata["is_on"] else "#484f58"
                    st.markdown(f"""
                    <div style="background:#161b22;border:1px solid {'#2dd4bf44' if adata['is_on'] else '#21262d'};
                                border-radius:10px;padding:14px 10px;text-align:center;margin-bottom:6px">
                      <div style="color:{icon_color};margin-bottom:8px">{icon_svg}</div>
                      <div style="font-size:0.78rem;font-weight:600;color:#e6edf3;margin-bottom:6px">{app}</div>
                      <span class="badge {badge_cls}">{badge_txt}</span>
                      <div style="font-size:0.88rem;font-weight:700;color:{pw_color};margin-top:8px">{adata['power_w']:.0f} W</div>
                      <div style="font-size:0.62rem;color:#484f58;margin-top:3px">{adata['type'].capitalize()}</div>
                    </div>""", unsafe_allow_html=True)


# ── Page 2: Appliance Monitoring with toggles ────────────────────────────────
def page_appliance_monitoring():
    inject_style()
    page_header("Appliance Monitoring", "Visual appliance controls — toggle ON / OFF in real time")

    snap = fetch_snapshot()
    if not snap:
        st.error("Backend unreachable.")
        return

    rooms = snap["rooms"]
    total = snap["total_power"]

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total House Power", f"{total:.0f} W")
    apps_on = sum(1 for r in rooms.values() for a in r["appliances"].values() if a["is_on"])
    total_apps = sum(len(r["appliances"]) for r in rooms.values())
    c2.metric("Appliances Running", f"{apps_on} / {total_apps}")
    status = "High Load" if total > 6000 else "Normal" if total > 2000 else "Low Load"
    c3.metric("Load Status", status)
    # Monthly estimate: assume 8h/day average usage
    monthly_kwh = round(total / 1000 * 8 * 30, 1)
    c4.metric("Est. Monthly Usage", f"{monthly_kwh} kWh")

    # ── Phone number + SMS controls ───────────────────────────────────────────
    section("SMS ALERT SETTINGS")
    if "phone_number" not in st.session_state:
        st.session_state.phone_number = ""

    ph_col1, ph_col2, ph_col3 = st.columns([2, 1, 1])
    with ph_col1:
        phone = st.text_input(
            "Your mobile number (E.164 format)",
            value=st.session_state.phone_number,
            placeholder="+919876543210",
            help="Include country code. Example: +919876543210 for India, +14155552671 for US"
        )
        st.session_state.phone_number = phone

    with ph_col2:
        if st.button("Send Test SMS", use_container_width=True):
            if not phone:
                st.error("Enter a phone number first.")
            else:
                try:
                    r = requests.post(f"{API}/notify/test", json={"phone_number": phone}, timeout=10)
                    res = r.json()
                    if res.get("status") == "sent":
                        st.success(f"Test SMS sent! SID: {res.get('sid','')[:12]}...")
                    elif res.get("status") == "skipped":
                        st.warning("Twilio not configured. Add credentials to backend/.env")
                    else:
                        st.error(f"Failed: {res.get('reason','Unknown error')}")
                except Exception as e:
                    st.error(str(e))

    with ph_col3:
        if st.button("Check & Alert Now", use_container_width=True):
            if not phone:
                st.error("Enter a phone number first.")
            else:
                try:
                    r = requests.post(f"{API}/notify/check", json={"phone_number": phone}, timeout=10)
                    res = r.json()
                    n = res.get("alerts_triggered", 0)
                    if n == 0:
                        st.success("No alerts — all systems normal.")
                    else:
                        st.warning(f"{n} alert(s) sent to {phone}")
                except Exception as e:
                    st.error(str(e))

    # Twilio config status
    try:
        sr = requests.get(f"{API}/notify/status", timeout=3)
        if sr.status_code == 200:
            cfg = sr.json()
            if cfg["configured"]:
                st.markdown(f'<div class="alert-box alert-success">Twilio configured — sending from {cfg["from_number"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-warning">Twilio not configured. Open <code>backend/.env</code> and fill in your Account SID, Auth Token, and Twilio phone number.</div>', unsafe_allow_html=True)
    except Exception:
        pass

    # ── Notifications / Alerts ────────────────────────────────────────────────
    section("LIVE NOTIFICATIONS")
    alerts = []

    # Overheat check
    for rname, rdata in rooms.items():
        if rdata["temperature"] > 30:
            alerts.append(("danger", f"OVERHEAT — {rname} temperature is {rdata['temperature']} °C. Check AC or ventilation."))
        elif rdata["temperature"] > 27:
            alerts.append(("warning", f"HIGH TEMP — {rname} is at {rdata['temperature']} °C."))

    # High power check
    if total > 6000:
        alerts.append(("danger", f"OVERLOAD — Total power {total:.0f} W exceeds safe limit (6000 W). Turn off non-essential appliances."))
    elif total > 4000:
        alerts.append(("warning", f"HIGH LOAD — Total power {total:.0f} W is elevated."))

    # Appliances left on check (occasional appliances running)
    for rname, rdata in rooms.items():
        for app, adata in rdata["appliances"].items():
            if adata["is_on"] and adata["type"] == "occasional":
                alerts.append(("warning", f"LEFT ON — {app} in {rname} is still running ({adata['power_w']:.0f} W)."))

    if not alerts:
        st.markdown('<div class="alert-box alert-success">All systems normal. No alerts at this time.</div>', unsafe_allow_html=True)
    else:
        for atype, msg in alerts[:6]:  # cap at 6
            st.markdown(f'<div class="alert-box alert-{atype}">{msg}</div>', unsafe_allow_html=True)

    # ── Energy Budget ─────────────────────────────────────────────────────────
    section("MONTHLY ENERGY BUDGET")
    if "monthly_budget_kwh" not in st.session_state:
        st.session_state.monthly_budget_kwh = 300.0

    col_b1, col_b2 = st.columns([2, 3])
    with col_b1:
        budget = st.number_input(
            "Set your monthly budget (kWh)",
            min_value=50.0, max_value=2000.0,
            value=st.session_state.monthly_budget_kwh,
            step=10.0,
            help="Based on current usage, we estimate your monthly consumption."
        )
        st.session_state.monthly_budget_kwh = budget

    with col_b2:
        pct = min(monthly_kwh / budget * 100, 100) if budget > 0 else 0
        bar_color = "#f85149" if pct > 90 else "#d29922" if pct > 70 else "#3fb950"
        st.markdown(f"""
        <div style="margin-top:8px">
          <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="font-size:0.8rem;color:#7d8590">Estimated usage this month</span>
            <span style="font-size:0.8rem;font-weight:700;color:{bar_color}">{monthly_kwh} / {budget:.0f} kWh ({pct:.1f}%)</span>
          </div>
          <div style="background:#21262d;border-radius:6px;height:10px;overflow:hidden">
            <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:6px;transition:width 0.4s"></div>
          </div>
          {'<div class="alert-box alert-danger" style="margin-top:10px">Budget exceeded! Reduce usage to stay within limit.</div>' if pct >= 100 else
           '<div class="alert-box alert-warning" style="margin-top:10px">Approaching budget limit. Consider reducing usage.</div>' if pct > 70 else
           '<div class="alert-box alert-success" style="margin-top:10px">Usage is within budget.</div>'}
        </div>""", unsafe_allow_html=True)

    # ── Appliance cards with ON/OFF toggles ───────────────────────────────────
    section("APPLIANCE CONTROLS")

    APP_ICONS = {
        "AC":              '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="20" height="10" rx="2"/><path d="M6 16v3M18 16v3M8 11h8"/></svg>',
        "TV":              '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 20h8M12 18v2"/></svg>',
        "Iron Box":        '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 17h18l-3-8H6L3 17z"/><path d="M6 17v2M18 17v2"/></svg>',
        "Lights":          '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 18h6M10 22h4M12 2a7 7 0 017 7c0 2.5-1.3 4.7-3.3 6H8.3A7 7 0 0112 2z"/></svg>',
        "Fridge":          '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M5 10h14M10 6v2M10 14v3"/></svg>',
        "Grinder":         '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3h8l2 6H6L8 3z"/><rect x="6" y="9" width="12" height="12" rx="2"/><circle cx="12" cy="15" r="2"/></svg>',
        "Mixer":           '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3h8l2 6H6L8 3z"/><rect x="6" y="9" width="12" height="12" rx="2"/><path d="M9 15h6"/></svg>',
        "Microwave":       '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="5" width="20" height="14" rx="2"/><rect x="5" y="8" width="11" height="8" rx="1"/><circle cx="19" cy="12" r="1"/></svg>',
        "Geyser":          '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="7" y="2" width="10" height="16" rx="2"/><path d="M10 18v4M14 18v4M10 8a2 2 0 004 0"/></svg>',
        "Washing Machine": '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="2" width="18" height="20" rx="2"/><circle cx="12" cy="13" r="4"/><path d="M6 6h2"/></svg>',
    }
    DEFAULT_ICON = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 8v4l3 3"/></svg>'

    for rname, rdata in rooms.items():
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid #21262d;border-radius:12px;
                    padding:18px 20px;margin-bottom:20px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <div style="font-size:0.95rem;font-weight:700;color:#e6edf3">{rname}</div>
            <div style="font-size:0.78rem;color:#7d8590">
              {rdata['total_power']:.0f} W &nbsp;·&nbsp; {rdata['temperature']} °C
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        n_apps = len(rdata["appliances"])
        cols = st.columns(min(n_apps, 5))

        for i, (app_name, adata) in enumerate(rdata["appliances"].items()):
            with cols[i % min(n_apps, 5)]:
                is_on     = adata["is_on"]
                icon_svg  = APP_ICONS.get(app_name, DEFAULT_ICON)
                icon_col  = "#2dd4bf" if is_on else "#484f58"
                card_bdr  = "#2dd4bf44" if is_on else "#21262d"
                pw_col    = "#2dd4bf" if is_on else "#484f58"

                # Visual card
                st.markdown(f"""
                <div style="background:#0d1117;border:1.5px solid {card_bdr};border-radius:10px;
                            padding:14px 8px;text-align:center;margin-bottom:4px">
                  <div style="color:{icon_col};margin-bottom:8px">{icon_svg}</div>
                  <div style="font-size:0.78rem;font-weight:600;color:#e6edf3;margin-bottom:4px">{app_name}</div>
                  <div style="font-size:0.85rem;font-weight:700;color:{pw_col}">{adata['power_w']:.0f} W</div>
                  <div style="font-size:0.62rem;color:#484f58;margin-top:3px">{adata['type'].capitalize()}</div>
                </div>""", unsafe_allow_html=True)

                # Toggle button
                btn_label = "Turn OFF" if is_on else "Turn ON"
                btn_key   = f"toggle_{rname}_{app_name}"
                if st.button(btn_label, key=btn_key, use_container_width=True):
                    try:
                        requests.post(f"{API}/toggle", json={
                            "room": rname,
                            "appliance": app_name,
                            "is_on": not is_on
                        }, timeout=5)
                        st.rerun()
                    except Exception:
                        st.error("Could not reach backend.")


# Page 3: Energy Analytics
def page_energy_analytics():
    inject_style()
    page_header("Energy Analytics", "Live power consumption trends and ML predictions")

    snap = fetch_snapshot()
    if not snap:
        st.error("Backend unreachable.")
        return

    total = snap["total_power"]
    st.session_state.history.append(total)
    if len(st.session_state.history) > 60:
        st.session_state.history = st.session_state.history[-60:]

    history = st.session_state.history
    times   = list(range(len(history)))

    section("TOTAL POWER — LIVE TREND")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=history, mode="lines",
        line=dict(color="#2dd4bf", width=2.5),
        name="Total Power (W)",
        fill="tozeroy", fillcolor="rgba(45,212,191,0.07)"
    ))
    fig.add_hline(y=6000, line_dash="dot", line_color="#f85149", line_width=1.5,
                  annotation_text="High (6000 W)", annotation_font_color="#f85149")
    fig.add_hline(y=2000, line_dash="dot", line_color="#3fb950", line_width=1.5,
                  annotation_text="Low (2000 W)", annotation_font_color="#3fb950")
    fig.update_layout(
        paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
        font=dict(color="#7d8590", family="Inter, sans-serif"),
        xaxis=dict(title="Reading", gridcolor="#21262d", showgrid=True, color="#7d8590"),
        yaxis=dict(title="Power (W)", gridcolor="#21262d", showgrid=True, color="#7d8590"),
        margin=dict(l=50, r=20, t=20, b=50),
        height=320,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    section("PER-ROOM BREAKDOWN")
    rooms       = snap["rooms"]
    room_names  = list(rooms.keys())
    room_powers = [rooms[r]["total_power"] for r in room_names]
    bar_colors  = [power_color(p) for p in room_powers]

    fig2 = go.Figure(go.Bar(
        x=room_names, y=room_powers,
        marker_color=bar_colors,
        text=[f"{p:.0f} W" for p in room_powers],
        textposition="outside",
        textfont=dict(size=11, color="#334155"),
    ))
    fig2.update_layout(
        paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
        font=dict(color="#7d8590", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#21262d", color="#7d8590"),
        yaxis=dict(title="Power (W)", gridcolor="#21262d", color="#7d8590"),
        margin=dict(l=50, r=20, t=10, b=50),
        height=260,
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

    section("ML PREDICTION")
    try:
        pr = requests.post(f"{API}/predict", json={"current_power": total}, timeout=5)
        if pr.status_code == 200:
            pd_data = pr.json()
            c1, c2 = st.columns(2)
            c1.metric("Predicted Next Reading", f"{pd_data['predicted_power']:.0f} W")
            anomaly_label = "Anomaly Detected" if pd_data["is_anomaly"] else "Normal Pattern"
            c2.metric("Anomaly Status", anomaly_label)
            if pd_data["is_anomaly"]:
                st.markdown('<div class="alert-box alert-warning">Unusual power pattern detected. Review appliance usage.</div>', unsafe_allow_html=True)
    except Exception:
        st.warning("ML prediction service unavailable.")


# Page 4: Simulation & Hazard
def page_simulation():
    inject_style()
    page_header("Simulation & Hazard Prediction", "What-if analysis, load advisory, and risk detection")

    snap = fetch_snapshot()
    if not snap:
        st.error("Backend unreachable.")
        return

    current_power = snap["total_power"]
    c1, c2 = st.columns(2)
    c1.metric("Current Total Power", f"{current_power:.0f} W")
    c2.metric("Baseline Status", "High" if current_power > 6000 else "Normal" if current_power > 2000 else "Low")

    section("WHAT-IF SIMULATION")
    EXTRA_OPTIONS = ["Iron Box","Washing Machine","Microwave","Geyser","Grinder","Mixer","Extra AC","Extra Heater"]
    selected = st.multiselect("Add appliances to simulate:", EXTRA_OPTIONS,
                              help="Select one or more appliances to see the projected impact on total load.")

    if st.button("Run Simulation", use_container_width=False):
        try:
            r = requests.post(f"{API}/simulate",
                json={"current_power": current_power, "extra_appliances": selected},
                timeout=5)
            if r.status_code == 200:
                res = r.json()

                section("SIMULATION RESULTS")
                r1, r2, r3 = st.columns(3)
                r1.metric("Simulated Total", f"{res['total_power']:.0f} W")
                r2.metric("Additional Load",  f"{res['extra_power']:.0f} W")

                level_cls = {"LOW": "level-low", "NORMAL": "level-normal", "HIGH": "level-high"}
                lc = level_cls.get(res["level"], "level-normal")
                r3.markdown(f'<div style="padding-top:8px"><span class="level-badge {lc}">{res["level"]}</span></div>',
                            unsafe_allow_html=True)

                section("ADVISORY")
                advice_cls = "alert-danger" if res["level"] == "HIGH" else "alert-info" if res["level"] == "NORMAL" else "alert-success"
                st.markdown(f'<div class="alert-box {advice_cls}">{res["advice"]}</div>', unsafe_allow_html=True)

                section("HAZARD & ANOMALY DETECTION")
                h1, h2, h3 = st.columns(3)
                with h1:
                    if res["hazard_risk"]:
                        st.markdown('<div class="alert-box alert-danger"><strong>Overload Risk</strong><br>Reduce load immediately.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-box alert-success">No overload risk detected.</div>', unsafe_allow_html=True)
                with h2:
                    if res["anomaly"]:
                        st.markdown('<div class="alert-box alert-warning"><strong>Anomaly Detected</strong><br>Unusual power pattern.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-box alert-success">No anomaly detected.</div>', unsafe_allow_html=True)
                with h3:
                    if res["fire_risk"]:
                        st.markdown('<div class="alert-box alert-danger"><strong>Fire / Overheat Risk</strong><br>Inspect appliances now.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-box alert-success">No fire or overheat risk.</div>', unsafe_allow_html=True)

                section("POWER GAUGE")
                lc_hex = {"LOW": "#3fb950", "NORMAL": "#2dd4bf", "HIGH": "#f85149"}.get(res["level"], "#2dd4bf")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=res["total_power"],
                    title={"text": "Simulated Load (W)", "font": {"color": "#7d8590", "size": 14}},
                    gauge={
                        "axis": {"range": [0, 10000], "tickcolor": "#484f58", "tickfont": {"color": "#484f58"}},
                        "bar":  {"color": lc_hex},
                        "bgcolor": "#0d1117",
                        "bordercolor": "#21262d",
                        "steps": [
                            {"range": [0, 2000],    "color": "rgba(63,185,80,0.12)"},
                            {"range": [2000, 6000],  "color": "rgba(45,212,191,0.08)"},
                            {"range": [6000, 10000], "color": "rgba(248,81,73,0.12)"},
                        ],
                        "threshold": {"line": {"color": "#f85149", "width": 3}, "value": 8000},
                    },
                    number={"font": {"color": "#e6edf3", "size": 28}},
                ))
                fig.update_layout(
                    paper_bgcolor="#161b22", font=dict(family="Inter, sans-serif"),
                    height=260, margin=dict(l=20, r=20, t=40, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Simulation error: {e}")

    section("MODEL MANAGEMENT")
    if st.button("Retrain ML Models with Latest Data"):
        try:
            r = requests.post(f"{API}/retrain", timeout=10)
            if r.status_code == 200:
                d = r.json()
                st.success(f"Models retrained successfully on {d.get('samples', '?')} samples.")
            else:
                st.error(r.json().get("detail", "Retrain failed."))
        except Exception as e:
            st.error(str(e))


# Main router
def main():
    if not st.session_state.logged_in:
        auth_page()
        return

    inject_style()

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">SmartHome Platform</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-user">Signed in as {st.session_state.username}</div>', unsafe_allow_html=True)
        st.markdown("---")
        page = st.radio(
            "Navigation",
            ["Digital Twin", "Appliance Monitoring", "Energy Analytics", "Simulation & Hazard"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.history   = []
            st.rerun()

    if page == "Digital Twin":
        page_digital_twin()
    elif page == "Appliance Monitoring":
        page_appliance_monitoring()
    elif page == "Energy Analytics":
        page_energy_analytics()
    elif page == "Simulation & Hazard":
        page_simulation()

    if auto_refresh and page != "Simulation & Hazard":
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()
