"""
AgriSense - Resource Efficiency & Agricultural Productivity View (SDG 12 & SDG 2)
Evaluates Water Productivity (kg/m3), Fertilizer Productivity (kg/kg), Land Productivity (kg/ha),
and comparative input efficiency benchmarks without machine learning.
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
from analytics.resource_analytics import ResourceAnalytics


def render_resource_efficiency_page() -> None:
    """Renders the comprehensive Resource Efficiency analytics view."""
    render_page_header(
        title="Resource Efficiency & Input Productivity",
        subtitle="Evaluating crop harvest output per unit of water, fertilizer, and arable land under UN SDG 12 & SDG 2.",
        sdg_label="SDG 12: Sustainable Resource Consumption • SDG 2: Agricultural Productivity",
    )
    render_database_status_strip()

    analytics = ResourceAnalytics()
    master_df = analytics.get_resource_efficiency_master_table()

    if master_df.empty:
        render_empty_state("No completed crop harvest and input application records available for efficiency analysis.")
        return

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    total_cycles = len(master_df)
    avg_land_prod = master_df["land_productivity_kg_ha"].mean()
    avg_water_prod = master_df[master_df["water_productivity_kg_m3"] > 0]["water_productivity_kg_m3"].mean()
    avg_fert_prod = master_df[master_df["fert_productivity_kg_kg"] > 0]["fert_productivity_kg_kg"].mean()
    top_water_crop = master_df.groupby("crop_name")["water_productivity_kg_m3"].mean().idxmax() if not master_df.empty else "N/A"

    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "Harvest Cycles Evaluated", f"{total_cycles:,}", "Completed field records", icon="🔄", is_dark=True)
    render_kpi(k2, "Mean Land Productivity", f"{avg_land_prod:,.0f} kg/ha", "Across all crops", icon="🌱")
    render_kpi(k3, "Mean Water Productivity", f"{avg_water_prod:.2f} kg/m³", f"Top: {top_water_crop}", icon="💧")
    render_kpi(k4, "Mean Fertilizer Productivity", f"{avg_fert_prod:.1f} kg/kg", "Harvest output / input kg", icon="🌿")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visualizations Row 1: Water & Fertilizer Productivity Ratios ─────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("💧 Crop Water Productivity (kg yield per m³ water)")
        water_prod_df = analytics.get_water_productivity_ratio()
        if not water_prod_df.empty:
            fig_wp = px.bar(
                water_prod_df,
                x="avg_kg_per_m3",
                y="crop_name",
                orientation="h",
                color="avg_kg_per_m3",
                color_continuous_scale=["#E8EFE5", "#26734D"],
                text_auto=".2f",
                labels={"avg_kg_per_m3": "Water Productivity (kg / m³)", "crop_name": "Crop Variety"},
            )
            fig_wp.update_coloraxes(showscale=False)
            fig_wp = apply_agrisense_theme(fig_wp, title="", x_title="kg yield / m³ water consumed", height=320, show_legend=False)
            st.plotly_chart(fig_wp, use_container_width=True)
        else:
            render_empty_state("Water productivity metrics unavailable.")

    with c2:
        st.subheader("🌿 Fertilizer Productivity (kg yield per kg fertilizer)")
        fert_prod_df = analytics.get_fertilizer_productivity_ratio()
        if not fert_prod_df.empty:
            fig_fp = px.bar(
                fert_prod_df,
                x="avg_kg_per_kg_fert",
                y="crop_name",
                orientation="h",
                color="avg_kg_per_kg_fert",
                color_continuous_scale=["#E8EFE5", "#D69B36", "#173F35"],
                text_auto=".1f",
                labels={"avg_kg_per_kg_fert": "Fertilizer Productivity (kg / kg)", "crop_name": "Crop Variety"},
            )
            fig_fp.update_coloraxes(showscale=False)
            fig_fp = apply_agrisense_theme(fig_fp, title="", x_title="kg yield / kg fertilizer applied", height=320, show_legend=False)
            st.plotly_chart(fig_fp, use_container_width=True)
        else:
            render_empty_state("Fertilizer productivity metrics unavailable.")

    # ── Visualizations Row 2: Irrigation Method & Resource Intensity ─────────
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("🚿 Water Application Intensity by Irrigation Method")
        method_df = analytics.get_water_efficiency_by_method()
        if not method_df.empty:
            fig_method = px.bar(
                method_df,
                x="irrigation_method",
                y="mean_m3_ha",
                color="irrigation_method",
                text_auto=".1f",
                labels={"irrigation_method": "Irrigation Method", "mean_m3_ha": "Mean Water (m³ / ha)"},
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_method.update_traces(textposition="outside")
            fig_method = apply_agrisense_theme(fig_method, title="", y_title="Water Intensity (m³ / ha)", height=320, show_legend=False)
            st.plotly_chart(fig_method, use_container_width=True)
        else:
            render_empty_state("Irrigation method comparison unavailable.")

    with c4:
        st.subheader("📊 Resource Intensity Correlation (Water vs Fertilizer)")
        if not master_df.empty:
            fig_scatter = px.scatter(
                master_df,
                x="water_per_ha_m3",
                y="fert_per_ha_kg",
                color="crop_name",
                size="land_productivity_kg_ha",
                hover_data=["farm_name", "primary_method"],
                labels={
                    "water_per_ha_m3": "Water Intensity (m³ / ha)",
                    "fert_per_ha_kg": "Fertilizer Intensity (kg / ha)",
                    "crop_name": "Crop",
                    "land_productivity_kg_ha": "Yield (kg/ha)",
                },
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_scatter = apply_agrisense_theme(fig_scatter, title="", height=320, show_legend=True)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            render_empty_state("Intensity correlation data unavailable.")

    # ── Methodological Documentation & Formula Limitations ─────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="content-card">
            <h3>📐 Agronomic Formulas, Definitions &amp; Analytical Limitations</h3>
            <div style="font-size: 0.85rem; color: #3C4A42; line-height: 1.7;">
                <p><strong>Strict Analytical Guardrails:</strong> AgriSense computes all productivity ratios deterministically from real field logs without predictive AI models. Interpret ratios with the following agronomic constraints:</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin-top: 10px;">
                    <div style="background: #F7F8F3; padding: 12px; border-radius: 8px; border-left: 3px solid #26734D;">
                        <strong style="color: #173F35;">Water Productivity (WP)</strong><br>
                        <code>WP = Yield (kg) / Water Consumed (m³)</code><br>
                        <span style="font-size: 0.78rem; color: #738078;">
                        • <em>Limitation:</em> Measures applied irrigation water only. Effective precipitation contribution is unaccounted for in single-meter readings.
                        </span>
                    </div>
                    <div style="background: #F7F8F3; padding: 12px; border-radius: 8px; border-left: 3px solid #D69B36;">
                        <strong style="color: #173F35;">Fertilizer Productivity (FP)</strong><br>
                        <code>FP = Yield (kg) / Fertilizer Input (kg)</code><br>
                        <span style="font-size: 0.78rem; color: #738078;">
                        • <em>Limitation:</em> Ratios vary widely between high-biomass perennials (e.g. Sugarcane) and pulses due to biological nitrogen fixation.
                        </span>
                    </div>
                    <div style="background: #F7F8F3; padding: 12px; border-radius: 8px; border-left: 3px solid #2A9D8F;">
                        <strong style="color: #173F35;">Land Productivity (LP)</strong><br>
                        <code>LP = Harvested Yield (kg) / Area (ha)</code><br>
                        <span style="font-size: 0.78rem; color: #738078;">
                        • <em>Principle:</em> Correlation between input intensity and yield does not prove agronomic causation without controlled parcel trials.
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Master Efficiency Audit Table ─────────────────────────────────────────
    st.subheader("📋 Cultivation Cycle Resource Efficiency Log")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        crop_filter = st.selectbox("Filter by Crop Variety", ["All Crops"] + sorted(master_df["crop_name"].dropna().unique().tolist()))
    with filter_col2:
        method_filter = st.selectbox("Filter by Primary Irrigation Method", ["All Methods"] + sorted(master_df["primary_method"].dropna().unique().tolist()))

    filtered_table = master_df.copy()
    if crop_filter != "All Crops":
        filtered_table = filtered_table[filtered_table["crop_name"] == crop_filter]
    if method_filter != "All Methods":
        filtered_table = filtered_table[filtered_table["primary_method"] == method_filter]

    rename_cols = {
        "cycle_id": "Cycle ID",
        "farm_name": "Farm",
        "crop_name": "Crop",
        "season_name": "Season",
        "area_ha": "Area (ha)",
        "yield_kg": "Harvest (kg)",
        "land_productivity_kg_ha": "Yield (kg/ha)",
        "total_water_liters": "Water (L)",
        "water_per_ha_m3": "Water (m³/ha)",
        "water_productivity_kg_m3": "Water Prod (kg/m³)",
        "primary_method": "Irrigation Method",
        "total_fertilizer_kg": "Fertilizer (kg)",
        "fert_per_ha_kg": "Fert (kg/ha)",
        "fert_productivity_kg_kg": "Fert Prod (kg/kg)",
        "quality_grade": "Grade",
    }
    display_df = filtered_table.rename(columns={k: v for k, v in rename_cols.items() if k in filtered_table.columns})
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # CSV Export
    render_csv_export(display_df, "agrisense_resource_efficiency_report.csv", "📥 Export Resource Efficiency Report (CSV)")
