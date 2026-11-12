from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.visualizer import (
    render_metric_card,
    render_section_heading,
    render_speed_gauge,
    render_status_card,
    render_community_map,
    render_location_comparison,
)

st.set_page_config(
    page_title="WiFi-Radar ID | Public Wi-Fi Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Light theme ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    :root {
        --bg: #F5F7FB; --surface: #FFFFFF; --surface-soft: #F0F4FA;
        --line: #DCE3ED; --text: #17243A; --muted: #5F6F85;
        --blue: #315FBA; --blue-soft: #EAF1FF; --green: #16865B;
        --yellow: #B77908; --red: #C43D45;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg); color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stHeader"] { background: rgba(245,247,251,.92); }
    [data-testid="stSidebar"] {
        background: #FFFFFF; border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { color: var(--text); }
    .block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1480px; }
    h1,h2,h3,.brand-name,.page-title,.section-title {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text) !important;
    }
    .brand { display:flex; align-items:center; gap:12px; padding:8px 4px 24px; }
    .brand-mark {
        width:42px; height:42px; border-radius:13px; background:#EAF1FF;
        display:flex; align-items:center; justify-content:center;
        color:#315FBA; font-size:23px; font-weight:700;
    }
    .brand-name { font-size:19px; font-weight:800; letter-spacing:-.5px; }
    .brand-sub { color:var(--muted); font-size:10px; letter-spacing:1.25px; text-transform:uppercase; margin-top:3px; }
    .eyebrow { color:var(--blue); font-size:11px; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; margin-bottom:8px; }
    .page-title { font-size:31px; font-weight:800; letter-spacing:-.8px; margin:0; }
    .page-desc { color:var(--muted); font-size:14px; margin-top:7px; line-height:1.55; }
    .topline { border-bottom:1px solid var(--line); padding-bottom:20px; margin-bottom:24px; }
    .panel { background:var(--surface); border:1px solid var(--line); border-radius:17px; padding:20px 22px; }
    .panel-label { color:var(--muted); font-size:11px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; }
    .info-banner {
        background:#EAF1FF; border:1px solid #D4E1FC; border-radius:12px;
        padding:13px 16px; color:#294C88; font-size:13px; line-height:1.55;
    }
    div.stButton > button {
        background:#315FBA; color:#FFFFFF; border:1px solid #315FBA;
        border-radius:10px; font-weight:700; min-height:42px;
    }
    div.stButton > button:hover { background:#244D9D; border-color:#244D9D; color:#FFFFFF; }
    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background:#FFFFFF !important; color:#17243A !important;
        border:1px solid #C9D4E2 !important; border-radius:9px;
    }
    div[data-testid="stTextInput"] input::placeholder { color:#78879A !important; opacity:1; }
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label { color:#33445C !important; font-weight:600; }
    [data-testid="stMetric"] {
        background:#FFFFFF; padding:15px; border:1px solid var(--line); border-radius:13px;
    }
    [data-testid="stMetricLabel"] { color:#5F6F85; }
    [data-testid="stMetricValue"] { color:#17243A; }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; }
    hr { border-color:var(--line); }
    .footer { color:#78879A; font-size:11px; text-align:center; margin-top:34px; padding-top:16px; border-top:1px solid var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_location_data() -> tuple[list[dict], bool]:
    """Ambil ringkasan lokasi dari database; gunakan seed sebagai preview jika DB kosong."""
    try:
        from modules.database import get_all_locations_summary, init_db

        init_db()
        rows = get_all_locations_summary()
        if rows:
            valid_rows = [dict(row) for row in rows if row.get("latitude") is not None and row.get("longitude") is not None]
            if valid_rows:
                return valid_rows, False
    except Exception as exc:
        st.warning(f"Database belum dapat dimuat: {exc}")

    seed_path = Path(__file__).resolve().parent / "data" / "seed_data.json"
    if seed_path.exists():
        try:
            with seed_path.open("r", encoding="utf-8") as file:
                seed = json.load(file)
            preview = []
            for location in seed.get("locations_master", []):
                scan = location.get("initial_scan", {})
                preview.append({
                    **location,
                    **scan,
                    "timestamp": "Data seed",
                    "scan_id": None,
                })
            return preview, True
        except (OSError, json.JSONDecodeError):
            pass
    return [], False


def number_or_none(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


locations, is_preview = load_location_data()
categories = [str(item.get("category") or "Belum diuji") for item in locations]
safe_count = sum(category.lower() == "aman" for category in categories)
warning_count = sum(category.lower() == "rawan" for category in categories)
danger_count = sum(category.lower() == "bahaya" for category in categories)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">⌁</div><div><div class="brand-name">WiFi-Radar ID</div><div class="brand-sub">Public Wi-Fi Intelligence</div></div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio("NAVIGATION", ["Overview", "Community Map", "Scan History"])
    st.markdown("---")
    st.markdown('<div class="panel-label">DATA STATUS</div>', unsafe_allow_html=True)
    if is_preview:
        st.caption("● Seed data preview · bukan pengukuran langsung")
    else:
        st.caption("● Data dari database")
    st.markdown("---")
    st.caption("WiFi-Radar ID · Project Prototype")

if page == "Overview":
    st.markdown(
        '<div class="topline"><div class="eyebrow">NETWORK INTELLIGENCE PLATFORM</div><div class="page-title">Wi-Fi Overview</div><div class="page-desc">Lihat ringkasan kualitas dan keamanan jaringan Wi-Fi publik dari data komunitas.</div></div>',
        unsafe_allow_html=True,
    )

    if is_preview:
        st.markdown(
            '<div class="info-banner">Dashboard sedang menampilkan data awal dari <b>data/seed_data.json</b> sebagai preview. Data ini bukan hasil pemindaian langsung dan akan tergantikan ketika database berisi hasil scan.</div>',
            unsafe_allow_html=True,
        )
        st.write("")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lokasi terdaftar", len(locations))
    col2.metric("Kategori aman", safe_count)
    col3.metric("Perlu perhatian", warning_count)
    col4.metric("Risiko tinggi", danger_count)

    st.write("")
    left, right = st.columns([1, 1.7], gap="large")
    with left:
        render_section_heading("Network health", "Skor keamanan dari hasil scan terbaru")
        scores = [number_or_none(item.get("score")) for item in locations]
        scores = [score for score in scores if score is not None]
        average_score = round(sum(scores) / len(scores)) if scores else None
        render_speed_gauge(average_score, label="AVERAGE SECURITY SCORE")
    with right:
        render_section_heading("Location comparison", "Perbandingan kecepatan download tiap lokasi")
        render_location_comparison(locations, metric="download_mbps", height=330)

    render_section_heading("Network assessment", "Distribusi status keamanan jaringan")
    a, b, c = st.columns(3, gap="medium")
    with a:
        render_status_card("AMAN", f"{safe_count} lokasi", "Skor keamanan 80–100.", "good")
    with b:
        render_status_card("RAWAN", f"{warning_count} lokasi", "Skor keamanan 50–79.", "warning")
    with c:
        render_status_card("BAHAYA", f"{danger_count} lokasi", "Skor keamanan di bawah 50.", "danger")

elif page == "Community Map":
    st.markdown(
        '<div class="topline"><div class="eyebrow">COMMUNITY NETWORK DATA</div><div class="page-title">Community Map</div><div class="page-desc">Jelajahi lokasi Wi-Fi publik dan bandingkan kualitas koneksi serta skor keamanannya.</div></div>',
        unsafe_allow_html=True,
    )
    if is_preview:
        st.markdown(
            '<div class="info-banner">Peta dan grafik saat ini memakai data seed untuk demonstrasi. Nilainya belum tentu mencerminkan kondisi jaringan saat ini.</div>',
            unsafe_allow_html=True,
        )
        st.write("")

    if locations:
        selected_status = st.selectbox("Filter status keamanan", ["Semua status", "Aman", "Rawan", "Bahaya"])
        filtered = locations if selected_status == "Semua status" else [
            item for item in locations if str(item.get("category", "")).lower() == selected_status.lower()
        ]
        render_community_map(filtered)
        st.write("")
        metric_options = {
            "Download (Mbps)": "download_mbps",
            "Upload (Mbps)": "upload_mbps",
            "Ping (ms)": "ping_ms",
            "Skor keamanan": "score",
        }
        selected_metric = st.selectbox("Metrik perbandingan", list(metric_options.keys()))
        render_location_comparison(filtered, metric=metric_options[selected_metric], height=390)

        table_rows = []
        for item in filtered:
            table_rows.append({
                "Lokasi": item.get("name", "-"),
                "Area": item.get("area", "-"),
                "Download (Mbps)": item.get("download_mbps"),
                "Upload (Mbps)": item.get("upload_mbps"),
                "Ping (ms)": item.get("ping_ms"),
                "Skor": item.get("score"),
                "Status": item.get("category", "Belum diuji"),
            })
        render_section_heading("Location details", "Ringkasan hasil scan terbaru per lokasi")
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data lokasi. Tambahkan lokasi dan hasil pengujian melalui modul database.")

else:
    st.markdown(
        '<div class="topline"><div class="eyebrow">YOUR NETWORK RECORDS</div><div class="page-title">Scan History</div><div class="page-desc">Lihat hasil pengujian jaringan yang tersimpan di database.</div></div>',
        unsafe_allow_html=True,
    )
    try:
        from modules.database import get_scan_history

        history = get_scan_history(limit=100)
    except Exception as exc:
        history = []
        st.warning(f"Riwayat belum dapat dimuat: {exc}")

    if history:
        history_df = pd.DataFrame(history)
        preferred = ["timestamp", "name", "ssid", "download_mbps", "upload_mbps", "ping_ms", "jitter_ms", "score", "category"]
        available = [column for column in preferred if column in history_df.columns]
        st.dataframe(history_df[available], use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat scan yang tersimpan. Data seed hanya digunakan untuk preview peta dan grafik.")

st.markdown(
    '<div class="footer">WI-FI RADAR ID · COMMUNITY-DRIVEN PUBLIC WI-FI MONITORING</div>',
    unsafe_allow_html=True,
)
