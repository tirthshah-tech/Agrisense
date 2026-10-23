"""
AgriSense - Executive Agricultural Analytics Dashboard
Modern Botanical Intelligence UI featuring:
- High-resolution agricultural hero visual with dark-forest overlay and CSS fallback
- Global multidimensional filter bar (Year, Season, Crop, District, Farm) with Reset
- Dynamically calculated primary & secondary KPI strips
- Interactive Plotly visualizations (Crop Productivity & Water Stewardship)
- Dynamic Data-Driven Insights panel & Recent Rule-Based Alerts
- UN SDG 2 & SDG 12 Impact Alignment panel
- CSV Export for operational dashboard data
"""
from typing import Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from ui.components import (
    render_hero_header,
    render_kpi,
    render_database_status_strip,
    apply_agrisense_theme,
    render_csv_export,
    render_empty_state,
    render_insights_panel,
    AGRI_COLOR_SEQUENCE,
    AGRI_PALETTE,
)
from repositories.crop_repository import CropRepository
from repositories.farm_repository import FarmRepository
from repositories.farmer_repository import FarmerRepository
from repositories.resource_repository import ResourceRepository
from repositories.soil_repository import SoilRepository
from repositories.yield_repository import YieldRepository
from repositories.observation_repository import ObservationRepository
from services.alert_service import AlertService


