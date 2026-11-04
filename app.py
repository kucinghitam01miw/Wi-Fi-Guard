from __future__ import annotations

import streamlit as st

from modules.visualizer import (
    render_metric_card,
    render_section_heading,
    render_speed_gauge,
    render_status_card,
)

st.set_page_config(
    page_title="WiFi-Radar ID | Public Wi-Fi Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    :root { --bg:#080f1c; --panel:#101c2d; --panel2:#142238; --line:#23344b; --muted:#8fa3bb; --text:#edf5ff; --cyan:#35d5e8; --blue:#638cff; }
    html, body, [data-testid="stAppViewContainer"] { background:var(--bg); color:var(--text); font-family:'DM Sans',sans-serif; }
    [data-testid="stHeader"] { background:rgba(8,15,28,.92); }
    [data-testid="stSidebar"] { background:#0b1626; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] * { color:var(--text); }
    .block-container { padding-top:2rem; padding-bottom:3rem; max-width:1440px; }
    h1,h2,h3,.brand-name,.section-title { font-family:'Space Grotesk',sans-serif !important; }
    .brand { display:flex; align-items:center; gap:11px; padding:8px 4px 24px; }
    .brand-mark { width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#35d5e8,#638cff);display:flex;align-items:center;justify-content:center;color:#06111e;font-size:20px;font-weight:700; }
    .brand-name { font-size:19px;font-weight:700;letter-spacing:-.5px; }
    .brand-sub { color:var(--muted);font-size:10px;letter-spacing:1.6px;text-transform:uppercase;margin-top:2px; }
    .eyebrow { color:var(--cyan);font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px; }
    .page-title { font-family:'Space Grotesk',sans-serif;font-size:32px;font-weight:700;letter-spacing:-1px;color:var(--text);margin:0; }
    .page-desc { color:var(--muted);font-size:14px;margin-top:6px; }
    .topline { border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:24px; }
    .panel { background:linear-gradient(145deg,#122238,#0e1929);border:1px solid var(--line);border-radius:18px;padding:22px 24px; }
    .panel-label { color:var(--muted);font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase; }
    .gauge-wrap { display:flex;flex-direction:column;align-items:center;justify-content:center;padding:14px 0 2px; }
    .gauge { width:218px;height:218px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(from 225deg,var(--cyan) 0 var(--progress),#26364c var(--progress) 75%,transparent 75% 100%);position:relative; }
    .gauge:before { content:'';position:absolute;inset:10px;border-radius:50%;background:#101d30;border:1px solid #263a52; }
    .gauge-inner { position:relative;text-align:center; }
    .gauge-label { color:#9db3ca;font-size:10px;letter-spacing:1.7px;font-weight:700; }
    .gauge-value { font-family:'Space Grotesk',sans-serif;font-size:49px;font-weight:700;line-height:1.15;color:#f2f8ff;margin-top:8px; }
    .gauge-value span { font-family:'DM Sans',sans-serif;font-size:12px;color:#9db3ca;font-weight:500; }
    .gauge-unit { color:var(--cyan);font-size:10px;letter-spacing:1.4px;margin-top:5px; }
    .gauge-subtext { color:var(--muted);font-size:11px;margin-top:14px; }
    .metric-card { background:#111f32;border:1px solid var(--line);border-radius:15px;padding:17px 18px;min-height:136px; }
    .metric-top { display:flex;align-items:center;justify-content:space-between;margin-bottom:14px; }
    .metric-icon { width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:#1a3448;color:var(--cyan);font-size:15px; }
    .metric-note { font-size:10px;color:#8198b2; }
    .metric-title { color:#a9bbce;font-size:12px; }
    .metric-value { color:#f2f7ff;font-family:'Space Grotesk',sans-serif;font-size:27px;font-weight:700;margin-top:4px; }
    .metric-value span { font-family:'DM Sans',sans-serif;font-size:12px;color:#91a6bd;font-weight:500; }
    .section-heading { margin:26px 0 14px; }
    .section-title { font-size:18px;font-weight:600;color:var(--text); }
    .section-subtitle { color:var(--muted);font-size:12px;margin-top:3px; }
    .status-card { display:flex;gap:12px;align-items:flex-start;background:#111f32;border:1px solid var(--line);border-radius:14px;padding:16px;min-height:112px; }
    .status-dot { width:9px;height:9px;border-radius:50%;background:#8295aa;margin-top:5px;flex-shrink:0; }
    .status-card.good .status-dot { background:#39d6a2;box-shadow:0 0 12px #39d6a255; }
    .status-card.warning .status-dot { background:#f5b84b;box-shadow:0 0 12px #f5b84b55; }
    .status-title { color:#9db1c7;font-size:11px; }
    .status-value { color:#f0f6ff;font-size:14px;font-weight:700;margin-top:4px; }
    .status-detail { color:#8298b0;font-size:11px;margin-top:4px;line-height:1.45; }
    .info-banner { background:#10283a;border:1px solid #1d5264;border-radius:12px;padding:13px 16px;color:#b9dce7;font-size:12px;line-height:1.5; }
    div.stButton > button { background:linear-gradient(100deg,#35d5e8,#638cff);color:#06111e;border:0;border-radius:11px;font-weight:700;padding:.65rem 1rem;min-height:44px; }
    div.stButton > button:hover { border:0;color:#06111e;filter:brightness(1.08); }
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { background:#101f32;color:#edf5ff;border-color:#2a3c54;border-radius:10px; }
    [data-testid="stMetric"] { background:#111f32;padding:14px;border:1px solid var(--line);border-radius:12px; }
    [data-testid="stMetricLabel"] { color:#9db1c7; }
    [data-testid="stMetricValue"] { color:#f2f7ff; }
    hr { border-color:var(--line); }
    .footer { color:#71869d;font-size:10px;text-align:center;margin-top:36px;padding-top:16px;border-top:1px solid var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">⌁</div><div><div class="brand-name">WiFi-Radar ID</div><div class="brand-sub">Public Wi-Fi Intelligence</div></div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Community Map", "Scan History"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("<div class='panel-label'>SYSTEM STATUS</div>", unsafe_allow_html=True)
    st.caption("● UI prototype · Scanner not connected")
    st.markdown("---")
    st.caption("WiFi-Radar ID · Project Prototype")

if page == "Overview":
    st.markdown(
        '<div class="topline"><div class="eyebrow">NETWORK INTELLIGENCE PLATFORM</div><div class="page-title">Wi-Fi Overview</div><div class="page-desc">Understand your public Wi-Fi connection, quality, and security at a glance.</div></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1.95], gap="large")
    with left:
        st.markdown('<div class="panel-label">NETWORK HEALTH</div>', unsafe_allow_html=True)
        render_speed_gauge(st.session_state.get("demo_score"))
        st.markdown('<div class="info-banner">Your network overview will appear here after the scanner module is connected.</div>', unsafe_allow_html=True)

    with right:
        render_section_heading("Connection metrics", "Core Quality of Service (QoS) measurements")
        demo = st.session_state.get("demo_metrics")
        if demo:
            vals = demo
        else:
            vals = {"download": "--", "upload": "--", "ping": "--", "jitter": "--"}
        cols = st.columns(2, gap="medium")
        with cols[0]:
            render_metric_card("Download", vals["download"], "Mbps", "↓ DOWNLOAD", "↓")
            render_metric_card("Ping / Latency", vals["ping"], "ms", "◉ RESPONSE", "◌")
        with cols[1]:
            render_metric_card("Upload", vals["upload"], "Mbps", "↑ UPLOAD", "↑")
            render_metric_card("Jitter", vals["jitter"], "ms", "≈ STABILITY", "⌁")

    render_section_heading("Network assessment", "A quick look at neutrality indicators and public Wi-Fi security")
    a, b, c = st.columns(3, gap="medium")
    with a:
        render_status_card("NET NEUTRALITY", "Awaiting test", "Traffic comparison is not available yet.")
    with b:
        render_status_card("WI-FI SECURITY", "Awaiting audit", "Encryption and security checks will appear here.")
    with c:
        render_status_card("AI ADVISOR", "Standby", "Recommendations will appear after a scan.")

    render_section_heading("Run a network check", "The interface is ready; live measurement is waiting for the scanner module.")
    loc_col, ssid_col = st.columns(2)
    with loc_col:
        location = st.text_input("LOCATION", placeholder="e.g. Perpustakaan UGM")
    with ssid_col:
        ssid = st.text_input("WI-FI NAME / SSID", placeholder="Enter network name (optional)")
    button_col, note_col = st.columns([1, 2])
    with button_col:
        if st.button("▶  Start network test", use_container_width=True):
            st.info("Network scanner belum terhubung. Tombol ini akan menjalankan pengujian live setelah `network_scanner.py` siap.")
    with note_col:
        st.caption("Location and SSID are descriptive inputs for the prototype. Do not enter a Wi-Fi password.")

    with st.expander("Preview dashboard with sample data"):
        st.caption("Sample values below are illustrative only, not real measurements from your network.")
        if st.button("Load sample preview"):
            st.session_state["demo_score"] = 86
            st.session_state["demo_metrics"] = {"download": "48.6", "upload": "21.3", "ping": "18", "jitter": "3.2"}
            st.rerun()
        if st.button("Clear sample preview"):
            st.session_state.pop("demo_score", None)
            st.session_state.pop("demo_metrics", None)
            st.rerun()

elif page == "Community Map":
    st.markdown('<div class="topline"><div class="eyebrow">COMMUNITY NETWORK DATA</div><div class="page-title">Community Map</div><div class="page-desc">Explore public Wi-Fi quality and security reports shared by the community.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-label">MAP MODULE</div><h3>Community coverage map</h3><p style="color:#9db1c7">The map will be connected after the community database and location visualizer are ready.</p></div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="topline"><div class="eyebrow">YOUR NETWORK RECORDS</div><div class="page-title">Scan History</div><div class="page-desc">Review previous network checks and compare connection quality over time.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-label">SCAN LOGS</div><h3>No scan history yet</h3><p style="color:#9db1c7">Completed scans will be stored here after the database module is connected.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="footer">WI-FI RADAR ID · COMMUNITY-DRIVEN PUBLIC WI-FI MONITORING</div>', unsafe_allow_html=True)

