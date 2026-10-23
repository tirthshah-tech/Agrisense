"""
AgriSense - Modern Agricultural Analytics Platform
Main Streamlit Application Entrypoint
A Python-Based Data-Driven Crop Monitoring and Agricultural Analytics Platform.
Focus: Academic & Research Reference (Pure Data Analytics, Strictly Non-AI/Non-ML).
"""
import sys
from pathlib import Path

# Ensure root directory is on Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

from ui.components import inject_custom_css, render_sidebar_brand
from ui.dashboard import render_dashboard
from ui.farms import render_farms_page
from ui.crops import render_crops_page
from ui.soil import render_soil_page
from ui.resources import render_resources_page
from ui.fertilizer import render_fertilizer_page
from ui.weather import render_weather_page
from ui.yield_view import render_yield_page
from ui.resource_efficiency import render_resource_efficiency_page
from ui.alerts import render_alerts_page
from ui.data_quality import render_data_quality_page


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="AgriSense | Agricultural Analytics",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Inject Custom Botanical Theme CSS
    inject_custom_css()

    # 3. Sidebar Branding Block
    render_sidebar_brand()

    # 4. Navigation Menu Organized by Strategic Domain
    nav_options = [
        "📊 Dashboard",
        "🏡 Farms",
        "🌾 Crop Analytics",
        "🧪 Soil Monitoring",
        "⛅ Weather",
        "💧 Water & Irrigation",
        "🌿 Fertilizer",
        "📈 Yield Analysis",
        "⚡ Resource Efficiency",
        "🚨 Alerts",
        "🛡️ Data Quality",
    ]

    selected_page = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=0,
        label_visibility="collapsed",
    )

    # 5. Sidebar SDG Alignment & Technical Governance
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.74rem; color: #A4B3A8; line-height: 1.55; padding: 0 4px;">
            <strong style="color: #E8EFE5; letter-spacing: 0.04em;">UN SDG Alignment:</strong><br>
            • <strong style="color: #BDE0C3;">SDG 2:</strong> Zero Hunger (Productivity &amp; Soil)<br>
            • <strong style="color: #BDE0C3;">SDG 12:</strong> Responsible Consumption (Water &amp; Inputs)<br><br>
            <strong style="color: #E8EFE5; letter-spacing: 0.04em;">Analytical Engine:</strong><br>
            • Relational (MySQL) &amp; Document (MongoDB)<br>
            • Statistical Aggregations &amp; KPI Formulas<br>
            • Deterministic Rule-Based Alerts<br>
            <span style="display:inline-block; margin-top:4px; padding:2px 6px; background:rgba(120,168,90,0.2); border-radius:4px; color:#A3CF88;">
                Deterministic Non-AI / Non-ML
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 6. Route to Selected Page
    if selected_page == "📊 Dashboard":
        render_dashboard()
    elif selected_page == "🏡 Farms":
        render_farms_page()
    elif selected_page == "🌾 Crop Analytics":
        render_crops_page()
    elif selected_page == "🧪 Soil Monitoring":
        render_soil_page()
    elif selected_page == "⛅ Weather":
        render_weather_page()
    elif selected_page == "💧 Water & Irrigation":
        render_resources_page()
    elif selected_page == "🌿 Fertilizer":
        render_fertilizer_page()
    elif selected_page == "📈 Yield Analysis":
        render_yield_page()
    elif selected_page == "⚡ Resource Efficiency":
        render_resource_efficiency_page()
    elif selected_page == "🚨 Alerts":
        render_alerts_page()
    elif selected_page == "🛡️ Data Quality":
        render_data_quality_page()


if __name__ == "__main__":
    main()
