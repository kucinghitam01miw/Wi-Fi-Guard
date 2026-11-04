"""Reusable UI components for WiFi-Radar ID's Streamlit dashboard."""

from __future__ import annotations

import streamlit as st


def render_speed_gauge(value: float | None = None, label: str = "NETWORK SCORE") -> None:
    """Render a clean circular gauge. None means no scan has been run yet."""
    if value is None:
        value_text = "--"
        progress = 0
        subtext = "Belum ada pengujian"
    else:
        progress = max(0, min(100, int(value)))
        value_text = str(progress)
        subtext = "Skor simulasi · bukan hasil pengukuran"

    st.markdown(
        f"""
        <div class="gauge-wrap">
          <div class="gauge" style="--progress:{progress}%">
            <div class="gauge-inner">
              <div class="gauge-label">{label}</div>
              <div class="gauge-value">{value_text}<span>{' / 100' if value is not None else ''}</span></div>
              <div class="gauge-unit">{ 'NETWORK HEALTH' if value is not None else 'READY TO TEST' }</div>
            </div>
          </div>
          <div class="gauge-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, unit: str, note: str, icon: str) -> None:
    """Render one compact metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-top"><span class="metric-icon">{icon}</span><span class="metric-note">{note}</span></div>
          <div class="metric-title">{title}</div>
          <div class="metric-value">{value}<span> {unit}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="section-heading"><div class="section-title">{title}</div>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def render_status_card(title: str, status: str, detail: str, tone: str = "neutral") -> None:
    """tone can be: good, warning, neutral."""
    tone = tone if tone in {"good", "warning", "neutral"} else "neutral"
    st.markdown(
        f"""
        <div class="status-card {tone}">
          <div class="status-dot"></div>
          <div class="status-copy"><div class="status-title">{title}</div>
          <div class="status-value">{status}</div><div class="status-detail">{detail}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

