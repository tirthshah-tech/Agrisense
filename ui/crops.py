"""
AgriSense - Crop Analytics View
Comprehensive agronomic crop comparison: cultivated area, total production,
yield per hectare benchmarks, water requirements, and crop performance matrix.
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
from repositories.crop_repository import CropRepository
from repositories.yield_repository import YieldRepository
from repositories.resource_repository import ResourceRepository
from services.crop_service import CropService
from analytics.crop_analytics import CropAnalytics


def render_crops_page() -> None:
    """Renders the comprehensive Crop Analytics view."""
    render_page_header(
        title="Crop Analytics & Agronomic Performance",
        subtitle="Botanical catalog, cultivation area comparisons, harvest production, and benchmark yield gap tracking.",
        sdg_label="SDG 2: Zero Hunger & Sustainable Crop Cultivation",
    )
    render_database_status_strip()

    crop_repo = CropRepository()
    crop_svc = CropService()
    crop_analytics = CropAnalytics()
    yield_repo = YieldRepository()
    res_repo = ResourceRepository()

    summary = crop_svc.get_crop_summary()
    crops_df = crop_repo.get_all_crops()
    cycles_df = crop_repo.get_cycles_enriched()
    yields_df = yield_repo.get_all_yields()
    irrig_df = res_repo.get_all_irrigation_records()
    fert_df = res_repo.get_all_fertilizer_records()

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    render_kpi(c1, "Crop Varieties", str(summary["total_crops"]), "Maharashtra Reference Catalog", icon="🌱", is_dark=True)
    render_kpi(c2, "Total Cycles Logged", str(summary["total_cycles"]), "Across All Seasons", icon="🔄")
    render_kpi(c3, "Active Cultivations", str(summary["active_cycles"]), "Currently In Field", icon="🌾")
    render_kpi(c4, "Harvested Cycles", str(summary["harvested_cycles"]), "Yield Analytics Completed", icon="📦")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 Multi-Crop Comparative Performance",
        "🌱 Botanical Crop Varieties Catalog",
        "🔄 Cultivation Cycle Registry",
    ])

    with tab1:
        # ── Cross-Crop Production & Acreage Comparison ────────────────────────
        cc1, cc2 = st.columns(2)

        with cc1:
            st.subheader("🗺️ Cultivated Acreage by Crop Variety")
            area_share_df = crop_analytics.get_crop_area_share()
            if not area_share_df.empty:
                fig_area = px.bar(
                    area_share_df,
                    x="cultivated_area",
                    y="crop_name",
                    orientation="h",
                    color="cultivated_area",
                    color_continuous_scale=["#E8EFE5", "#26734D"],
                    text_auto=".1f",
                    labels={"cultivated_area": "Cultivated Area (ha)", "crop_name": "Crop Variety"},
                )
                fig_area.update_coloraxes(showscale=False)
                fig_area = apply_agrisense_theme(fig_area, title="", x_title="Total Cultivated Area (ha)", height=320, show_legend=False)
                st.plotly_chart(fig_area, use_container_width=True)
            else:
                render_empty_state("Cultivated area distribution unavailable.")

        with cc2:
            st.subheader("📦 Total Production Output by Crop (Tonnes)")
            if not yields_df.empty and not cycles_df.empty:
                merged_y = yields_df.merge(cycles_df[["cycle_id", "crop_name"]].drop_duplicates("cycle_id"), on="cycle_id", how="inner")
                prod_by_crop = merged_y.groupby("crop_name")["yield_kg"].sum().reset_index()
                prod_by_crop["tonnes"] = (prod_by_crop["yield_kg"] / 1000.0).round(1)
                prod_by_crop = prod_by_crop.sort_values("tonnes", ascending=True)

                fig_prod = px.bar(
                    prod_by_crop,
                    x="tonnes",
                    y="crop_name",
                    orientation="h",
                    color="tonnes",
                    color_continuous_scale=["#E8EFE5", "#78A85A", "#173F35"],
                    text_auto=".1f",
                    labels={"tonnes": "Harvested Production (Metric Tonnes)", "crop_name": "Crop Variety"},
                )
                fig_prod.update_coloraxes(showscale=False)
                fig_prod = apply_agrisense_theme(fig_prod, title="", x_title="Total Production (Tonnes)", height=320, show_legend=False)
                st.plotly_chart(fig_prod, use_container_width=True)
            else:
                render_empty_state("Production statistics unavailable.")

        # ── Crop Growth Cycle Duration Boxplot / Stats ────────────────────────
        st.subheader("⏱️ Crop Cultivation Growth Duration (Days from Sowing to Harvest)")
        duration_stats = crop_analytics.get_cycle_duration_stats()
        if not duration_stats.empty:
            fig_dur = px.bar(
                duration_stats,
                x="crop_name",
                y="mean_days",
                error_y="std_days",
                color="crop_name",
                labels={"mean_days": "Mean Duration (Days)", "crop_name": "Crop", "std_days": "Std Deviation"},
                text_auto=".0f",
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_dur.update_traces(textposition="outside")
            fig_dur = apply_agrisense_theme(fig_dur, title="", y_title="Days to Harvest", height=310, show_legend=False)
            st.plotly_chart(fig_dur, use_container_width=True)

        # ── Multi-Input Performance Matrix ───────────────────────────────────
        st.subheader("📋 Crop Agronomic Performance Matrix")
        if not cycles_df.empty:
            # Aggregate area, yield, water, and fertilizer per crop
            area_agg = cycles_df.groupby("crop_name")["cultivated_area"].agg(
                cycles="count",
                total_area_ha="sum",
                avg_parcel_ha="mean",
            ).reset_index()

            yield_agg = pd.DataFrame()
            if not yields_df.empty:
                my = yields_df.merge(cycles_df[["cycle_id", "crop_name"]].drop_duplicates("cycle_id"), on="cycle_id", how="inner")
                yield_agg = my.groupby("crop_name").agg(
                    total_yield_tonnes=("yield_kg", lambda s: (s.sum() / 1000.0).round(1)),
                    mean_yield_kg_ha=("yield_per_hectare", lambda s: round(s.mean(), 1)),
                ).reset_index()

            matrix = area_agg.merge(yield_agg, on="crop_name", how="left") if not yield_agg.empty else area_agg
            matrix = matrix.merge(crops_df[["crop_name", "crop_category", "standard_yield_kg_per_ha", "water_requirement_mm"]], on="crop_name", how="left")

            rename_matrix = {
                "crop_name": "Crop Variety",
                "crop_category": "Category",
                "cycles": "Cycles Logged",
                "total_area_ha": "Total Area (ha)",
                "avg_parcel_ha": "Avg Parcel (ha)",
                "total_yield_tonnes": "Harvest (Tonnes)",
                "mean_yield_kg_ha": "Actual Yield (kg/ha)",
                "standard_yield_kg_per_ha": "Standard Benchmark (kg/ha)",
                "water_requirement_mm": "Water Req (mm)",
            }
            clean_matrix = matrix.rename(columns=rename_matrix)
            st.dataframe(clean_matrix, use_container_width=True, hide_index=True)
            render_csv_export(clean_matrix, "agrisense_crop_performance_matrix.csv", "📥 Export Crop Performance Matrix (CSV)")

    with tab2:
        st.subheader("🌱 Botanical & Agronomic Crop Catalog")
        if not crops_df.empty:
            st.dataframe(
                crops_df.rename(columns={
                    "crop_id": "Crop ID",
                    "crop_name": "Crop Name",
                    "crop_category": "Category",
                    "ideal_season": "Ideal Season",
                    "ideal_soil_type": "Ideal Soil",
                    "typical_growth_days": "Growth Days",
                    "water_requirement_mm": "Water Req (mm)",
                    "standard_yield_kg_per_ha": "Benchmark Yield (kg/ha)",
                }),
                use_container_width=True,
                hide_index=True,
            )
            render_csv_export(crops_df, "agrisense_crop_catalog.csv", "📥 Export Crop Catalog (CSV)")
        else:
            render_empty_state("Crop catalog is empty.")

    with tab3:
        st.subheader("🔄 Active & Historical Cultivation Cycles")
        if not cycles_df.empty:
            filter_crop = st.selectbox("Filter Cycles by Crop", ["All Crops"] + sorted(cycles_df["crop_name"].dropna().unique().tolist()))
            filtered_c = cycles_df if filter_crop == "All Crops" else cycles_df[cycles_df["crop_name"] == filter_crop]

            area_c = "cultivated_area" if "cultivated_area" in filtered_c.columns else "cultivated_area_hectares"
            disp_cols = ["cycle_id", "farm_name", "crop_name", "season_name", "sowing_date", "harvest_date", area_c, "status"]
            avail_disp = [c for c in disp_cols if c in filtered_c.columns]

            st.dataframe(
                filtered_c[avail_disp].rename(columns={
                    "cycle_id": "Cycle ID",
                    "farm_name": "Farm",
                    "crop_name": "Crop",
                    "season_name": "Season",
                    "sowing_date": "Sowing Date",
                    "harvest_date": "Harvest Date",
                    area_c: "Area (ha)",
                    "status": "Status",
                }),
                use_container_width=True,
                hide_index=True,
            )
            render_csv_export(filtered_c[avail_disp], "agrisense_cultivation_cycles.csv", "📥 Export Crop Cycles (CSV)")
        else:
            render_empty_state("No cultivation cycles found.")
