"""
AgriSense - Reusable UI Components & Botanical Theme System
Provides:
- Modern Botanical Intelligence styling & hero banner with local image + CSS fallback
- Styled KPI cards (standard and dark forest variants)
- Consistent Plotly chart theming (apply_agrisense_theme)
- CSV export utility with clean column names and no index
- Database connectivity and data status indicators
- Dynamic data-driven insights panels
- Informative empty states
"""
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from config.settings import settings
from database.mysql_connection import check_mysql_connection
from database.mongo_connection import check_mongo_connection


# Botanical Palette Tokens for Charts & Components
AGRI_PALETTE = {
    "deep_forest": "#173F35",
    "primary_green": "#26734D",
    "fresh_leaf": "#78A85A",
    "pale_sage": "#E8EFE5",
    "warm_bg": "#F7F8F3",
    "surface_white": "#FFFFFF",
    "dark_charcoal": "#24332C",
    "muted_text": "#738078",
    "soft_border": "#E1E8DF",
    "muted_amber": "#D69B36",
    "muted_red": "#C65C50",
    "teal_accent": "#2A9D8F",
    "light_teal": "#52B8AE",
}

# Standard sequence of harmonious agricultural colors for multi-category charts
AGRI_COLOR_SEQUENCE = [
    "#26734D",  # Primary Agricultural Green
    "#78A85A",  # Fresh Leaf Green
    "#D69B36",  # Harvest Amber
    "#2A9D8F",  # Irrigation Teal
    "#C65C50",  # Muted Terracotta
    "#173F35",  # Deep Forest
    "#52B8AE",  # Soft Cyan-Green
    "#8F9489",  # Slate Sage
]


