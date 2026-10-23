"""
AgriSense - Soil Monitoring & Fertility Analytics View
Evaluates soil chemical balance, NPK nutrient availability, pH distribution,
moisture levels, and rule-based agronomic soil classifications across parcels.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from ui.components import (
    render_page_header,
    render_kpi,
    render_database_status_strip,
    apply_agrisense_theme,
    render_csv_export,
    render_empty_state,
    AGRI_COLOR_SEQUENCE,
    AGRI_PALETTE,
)
from services.soil_service import SoilService
from repositories.soil_repository import SoilRepository
from repositories.farm_repository import FarmRepository
from analytics.soil_analytics import SoilAnalytics
from utils.helpers import classify_soil_ph, classify_soil_nutrient


def render_soil_page() -> None:
    """Renders the comprehensive Soil Monitoring & Health view."""
    render_page_header(
        title="Soil Health & Macro-Nutrient Monitoring",
        subtitle="Chemical lab analysis, NPK macro-nutrient indices, moisture levels, and pH status across soil parcels.",
        sdg_label="SDG 2: Sustainable Agriculture & Land Degradation Neutrality",
    )
    render_database_status_strip()

    soil_svc = SoilService()
    soil_repo = SoilRepository()
    farm_repo = FarmRepository()
    soil_analytics = SoilAnalytics()

    metrics = soil_svc.get_soil_summary_metrics()
    deficiencies = soil_svc.get_npk_deficiency_rates()
    soil_df = soil_repo.get_all_soil_records()
    farms_df = farm_repo.get_all_farms()

    if soil_df.empty:
        render_empty_state("No soil laboratory test records available.")
        return

    # Normalize moisture column
    moisture_col = "moisture_percentage" if "moisture_percentage" in soil_df.columns else "moisture"

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    s1, s2, s3, s4, s5 = st.columns(5)
    render_kpi(s1, "Soil Lab Tests", f"{metrics['total_records']:,}", "Parcels Sampled", icon="🧪", is_dark=True)
    render_kpi(s2, "Mean Soil pH", f"{metrics['avg_ph']:.2f}", "Ideal: 6.5 – 7.5", icon="⚖️")
    render_kpi(s3, "Avg Nitrogen (N)", f"{metrics['avg_nitrogen']} kg/ha", f"Low in {deficiencies['N_low_pct']}% soils", icon="🌱")
    render_kpi(s4, "Avg Phosphorus (P)", f"{metrics['avg_phosphorus']} kg/ha", f"Low in {deficiencies['P_low_pct']}% soils", icon="🌿")
    render_kpi(s5, "Avg Potassium (K)", f"{metrics['avg_potassium']} kg/ha", f"Low in {deficiencies['K_low_pct']}% soils", icon="🌾")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visual Analytics Row 1: pH Distribution & NPK Deficiency Rates ────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("⚖️ Soil pH Classification Distribution")
        ph_df = soil_svc.get_ph_distribution()
        if not ph_df.empty:
            ph_color_map = {
                "Strongly Acidic": "#C65C50",
                "Moderately Acidic": "#D69B36",
                "Slightly Acidic": "#78A85A",
                "Neutral": "#26734D",
                "Slightly Alkaline": "#2A9D8F",
                "Moderately Alkaline": "#173F35",
                "Strongly Alkaline": "#8F9489",
            }
            fig_ph = px.pie(
                ph_df,
                names="ph_band",
                values="sample_count",
                hole=0.45,
                color="ph_band",
                color_discrete_map=ph_color_map,
            )
            fig_ph.update_traces(textposition="outside", textinfo="percent+label")
            fig_ph = apply_agrisense_theme(fig_ph, title="", height=310, show_legend=False)
            st.plotly_chart(fig_ph, use_container_width=True)

    with c2:
        st.subheader("📉 Macro-Nutrient Deficiency Proportions (< Optimal)")
        def_df = pd.DataFrame([
            {"Nutrient": "Nitrogen (N)", "Deficient_Pct": deficiencies["N_low_pct"], "Optimal_Threshold": "280 kg/ha"},
            {"Nutrient": "Phosphorus (P)", "Deficient_Pct": deficiencies["P_low_pct"], "Optimal_Threshold": "10 kg/ha"},
            {"Nutrient": "Potassium (K)", "Deficient_Pct": deficiencies["K_low_pct"], "Optimal_Threshold": "110 kg/ha"},
        ])
        fig_def = px.bar(
            def_df,
            x="Nutrient",
            y="Deficient_Pct",
            color="Nutrient",
            text="Deficient_Pct",
            labels={"Deficient_Pct": "Samples Deficient (%)", "Nutrient": "Macro-Nutrient"},
            color_discrete_sequence=["#26734D", "#78A85A", "#D69B36"],
        )
        fig_def.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_def = apply_agrisense_theme(fig_def, title="", y_title="Deficient Samples (%)", height=310, show_legend=False)
        st.plotly_chart(fig_def, use_container_width=True)

    # ── Visual Analytics Row 2: Moisture vs N & Soil Type Comparison ──────────
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("💧 Soil Moisture vs Available Nitrogen")
        if moisture_col in soil_df.columns:
            fig_scatter = px.scatter(
                soil_df.head(200),
                x="nitrogen",
                y=moisture_col,
                color="ph",
                hover_data=["farm_id"],
                labels={"nitrogen": "Available Nitrogen (kg/ha)", moisture_col: "Moisture Content (%)", "ph": "Soil pH"},
                color_continuous_scale=["#C65C50", "#78A85A", "#26734D"],
            )
            fig_scatter = apply_agrisense_theme(fig_scatter, title="", height=310, show_legend=True)
            st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        st.subheader("🗺️ Soil Fertility Across Soil Types")
        type_comp = soil_analytics.get_soil_type_comparisons()
        if not type_comp.empty:
            fig_type = px.bar(
                type_comp,
                x="soil_type",
                y=["avg_nitrogen", "avg_potassium"],
                barmode="group",
                labels={"value": "Nutrient Level (kg/ha)", "soil_type": "Soil Type", "variable": "Nutrient"},
                color_discrete_map={"avg_nitrogen": "#26734D", "avg_potassium": "#D69B36"},
            )
            fig_type = apply_agrisense_theme(fig_type, title="", y_title="kg / ha", height=310, show_legend=True)
            st.plotly_chart(fig_type, use_container_width=True)

    # ── Correlation Matrix ───────────────────────────────────────────────────
    st.subheader("📊 Soil Parameter Pearson Correlation Matrix")
    corr_df = soil_analytics.get_soil_correlation_matrix()
    if not corr_df.empty:
        fig_corr = px.imshow(
            corr_df,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=["#C65C50", "#FFFFFF", "#26734D"],
            labels=dict(color="Correlation"),
        )
        fig_corr = apply_agrisense_theme(fig_corr, title="", height=280, show_legend=False)
        st.plotly_chart(fig_corr, use_container_width=True)

    # ── Lab Records Filter & Data Table ──────────────────────────────────────
    st.subheader("📋 Soil Laboratory Analysis Records")
    if not farms_df.empty and "farm_id" in farms_df.columns:
        enriched_soil = soil_df.merge(farms_df[["farm_id", "farm_name", "soil_type"]].drop_duplicates("farm_id"), on="farm_id", how="left")
    else:
        enriched_soil = soil_df.copy()

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        ph_filter = st.selectbox("Filter by pH Classification", ["All Bands"] + sorted(ph_df["ph_band"].unique().tolist()) if not ph_df.empty else ["All Bands"])
    with f_col2:
        soil_type_filter = st.selectbox("Filter by Soil Type", ["All Types"] + sorted(enriched_soil["soil_type"].dropna().unique().tolist()) if "soil_type" in enriched_soil.columns else ["All Types"])

    filtered_soil = enriched_soil.copy()
    filtered_soil["ph_classification"] = filtered_soil["ph"].apply(classify_soil_ph)

    if ph_filter != "All Bands":
        filtered_soil = filtered_soil[filtered_soil["ph_classification"] == ph_filter]
    if soil_type_filter != "All Types" and "soil_type" in filtered_soil.columns:
        filtered_soil = filtered_soil[filtered_soil["soil_type"] == soil_type_filter]

    rename_soil = {
        "soil_record_id": "Lab Record ID",
        "farm_id": "Farm ID",
        "farm_name": "Farm",
        "soil_type": "Soil Type",
        "record_date": "Test Date",
        "ph": "pH",
        "ph_classification": "Classification",
        "nitrogen": "Nitrogen (kg/ha)",
        "phosphorus": "Phosphorus (kg/ha)",
        "potassium": "Potassium (kg/ha)",
        moisture_col: "Moisture (%)",
        "organic_carbon": "OC (%)",
        "electrical_conductivity": "EC (dS/m)",
    }
    avail_cols = [c for c in rename_soil.keys() if c in filtered_soil.columns]
    disp_soil = filtered_soil[avail_cols].rename(columns=rename_soil)

    st.dataframe(disp_soil.head(150), use_container_width=True, hide_index=True)
    render_csv_export(disp_soil, "agrisense_soil_monitoring_data.csv", "📥 Export Soil Records (CSV)")
