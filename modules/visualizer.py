"""Komponen visualisasi untuk dashboard WiFi-Radar ID."""

from __future__ import annotations

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium


STATUS_COLORS = {
    "aman": "#16865B",
    "rawan": "#E2A008",
    "bahaya": "#C43D45",
}
STATUS_LABELS = {
    "aman": "Aman",
    "rawan": "Rawan",
    "bahaya": "Bahaya",
}


def _status_key(category: str | None) -> str:
    value = str(category or "").strip().lower()
    if value in STATUS_COLORS:
        return value
    return "rawan"


def render_speed_gauge(value: float | None = None, label: str = "NETWORK SCORE") -> None:
    """Menampilkan skor rata-rata keamanan dalam bentuk gauge."""
    if value is None:
        value_text = "--"
        progress = 0
        subtext = "Belum ada hasil scan"
    else:
        progress = max(0, min(100, int(value)))
        value_text = str(progress)
        subtext = "Rata-rata skor keamanan lokasi"

    st.markdown(
        f"""
        <div style="background:#FFFFFF;border:1px solid #DCE3ED;border-radius:16px;padding:22px 12px;text-align:center;">
          <div style="color:#5F6F85;font-size:11px;font-weight:700;letter-spacing:1.4px;">{label}</div>
          <div style="width:174px;height:174px;border-radius:50%;margin:18px auto 12px;
              display:grid;place-items:center;
              background:conic-gradient(#315FBA {progress * 3.6}deg,#E8EDF5 0deg);">
            <div style="width:142px;height:142px;border-radius:50%;background:#FFFFFF;
                display:flex;flex-direction:column;align-items:center;justify-content:center;">
              <div style="font-size:43px;font-weight:800;line-height:1.1;color:#17243A;">{value_text}</div>
              <div style="font-size:12px;color:#718096;">{"/ 100" if value is not None else ""}</div>
            </div>
          </div>
          <div style="font-size:12px;color:#5F6F85;">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, unit: str, note: str, icon: str) -> None:
    """Menampilkan satu kartu metrik."""
    st.markdown(
        f"""
        <div style="background:#FFFFFF;border:1px solid #DCE3ED;border-radius:14px;padding:17px;min-height:120px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:13px;">
            <span style="width:31px;height:31px;border-radius:9px;background:#EAF1FF;color:#315FBA;display:grid;place-items:center;font-size:15px;">{icon}</span>
            <span style="font-size:10px;color:#718096;font-weight:700;">{note}</span>
          </div>
          <div style="font-size:12px;color:#5F6F85;">{title}</div>
          <div style="font-size:27px;font-weight:800;color:#17243A;margin-top:4px;">{value}<span style="font-size:12px;color:#718096;font-weight:500;"> {unit}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<div style="font-size:12px;color:#5F6F85;margin-top:4px;">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div style="margin:25px 0 13px;"><div style="font-size:18px;font-weight:700;color:#17243A;">{title}</div>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def render_status_card(title: str, status: str, detail: str, tone: str = "neutral") -> None:
    """tone: good, warning, danger, atau neutral."""
    tones = {
        "good": ("#EAF7F0", "#16865B"),
        "warning": ("#FFF6DF", "#A66B00"),
        "danger": ("#FDEEEF", "#C43D45"),
        "neutral": ("#F0F4FA", "#5F6F85"),
    }
    background, accent = tones.get(tone, tones["neutral"])
    st.markdown(
        f"""
        <div style="display:flex;gap:12px;align-items:flex-start;background:#FFFFFF;
            border:1px solid #DCE3ED;border-radius:13px;padding:16px;min-height:105px;">
          <span style="width:10px;height:10px;border-radius:50%;background:{accent};margin-top:5px;flex-shrink:0;"></span>
          <div>
            <div style="font-size:11px;color:#5F6F85;font-weight:700;">{title}</div>
            <div style="font-size:16px;color:#17243A;font-weight:700;margin-top:5px;">{status}</div>
            <div style="font-size:12px;color:#5F6F85;margin-top:4px;line-height:1.45;">{detail}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_community_map(locations: list[dict]) -> None:
    """Membuat peta Folium dengan pin hijau, kuning, dan merah berdasarkan kategori keamanan."""
    valid = [
        item for item in locations
        if item.get("latitude") is not None and item.get("longitude") is not None
    ]
    if not valid:
        st.info("Belum ada koordinat lokasi yang dapat ditampilkan.")
        return

    center_lat = sum(float(item["latitude"]) for item in valid) / len(valid)
    center_lon = sum(float(item["longitude"]) for item in valid) / len(valid)
    map_view = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    for item in valid:
        category = _status_key(item.get("category"))
        color = STATUS_COLORS[category]
        name = str(item.get("name") or "Lokasi Wi-Fi")
        score = item.get("score")
        score_text = f"{score}/100" if score is not None else "Belum ada skor"
        download = item.get("download_mbps")
        download_text = f"{download} Mbps" if download is not None else "Belum tersedia"
        popup_html = f"""
        <div style="font-family:Arial,sans-serif;min-width:180px;">
          <b>{name}</b><br>
          Status: {STATUS_LABELS[category]}<br>
          Skor keamanan: {score_text}<br>
          Download: {download_text}
        </div>
        """
        folium.CircleMarker(
            location=[float(item["latitude"]), float(item["longitude"])],
            radius=9,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=f"{name} · {STATUS_LABELS[category]}",
            popup=folium.Popup(popup_html, max_width=280),
        ).add_to(map_view)

    st_folium(map_view, use_container_width=True, height=520, returned_objects=[])

    st.markdown(
        """
        <div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:8px;font-size:12px;color:#33445C;">
          <span>🟢 Aman</span><span>🟡 Rawan</span><span>🔴 Bahaya</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_location_comparison(
    locations: list[dict],
    metric: str = "download_mbps",
    height: int = 360,
) -> None:
    """Membandingkan satu metrik antarlokasi menggunakan grafik batang."""
    metric_labels = {
        "download_mbps": ("Download", "Mbps"),
        "upload_mbps": ("Upload", "Mbps"),
        "ping_ms": ("Ping", "ms"),
        "score": ("Skor keamanan", "Poin"),
    }
    label, unit = metric_labels.get(metric, (metric.replace("_", " ").title(), ""))
    rows = []
    for item in locations:
        value = item.get(metric)
        if value is None:
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        rows.append({
            "Lokasi": str(item.get("name") or "Lokasi"),
            "Nilai": numeric_value,
            "Status": STATUS_LABELS[_status_key(item.get("category"))],
        })

    if not rows:
        st.info(f"Belum ada data {label.lower()} untuk dibandingkan.")
        return

    frame = pd.DataFrame(rows).sort_values("Nilai", ascending=True)
    color_map = {
        "Aman": STATUS_COLORS["aman"],
        "Rawan": STATUS_COLORS["rawan"],
        "Bahaya": STATUS_COLORS["bahaya"],
    }
    figure = px.bar(
        frame,
        x="Nilai",
        y="Lokasi",
        color="Status",
        orientation="h",
        color_discrete_map=color_map,
        text="Nilai",
        labels={"Nilai": f"{label} ({unit})", "Lokasi": ""},
    )
    figure.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
    figure.update_layout(
        height=height,
        margin=dict(l=8, r=35, t=18, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="DM Sans, sans-serif", color="#33445C", size=12),
        legend_title_text="Status keamanan",
        xaxis=dict(showgrid=True, gridcolor="#E8EDF4", zeroline=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