def inject_custom_css() -> None:
    """Injects the global CSS stylesheet into the Streamlit app."""
    css_path = settings.paths.css_path
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def get_hero_banner_base64() -> Optional[str]:
    """Reads local hero_banner.jpg and returns a base64 data URI, or None if unavailable."""
    banner_path = settings.paths.assets_dir / "hero_banner.jpg"
    if banner_path.exists():
        try:
            with open(banner_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/jpeg;base64,{encoded}"
        except Exception:
            return None
    return None


def render_hero_header() -> None:
    """
    Renders the distinctive AgriSense welcome/header hero banner.
    Includes the local high-resolution agricultural landscape with dark green gradient overlay,
    clear typographic hierarchy, and a pure CSS botanical fallback if the image is missing.
    """
    bg_uri = get_hero_banner_base64()
    bg_css = f'style="background-image: url(\'{bg_uri}\');"' if bg_uri else ""

    st.markdown(
        f"""
        <div class="agri-hero-banner">
            <div class="agri-hero-bg" {bg_css}></div>
            <div class="agri-hero-overlay"></div>
            <div class="agri-hero-content">
                <div class="agri-hero-title">
                    <span>🌾</span> AgriSense
                </div>
                <div class="agri-hero-subtitle">
                    Agricultural Monitoring &amp; Analytics Platform
                </div>
                <div class="agri-hero-motto">
                    “Understand crop performance. Monitor resources. Make informed agricultural decisions.”
                </div>
                <div class="agri-hero-meta">
                    <span class="sdg-tag">🎯 SDG 2: Zero Hunger</span>
                    <span class="sdg-tag">🌱 SDG 12: Responsible Consumption</span>
                    <span class="badge badge-sage">Pure Statistical Data Analytics (Deterministic Non-AI)</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str, sdg_label: Optional[str] = None) -> None:
    """Renders a refined, compact page header for analytical subpages."""
    sdg_html = f'<div style="margin-top: 0.5rem;"><span class="sdg-tag">🎯 {sdg_label}</span></div>' if sdg_label else ""
    st.markdown(
        f"""
        <div class="agri-page-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            {sdg_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    """Renders the top branding block in the Streamlit sidebar."""
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <span class="brand-badge">Academic &amp; Research Platform</span>
            <div class="brand-title">🌾 AgriSense</div>
            <div class="brand-subtitle">Agricultural Intelligence through Data</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_category(category_name: str) -> None:
    """Renders a clean category divider in the sidebar."""
    st.sidebar.markdown(
        f'<div class="sidebar-category-header">{category_name}</div>',
        unsafe_allow_html=True,
    )


def render_kpi(col, title: str, value: str, subtext: str = "", icon: str = "", is_dark: bool = False):
    """
    Renders a custom-styled KPI metric card with green accent bar,
    subtle hover elevation, and distinct dark-forest option.
    """
    dark_class = "kpi-card-dark" if is_dark else ""
    icon_html = f'<span class="kpi-icon">{icon}</span>' if icon else ""

    with col:
        st.markdown(
            f"""
            <div class="kpi-card {dark_class}">
                <div class="kpi-header-row">
                    <div class="kpi-title">{title}</div>
                    {icon_html}
                </div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-subtext">{subtext}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_database_status_strip() -> None:
    """
    Renders an informative, honest database and data-engine status strip.
    Detects whether MySQL and MongoDB are live or running on verified local data fallback.
    """
    mysql_ok, _ = check_mysql_connection()
    mongo_ok, _ = check_mongo_connection()

    col1, col2, col3 = st.columns([1.5, 1.5, 3])
    with col1:
        if mysql_ok:
            st.markdown('<span class="badge badge-green">● MySQL 8.0: Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-amber">● MySQL: Verified Local Fallback</span>', unsafe_allow_html=True)

    with col2:
        if mongo_ok:
            st.markdown('<span class="badge badge-green">● MongoDB 6.0+: Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-amber">● MongoDB: Verified Local Fallback</span>', unsafe_allow_html=True)

    with col3:
        st.markdown(
            '<div style="text-align: right; font-size: 0.78rem; color: #738078; padding-top: 4px;">'
            'Engine: <strong>Deterministic SQL &amp; Statistical Aggregation</strong> (No-AI)</div>',
            unsafe_allow_html=True,
        )
    st.divider()


def apply_agrisense_theme(
    fig: go.Figure,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    height: int = 320,
    show_legend: bool = True,
) -> go.Figure:
    """
    Applies the AgriSense 'Modern Botanical Intelligence' theme to any Plotly figure.
    Ensures white background, subtle soft-border gridlines, Manrope typography,
    and comfortable margins across all pages.
    """
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Manrope, sans-serif", size=13, color=AGRI_PALETTE["deep_forest"]),
            x=0.01,
            y=0.96,
        ) if title else None,
        font=dict(family="Manrope, sans-serif", color=AGRI_PALETTE["dark_charcoal"], size=11),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=20, r=20, t=35 if title else 20, b=25),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
        ),
        xaxis=dict(
            title=dict(text=x_title, font=dict(size=11, color=AGRI_PALETTE["muted_text"])) if x_title else None,
            gridcolor=AGRI_PALETTE["soft_border"],
            zerolinecolor=AGRI_PALETTE["soft_border"],
            showline=True,
            linecolor=AGRI_PALETTE["soft_border"],
            tickfont=dict(size=10, color=AGRI_PALETTE["dark_charcoal"]),
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=11, color=AGRI_PALETTE["muted_text"])) if y_title else None,
            gridcolor=AGRI_PALETTE["soft_border"],
            zerolinecolor=AGRI_PALETTE["soft_border"],
            showline=True,
            linecolor=AGRI_PALETTE["soft_border"],
            tickfont=dict(size=10, color=AGRI_PALETTE["dark_charcoal"]),
        ),
        hoverlabel=dict(
            bgcolor=AGRI_PALETTE["deep_forest"],
            font_size=11,
            font_family="Manrope, sans-serif",
            font_color="#FFFFFF",
            bordercolor=AGRI_PALETTE["primary_green"],
        ),
    )
    return fig


def render_csv_export(df: pd.DataFrame, filename: str, label: str = "📥 Export Data to CSV") -> None:
    """Renders a clean, reliable CSV export button with no index and UTF-8 encoding."""
    if df.empty:
        return
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        key=f"export_{filename}",
    )


def render_empty_state(message: str = "No data is available for the selected filters.") -> None:
    """Renders a restrained, informative empty state."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2.5rem 1rem; background: #FFFFFF; border: 1px dashed #E1E8DF; border-radius: 12px; margin: 1rem 0;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem; opacity: 0.7;">🌾</div>
            <div style="font-size: 0.95rem; font-weight: 600; color: #24332C; margin-bottom: 0.3rem;">Data Unpopulated</div>
            <div style="font-size: 0.84rem; color: #738078; max-width: 480px; margin: 0 auto;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insights_panel(insights: List[Dict[str, str]]) -> None:
    """
    Renders dynamically calculated agricultural insights with icons
    and precise statistical grounding (100% deterministic, non-AI).
    """
    if not insights:
        return

    items_html = ""
    for ins in insights:
        icon = ins.get("icon", "🌱")
        title = ins.get("title", "")
        detail = ins.get("detail", "")
        items_html += f"""
        <div class="insight-item">
            <span>{icon}</span>
            <div><strong>{title}:</strong> {detail}</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-card-header">
                <span>📊</span> Data-Driven Agricultural Insights (Deterministic Rules)
            </div>
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
