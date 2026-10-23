"""
AgriSense - Harvest Yield & Productivity Analytics View (SDG 2)
Evaluates crop harvest output, analyzes yield gap against reference standards,
and grades output quality across Maharashtra agricultural holdings.
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
from analytics.yield_analytics import YieldAnalytics
from repositories.yield_repository import YieldRepository
from repositories.crop_repository import CropRepository


def render_yield_page() -> None:
    """Renders the comprehensive Yield Analysis view."""
    render_page_header(
        title="Harvest Yield & Crop Productivity Analytics",
        subtitle="Evaluating crop harvest output, analyzing yield gap against agronomic standards, and quality grading.",
        sdg_label="SDG 2: Zero Hunger & Sustainable Agricultural Productivity",
    )
    render_database_status_strip()

    yield_analytics = YieldAnalytics()
    yield_repo = YieldRepository()
    crop_repo = CropRepository()

    yields_df = yield_repo.get_all_yields()
    crops_df = crop_repo.get_all_crops()
    cycles_df = crop_repo.get_cycles_enriched()

    if yields_df.empty:
        render_empty_state("No completed crop harvest yield records found.")
        return

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    total_harvests = len(yields_df)
    total_yield_tonnes = yields_df["yield_kg"].sum() / 1000.0
    mean_yield_ha = yields_df["yield_per_hectare"].mean()
    high_grade_pct = (yields_df["quality_grade"] == "Grade A").mean() * 100 if "quality_grade" in yields_df.columns else 0.0

    y1, y2, y3, y4 = st.columns(4)
    render_kpi(y1, "Harvest Records", f"{total_harvests:,}", "Completed field cycles", icon="📦", is_dark=True)
    render_kpi(y2, "Total Harvest Output", f"{total_yield_tonnes:,.1f} Tonnes", f"{total_yield_tonnes*10:,.0f} Quintals", icon="🌾")
    render_kpi(y3, "Mean Yield / Hectare", f"{mean_yield_ha:,.0f} kg/ha", "Across all crops", icon="📈")
    render_kpi(y4, "Premium Quality (Grade A)", f"{high_grade_pct:.1f}%", "Market standard", icon="🏅")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visual Analytics Row 1: Actual vs Benchmark & Quality Grades ─────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🌾 Actual vs Standard Benchmark Yield (kg / ha)")
        perf_df = yield_analytics.get_yield_performance_by_crop()
        if not perf_df.empty:
            fig_perf = px.bar(
                perf_df,
                x="crop_name",
                y=["mean_kg_ha", "standard_kg_ha"],
                barmode="group",
                labels={"value": "Yield (kg / ha)", "crop_name": "Crop Variety", "variable": "Metric"},
                color_discrete_map={"mean_kg_ha": "#26734D", "standard_kg_ha": "#D69B36"},
            )
            fig_perf.for_each_trace(lambda t: t.update(name="Actual Mean Yield" if t.name == "mean_kg_ha" else "Standard Benchmark"))
            fig_perf = apply_agrisense_theme(fig_perf, title="", y_title="Yield (kg / ha)", height=320, show_legend=True)
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            render_empty_state("Benchmark gap analytics unavailable.")

    with c2:
        st.subheader("🏅 Harvest Quality Grade Distribution")
        grade_df = yield_analytics.get_quality_grade_breakdown()
        if not grade_df.empty:
            grade_colors = {
                "Grade A": "#26734D",
                "Grade B": "#78A85A",
                "Grade C": "#D69B36",
                "Grade D": "#C65C50",
            }
            fig_grade = px.pie(
                grade_df,
                names="quality_grade",
                values="count",
                color="quality_grade",
                color_discrete_map=grade_colors,
                hole=0.45,
            )
            fig_grade.update_traces(textposition="outside", textinfo="percent+label")
            fig_grade = apply_agrisense_theme(fig_grade, title="", height=320, show_legend=False)
            st.plotly_chart(fig_grade, use_container_width=True)

    # ── Visual Analytics Row 2: Seasonal Yield & Top Farm Rankings ───────────
    c3, c4 = st.columns(2)
    enriched_yields = yield_analytics.get_enriched_yields()

    with c3:
        st.subheader("⛅ Seasonal Harvest Output (Metric Tonnes)")
        if not enriched_yields.empty and "season_name" in enriched_yields.columns:
            season_yield = enriched_yields.groupby("season_name")["yield_kg"].sum().reset_index()
            season_yield["tonnes"] = (season_yield["yield_kg"] / 1000.0).round(1)
            fig_season = px.bar(
                season_yield,
                x="season_name",
                y="tonnes",
                color="season_name",
                text="tonnes",
                labels={"season_name": "Agricultural Season", "tonnes": "Harvest (Tonnes)"},
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_season.update_traces(texttemplate="%{text:,.0f} T", textposition="outside")
            fig_season = apply_agrisense_theme(fig_season, title="", y_title="Tonnes", height=310, show_legend=False)
            st.plotly_chart(fig_season, use_container_width=True)

    with c4:
        st.subheader("🏆 Top Performing Farms by Mean Productivity")
        if not enriched_yields.empty and "farm_name" in enriched_yields.columns:
            top_farms = enriched_yields.groupby("farm_name")["yield_per_hectare"].mean().reset_index()
            top_farms = top_farms.sort_values("yield_per_hectare", ascending=False).head(8)
            fig_farm = px.bar(
                top_farms.sort_values("yield_per_hectare", ascending=True),
                x="yield_per_hectare",
                y="farm_name",
                orientation="h",
                color="yield_per_hectare",
                color_continuous_scale=["#E8EFE5", "#26734D"],
                text_auto=".0f",
                labels={"yield_per_hectare": "Yield (kg / ha)", "farm_name": "Farm"},
            )
            fig_farm.update_coloraxes(showscale=False)
            fig_farm = apply_agrisense_theme(fig_farm, title="", x_title="Mean Yield (kg / ha)", height=310, show_legend=False)
            st.plotly_chart(fig_farm, use_container_width=True)

    # ── Completed Harvest Yield Log Table & Export ────────────────────────────
    st.subheader("📋 Completed Harvest Yield Records")
    if not enriched_yields.empty:
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            c_list = ["All Crops"] + sorted(enriched_yields["crop_name"].dropna().unique().tolist()) if "crop_name" in enriched_yields.columns else ["All Crops"]
            sel_c = st.selectbox("Filter Harvests by Crop", c_list)
        with filter_col2:
            g_list = ["All Grades"] + sorted(enriched_yields["quality_grade"].dropna().unique().tolist()) if "quality_grade" in enriched_yields.columns else ["All Grades"]
            sel_g = st.selectbox("Filter Harvests by Quality Grade", g_list)

        filtered_y = enriched_yields.copy()
        if sel_c != "All Crops" and "crop_name" in filtered_y.columns:
            filtered_y = filtered_y[filtered_y["crop_name"] == sel_c]
        if sel_g != "All Grades" and "quality_grade" in filtered_y.columns:
            filtered_y = filtered_y[filtered_y["quality_grade"] == sel_g]

        disp_cols = ["yield_id", "farm_name", "crop_name", "season_name", "harvest_date", "yield_kg", "yield_per_hectare", "quality_grade"]
        avail_cols = [c for c in disp_cols if c in filtered_y.columns]
        rename_y = {
            "yield_id": "Yield ID",
            "farm_name": "Farm",
            "crop_name": "Crop",
            "season_name": "Season",
            "harvest_date": "Harvest Date",
            "yield_kg": "Total Yield (kg)",
            "yield_per_hectare": "Yield (kg/ha)",
            "quality_grade": "Quality Grade",
        }
        disp_df = filtered_y[avail_cols].rename(columns=rename_y)
        st.dataframe(disp_df.head(150), use_container_width=True, hide_index=True)

        render_csv_export(disp_df, "agrisense_harvest_yield_data.csv", "📥 Export Harvest Yield Data (CSV)")