def render_dashboard() -> None:
    """Renders the executive AgriSense dashboard with global interactive filters."""
    # ── 1. Hero Welcome Header & System Status ────────────────────────────────
    render_hero_header()
    render_database_status_strip()

    # ── 2. Data Ingestion from Repositories ───────────────────────────────────
    crop_repo = CropRepository()
    farm_repo = FarmRepository()
    farmer_repo = FarmerRepository()
    res_repo = ResourceRepository()
    soil_repo = SoilRepository()
    yield_repo = YieldRepository()
    obs_repo = ObservationRepository()
    alert_svc = AlertService()

    cycles_df = crop_repo.get_cycles_enriched()
    farms_df = farm_repo.get_all_farms()
    farmers_df = farmer_repo.get_all_farmers()
    yields_df = yield_repo.get_all_yields()
    irrig_df = res_repo.get_all_irrigation_records()
    fert_df = res_repo.get_all_fertilizer_records()
    soil_df = soil_repo.get_all_soil_records()
    alerts_df = obs_repo.get_agricultural_alerts()

    # Enrich farms with district from farmers
    if not farms_df.empty and not farmers_df.empty and "farmer_id" in farms_df.columns:
        farms_df = farms_df.merge(farmers_df[["farmer_id", "district", "village"]], on="farmer_id", how="left")

    # Enrich cycles with district
    if not cycles_df.empty and not farms_df.empty and "district" not in cycles_df.columns:
        cycles_df = cycles_df.merge(farms_df[["farm_id", "district"]].drop_duplicates("farm_id"), on="farm_id", how="left")

    # ── 3. Global Filter Strip ────────────────────────────────────────────────
    st.markdown(
        """
        <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #173F35; margin-bottom: 0.4rem;">
            🔍 Global Multidimensional Agricultural Filters
        </div>
        """,
        unsafe_allow_html=True,
    )

    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([1.5, 1.5, 1.5, 1.5, 1.0])

    # Extract filter options
    years = ["All Years"]
    if not cycles_df.empty and "year" in cycles_df.columns:
        avail_years = sorted([int(y) for y in cycles_df["year"].dropna().unique() if y > 0])
        years += [str(y) for y in avail_years]

    seasons = ["All Seasons"]
    if not cycles_df.empty and "season_name" in cycles_df.columns:
        seasons += sorted([s for s in cycles_df["season_name"].dropna().unique() if s != "Unknown"])

    crops = ["All Crops"]
    if not cycles_df.empty and "crop_name" in cycles_df.columns:
        crops += sorted(cycles_df["crop_name"].dropna().unique().tolist())

    districts = ["All Districts"]
    if not farms_df.empty and "district" in farms_df.columns:
        districts += sorted(farms_df["district"].dropna().unique().tolist())

    with f_col1:
        sel_year = st.selectbox("Year", years, key="dash_filter_year")
    with f_col2:
        sel_season = st.selectbox("Season", seasons, key="dash_filter_season")
    with f_col3:
        sel_crop = st.selectbox("Crop Variety", crops, key="dash_filter_crop")
    with f_col4:
        sel_district = st.selectbox("District", districts, key="dash_filter_district")
    with f_col5:
        st.write("")
        st.write("")
        reset_clicked = st.button("↺ Reset", key="dash_reset_filters")
        if reset_clicked:
            st.session_state["dash_filter_year"] = "All Years"
            st.session_state["dash_filter_season"] = "All Seasons"
            st.session_state["dash_filter_crop"] = "All Crops"
            st.session_state["dash_filter_district"] = "All Districts"
            st.rerun()

    # ── Apply Filters to Datasets ─────────────────────────────────────────────
    filtered_cycles = cycles_df.copy() if not cycles_df.empty else pd.DataFrame()
    filtered_farms = farms_df.copy() if not farms_df.empty else pd.DataFrame()

    if not filtered_cycles.empty:
        if sel_year != "All Years" and "year" in filtered_cycles.columns:
            filtered_cycles = filtered_cycles[filtered_cycles["year"].astype(str) == sel_year]
        if sel_season != "All Seasons" and "season_name" in filtered_cycles.columns:
            filtered_cycles = filtered_cycles[filtered_cycles["season_name"] == sel_season]
        if sel_crop != "All Crops" and "crop_name" in filtered_cycles.columns:
            filtered_cycles = filtered_cycles[filtered_cycles["crop_name"] == sel_crop]
        if sel_district != "All Districts" and "district" in filtered_cycles.columns:
            filtered_cycles = filtered_cycles[filtered_cycles["district"] == sel_district]

    if not filtered_farms.empty and sel_district != "All Districts" and "district" in filtered_farms.columns:
        filtered_farms = filtered_farms[filtered_farms["district"] == sel_district]

    # Map filtered cycles into yields, irrigation, and fertilizer
    filtered_cycle_ids = set(filtered_cycles["cycle_id"]) if not filtered_cycles.empty else set()
    filtered_farm_ids = set(filtered_cycles["farm_id"]).union(set(filtered_farms["farm_id"])) if not filtered_farms.empty else set()

    filtered_yields = yields_df[yields_df["cycle_id"].isin(filtered_cycle_ids)] if not yields_df.empty and filtered_cycle_ids else yields_df
    filtered_irrig = irrig_df[irrig_df["cycle_id"].isin(filtered_cycle_ids)] if not irrig_df.empty and filtered_cycle_ids else irrig_df
    filtered_fert = fert_df[fert_df["cycle_id"].isin(filtered_cycle_ids)] if not fert_df.empty and filtered_cycle_ids else fert_df
    filtered_soil = soil_df[soil_df["farm_id"].isin(filtered_farm_ids)] if not soil_df.empty and filtered_farm_ids else soil_df
    filtered_alerts = alerts_df[alerts_df["farm_id"].isin(filtered_farm_ids)] if not alerts_df.empty and filtered_farm_ids else alerts_df

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4. Primary KPI Strip ──────────────────────────────────────────────────
    k_farms = len(filtered_farm_ids) if filtered_farm_ids else (len(filtered_farms) if not filtered_farms.empty else 0)
    area_col = "cultivated_area" if "cultivated_area" in filtered_cycles.columns else "cultivated_area_hectares"
    k_area = filtered_cycles[area_col].sum() if not filtered_cycles.empty and area_col in filtered_cycles.columns else 0.0

    k_prod_tonnes = (filtered_yields["yield_kg"].sum() / 1000.0) if not filtered_yields.empty else 0.0
    k_avg_yield = filtered_yields["yield_per_hectare"].mean() if not filtered_yields.empty else 0.0

    k_water_m3 = (filtered_irrig["water_used_liters"].sum() / 1000.0) if not filtered_irrig.empty else 0.0
    k_fert_tonnes = (filtered_fert["quantity_kg"].sum() / 1000.0) if not filtered_fert.empty else 0.0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    render_kpi(k1, "Farms Monitored", f"{k_farms:,}", f"In {sel_district if sel_district != 'All Districts' else 'Maharashtra'}", icon="🏡", is_dark=True)
    render_kpi(k2, "Cultivated Area", f"{k_area:,.1f} ha", f"Cycles: {len(filtered_cycles):,}", icon="🗺️")
    render_kpi(k3, "Total Crop Production", f"{k_prod_tonnes:,.1f} T", f"{k_prod_tonnes*10:,.0f} Quintals", icon="🌾")
    render_kpi(k4, "Mean Yield / Hectare", f"{k_avg_yield:,.0f} kg/ha", "Across harvests", icon="📈")
    render_kpi(k5, "Water Consumed", f"{k_water_m3:,.0f} m³", f"Events: {len(filtered_irrig):,}", icon="💧")
    render_kpi(k6, "Fertilizer Input", f"{k_fert_tonnes:,.1f} T", f"Events: {len(filtered_fert):,}", icon="🌿")

    # ── Secondary Monitoring Strip ────────────────────────────────────────────
    moisture_col = "moisture_percentage" if "moisture_percentage" in filtered_soil.columns else "moisture"
    s_moist = filtered_soil[moisture_col].mean() if not filtered_soil.empty and moisture_col in filtered_soil.columns else 0.0
    s_ph = filtered_soil["ph"].mean() if not filtered_soil.empty and "ph" in filtered_soil.columns else 0.0
    s_crops_count = filtered_cycles["crop_name"].nunique() if not filtered_cycles.empty and "crop_name" in filtered_cycles.columns else 0
    s_open_alerts = len(filtered_alerts[filtered_alerts["status"] == "Open"]) if not filtered_alerts.empty and "status" in filtered_alerts.columns else len(filtered_alerts)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    sk1, sk2, sk3, sk4 = st.columns(4)
    render_kpi(sk1, "Active Alerts", f"{s_open_alerts:,}", "Requires attention", icon="🚨")
    render_kpi(sk2, "Mean Soil Moisture", f"{s_moist:.1f}%", "Target: 25% – 50%", icon="🧪")
    render_kpi(sk3, "Mean Soil pH", f"{s_ph:.2f}", "Target: 6.5 – 7.5", icon="⚖️")
    render_kpi(sk4, "Crop Varieties", f"{s_crops_count}", "In field cycle", icon="🌱")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 5. Main Visualizations Row ────────────────────────────────────────────
    v_col1, v_col2 = st.columns(2)

    with v_col1:
        st.subheader("🌾 Crop Productivity (Yield per Hectare)")
        if not filtered_yields.empty and not filtered_cycles.empty:
            merged_yield = filtered_yields.merge(
                filtered_cycles[["cycle_id", "crop_name", "crop_category"]].drop_duplicates("cycle_id"),
                on="cycle_id",
                how="inner",
            )
            if not merged_yield.empty:
                yield_by_crop = merged_yield.groupby("crop_name").agg(
                    mean_yield=("yield_per_hectare", "mean"),
                    total_output=("yield_kg", "sum"),
                    cycles=("cycle_id", "count"),
                ).reset_index().sort_values("mean_yield", ascending=True)

                fig_yield = px.bar(
                    yield_by_crop,
                    x="mean_yield",
                    y="crop_name",
                    orientation="h",
                    color="mean_yield",
                    color_continuous_scale=["#E8EFE5", "#26734D", "#173F35"],
                    labels={"mean_yield": "Mean Yield (kg / ha)", "crop_name": "Crop"},
                    text_auto=".0f",
                )
                fig_yield.update_coloraxes(showscale=False)
                fig_yield = apply_agrisense_theme(fig_yield, title="", x_title="Mean Yield (kg / ha)", height=320, show_legend=False)
                st.plotly_chart(fig_yield, use_container_width=True)
            else:
                render_empty_state("No harvested yield records match current filters.")
        else:
            render_empty_state("No yield records available for selected criteria.")

    with v_col2:
        st.subheader("💧 Water Consumption by Irrigation Method")
        if not filtered_irrig.empty and "irrigation_method" in filtered_irrig.columns:
            water_by_method = filtered_irrig.groupby("irrigation_method").agg(
                total_m3=("water_used_liters", lambda s: s.sum() / 1000.0),
                events=("irrigation_id", "count"),
            ).reset_index()

            fig_water = px.pie(
                water_by_method,
                names="irrigation_method",
                values="total_m3",
                hole=0.48,
                color="irrigation_method",
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_water.update_traces(textposition="outside", textinfo="percent+label")
            fig_water = apply_agrisense_theme(fig_water, title="", height=320, show_legend=False)
            st.plotly_chart(fig_water, use_container_width=True)
        else:
            render_empty_state("No irrigation records available for selected criteria.")

    # ── 6. Secondary Row: Soil Health Radar + Cycle Lifecycle Status ─────────
    s_col1, s_col2 = st.columns(2)

    with s_col1:
        st.subheader("🧪 Soil Chemical Health Index")
        if not filtered_soil.empty:
            avg_n = filtered_soil["nitrogen"].mean() if "nitrogen" in filtered_soil.columns else 250.0
            avg_p = filtered_soil["phosphorus"].mean() if "phosphorus" in filtered_soil.columns else 18.0
            avg_k = filtered_soil["potassium"].mean() if "potassium" in filtered_soil.columns else 210.0
            avg_m = s_moist
            avg_ph_val = s_ph

            soil_radar_data = {
                "Metric": ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "Moisture", "pH Neutrality"],
                "Index": [
                    min((avg_n / 350.0) * 100, 100),
                    min((avg_p / 25.0) * 100, 100),
                    min((avg_k / 300.0) * 100, 100),
                    min((avg_m / 45.0) * 100, 100),
                    min(max(100 - abs(avg_ph_val - 7.0) * 40, 20), 100),
                ]
            }
            fig_radar = go.Figure(go.Scatterpolar(
                r=soil_radar_data["Index"],
                theta=soil_radar_data["Metric"],
                fill="toself",
                fillcolor="rgba(120, 168, 90, 0.25)",
                line=dict(color=AGRI_PALETTE["primary_green"], width=2),
                marker=dict(color=AGRI_PALETTE["deep_forest"], size=6),
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9, family="Manrope")),
                    angularaxis=dict(tickfont=dict(size=11, family="Manrope")),
                ),
                height=300,
                margin=dict(l=35, r=35, t=25, b=25),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            render_empty_state("Soil laboratory observations unavailable.")

    with s_col2:
        st.subheader("🔄 Cultivation Lifecycle Status")
        if not filtered_cycles.empty and "status" in filtered_cycles.columns:
            status_df = filtered_cycles["status"].value_counts().reset_index()
            status_df.columns = ["status", "count"]

            status_colors = {
                "Active": AGRI_PALETTE["primary_green"],
                "Harvested": AGRI_PALETTE["fresh_leaf"],
                "Planned": AGRI_PALETTE["muted_amber"],
                "Failed": AGRI_PALETTE["muted_red"],
            }
            fig_status = px.bar(
                status_df,
                x="status",
                y="count",
                color="status",
                text="count",
                color_discrete_map=status_colors,
                labels={"status": "Lifecycle Stage", "count": "Cycles"},
            )
            fig_status.update_traces(textposition="outside")
            fig_status = apply_agrisense_theme(fig_status, title="", y_title="Number of Cycles", height=300, show_legend=False)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            render_empty_state("Crop lifecycle distribution unavailable.")

    # ── 7. Dynamic Data-Driven Insights & Alert Engine ────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    insights = alert_svc.get_dynamic_insights()
    render_insights_panel(insights)

    # ── 8. Recent Rule-Based Agricultural Alerts Table ────────────────────────
    st.subheader("🚨 Field Rule Alerts & Operational Exceptions")
    if not filtered_alerts.empty:
        display_alerts = filtered_alerts.head(8)[
            [c for c in ["alert_id", "farm_id", "alert_type", "severity", "trigger_rule", "metric_value", "threshold_value", "status", "timestamp"] if c in filtered_alerts.columns]
        ].rename(columns={
            "alert_id": "Alert ID",
            "farm_id": "Farm ID",
            "alert_type": "Alert Rule",
            "severity": "Severity",
            "trigger_rule": "Trigger Rule Condition",
            "metric_value": "Observed Metric",
            "threshold_value": "Threshold Bound",
            "status": "Status",
            "timestamp": "Date",
        })
        st.dataframe(display_alerts, use_container_width=True, hide_index=True)
    else:
        st.info("No active alerts detected for current filter selection.")

    # ── 9. UN Sustainable Development Goals (SDG) Alignment ───────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="content-card">
            <h3>🌐 Sustainable Development Goals Alignment</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 10px;">
                <div style="background: #F7F8F3; padding: 14px; border-radius: 10px; border-left: 4px solid #26734D;">
                    <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #173F35; margin-bottom: 6px;">
                        <span>🎯</span> SDG 2 — Zero Hunger (Food Security &amp; Crop Productivity)
                    </div>
                    <div style="font-size: 0.83rem; color: #3C4A42; line-height: 1.6;">
                        • <strong>Yield Gap Benchmarking:</strong> Compares field harvest kilograms against agricultural research benchmarks to identify yield shortfalls early.<br>
                        • <strong>Soil Fertility Preservation:</strong> Tracks chemical macro-nutrient deficiencies (NPK) and pH bounds to prevent land degradation.
                    </div>
                </div>
                <div style="background: #F7F8F3; padding: 14px; border-radius: 10px; border-left: 4px solid #78A85A;">
                    <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #173F35; margin-bottom: 6px;">
                        <span>🌱</span> SDG 12 — Responsible Consumption &amp; Production
                    </div>
                    <div style="font-size: 0.83rem; color: #3C4A42; line-height: 1.6;">
                        • <strong>Water Footprint Analytics:</strong> Quantifies irrigation volume applied per kilogram of harvested food, demonstrating the efficiency disparity between Drip and Flood.<br>
                        • <strong>Agrochemical Intensity:</strong> Tracks chemical dosages to prevent over-fertilization, soil toxicity, and agrochemical runoff.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 10. Dashboard Operational Data CSV Export ────────────────────────────
    if not filtered_cycles.empty:
        dash_export_cols = [c for c in ["cycle_id", "farm_id", "crop_name", "season_name", "year", area_col, "status", "district"] if c in filtered_cycles.columns]
        render_csv_export(filtered_cycles[dash_export_cols], "agrisense_dashboard_summary.csv", "📥 Export Filtered Dashboard Data (CSV)")
