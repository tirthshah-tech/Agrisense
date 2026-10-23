"""
AgriSense - Farms & Landholdings Directory View
Provides interactive directory of farmers, farm holdings, geographic coordinates,
soil classifications, irrigation methods, and farm-level summary metrics.
"""
import streamlit as st
import plotly.express as px
import pandas as pd

from ui.components import (
    render_page_header,
    render_kpi,
    render_database_status_strip,
    apply_agrisense_theme,
    render_csv_export,
    render_empty_state,
    AGRI_COLOR_SEQUENCE,
)
from repositories.farmer_repository import FarmerRepository
from repositories.farm_repository import FarmRepository
from services.farm_service import FarmService


def render_farms_page() -> None:
    """Renders the Farms & Farmers directory view."""
    render_page_header(
        title="Farms & Landholdings Directory",
        subtitle="Manage farmer profiles, land boundaries, soil classifications, and irrigation setups across Maharashtra districts.",
        sdg_label="SDG 2: Sustainable Agriculture & Farm Land Management",
    )
    render_database_status_strip()

    farm_svc = FarmService()
    farm_repo = FarmRepository()
    farmer_repo = FarmerRepository()

    metrics = farm_svc.get_summary_metrics()

    f1, f2, f3, f4 = st.columns(4)
    render_kpi(f1, "Registered Farmers", str(metrics["total_farmers"]), "Maharashtra Network", icon="👨‍🌾", is_dark=True)
    render_kpi(f2, "Total Farm Parcels", str(metrics["total_farms"]), "Geo-referenced holdings", icon="🏡")
    render_kpi(f3, "Cultivated Land", f"{metrics['total_cultivated_area_ha']:,.1f} ha", "Across all districts", icon="🗺️")
    render_kpi(f4, "Average Holding Size", f"{metrics['avg_farm_size_ha']:.1f} ha", "Per farm parcel", icon="📐")

    st.markdown("<br>", unsafe_allow_html=True)

    farms_df = farm_repo.get_all_farms()
    farmers_df = farmer_repo.get_all_farmers()

    if farms_df.empty or farmers_df.empty:
        render_empty_state("No farms or farmers records available in database.")
        return

    # Merge farmer details into farms
    merged = farms_df.merge(
        farmers_df[["farmer_id", "name", "phone", "district", "village"]],
        on="farmer_id",
        how="left",
    )

    # ── Visual Analytics: Soil & Irrigation Distribution ──────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🧪 Farm Holdings by Soil Type")
        soil_dist = farm_svc.get_farms_by_soil_type()
        if not soil_dist.empty:
            fig_soil = px.bar(
                soil_dist,
                x="soil_type",
                y="total_area_ha",
                color="soil_type",
                text="total_area_ha",
                labels={"soil_type": "Soil Type", "total_area_ha": "Total Area (ha)"},
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_soil.update_traces(textposition="outside")
            fig_soil = apply_agrisense_theme(fig_soil, title="", y_title="Area (ha)", height=300, show_legend=False)
            st.plotly_chart(fig_soil, use_container_width=True)

    with c2:
        st.subheader("💧 Irrigation Infrastructure")
        irrig_dist = farm_svc.get_farms_by_irrigation_type()
        if not irrig_dist.empty:
            fig_irrig = px.pie(
                irrig_dist,
                names="irrigation_type",
                values="count",
                hole=0.45,
                color="irrigation_type",
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_irrig = apply_agrisense_theme(fig_irrig, title="", height=300, show_legend=False)
            st.plotly_chart(fig_irrig, use_container_width=True)

    # ── Directory Filters & Search ───────────────────────────────────────────
    st.subheader("📋 Registered Farm Directory")
    fc1, fc2, fc3, fc4 = st.columns([1.5, 1.5, 1.5, 2.0])

    with fc1:
        districts = ["All Districts"] + sorted(merged["district"].dropna().unique().tolist())
        sel_district = st.selectbox("District", districts, key="farm_view_dist")
    with fc2:
        soils = ["All Soil Types"] + sorted(merged["soil_type"].dropna().unique().tolist())
        sel_soil = st.selectbox("Soil Type", soils, key="farm_view_soil")
    with fc3:
        irrigs = ["All Irrigation Types"] + sorted(merged["irrigation_type"].dropna().unique().tolist())
        sel_irrig = st.selectbox("Irrigation Type", irrigs, key="farm_view_irrig")
    with fc4:
        search_query = st.text_input("🔍 Search Farmer or Farm Name", key="farm_search_query")

    filtered = merged.copy()
    if sel_district != "All Districts":
        filtered = filtered[filtered["district"] == sel_district]
    if sel_soil != "All Soil Types":
        filtered = filtered[filtered["soil_type"] == sel_soil]
    if sel_irrig != "All Irrigation Types":
        filtered = filtered[filtered["irrigation_type"] == sel_irrig]
    if search_query:
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["farm_name"].str.lower().str.contains(q, na=False) |
            filtered["name"].str.lower().str.contains(q, na=False) |
            filtered["village"].str.lower().str.contains(q, na=False)
        ]

    st.caption(f"Displaying {len(filtered)} of {len(merged)} registered farm records")

    display_cols = ["farm_id", "farm_name", "name", "phone", "district", "village", "area_hectares", "soil_type", "irrigation_type"]
    rename_cols = {
        "farm_id": "Farm ID",
        "farm_name": "Farm Name",
        "name": "Farmer Name",
        "phone": "Phone Contact",
        "district": "District",
        "village": "Village",
        "area_hectares": "Area (ha)",
        "soil_type": "Soil Type",
        "irrigation_type": "Irrigation",
    }
    st.dataframe(
        filtered[display_cols].rename(columns=rename_cols),
        use_container_width=True,
        hide_index=True,
    )

    # Export CSV
    render_csv_export(filtered[display_cols].rename(columns=rename_cols), "agrisense_farms_directory.csv", "📥 Export Farm Directory (CSV)")
