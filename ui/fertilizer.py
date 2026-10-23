"""
AgriSense - Fertilizer Usage & Agrochemical Intensity View (SDG 12)
Monitors chemical and organic fertilizer application, dosage rates per hectare,
application methods, and balanced crop nutrition.
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
)
from services.resource_service import ResourceService
from repositories.resource_repository import ResourceRepository
from repositories.crop_repository import CropRepository
from repositories.farm_repository import FarmRepository


def render_fertilizer_page() -> None:
    """Renders the Fertilizer Usage analytics view."""
    render_page_header(
        title="Fertilizer Usage & Agrochemical Intensity",
        subtitle="Tracking agrochemical inputs, dosage benchmarks per hectare, and balanced crop nutrition under SDG 12.",
        sdg_label="SDG 12: Responsible Agrochemical Management & Pollution Prevention",
    )
    render_database_status_strip()

    res_svc = ResourceService()
    res_repo = ResourceRepository()
    crop_repo = CropRepository()
    farm_repo = FarmRepository()

    metrics = res_svc.get_fertilizer_metrics()
    fert_df = res_repo.get_all_fertilizer_records()
    cycles_df = crop_repo.get_cycles_enriched()
    farms_df = farm_repo.get_all_farms()

    if fert_df.empty:
        render_empty_state("No fertilizer application records available.")
        return

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    total_fert_kg = metrics["total_fertilizer_kg"]
    total_apps = metrics["total_applications"]
    avg_dosage = metrics["avg_qty_kg"]

    f1, f2, f3, f4 = st.columns(4)
    render_kpi(f1, "Total Fertilizer Applied", f"{total_fert_kg:,.0f} kg", f"{(total_fert_kg/1000.0):,.1f} Metric Tonnes", icon="🌿", is_dark=True)
    render_kpi(f2, "Dosage Events", f"{total_apps:,}", "Applications logged", icon="🚜")
    render_kpi(f3, "Mean / Application", f"{avg_dosage:.1f} kg", "Per cycle dosage", icon="⚖️")
    render_kpi(f4, "Primary N Source", "Urea (46% N)", "Highest Volume", icon="🌱")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visual Analytics Row 1: Fertilizer by Type & Application Method ───────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🌿 Fertilizer Consumption by Chemical Type")
        fert_type_df = res_svc.get_fertilizer_by_type()
        if not fert_type_df.empty:
            fig_fert = px.bar(
                fert_type_df,
                x="fertilizer_type",
                y="total_kg",
                color="fertilizer_type",
                text="total_kg",
                labels={"fertilizer_type": "Fertilizer Type", "total_kg": "Total Quantity (kg)"},
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_fert.update_traces(texttemplate="%{text:,.0f} kg", textposition="outside")
            fig_fert = apply_agrisense_theme(fig_fert, title="", y_title="Quantity (kg)", height=320, show_legend=False)
            st.plotly_chart(fig_fert, use_container_width=True)

    with c2:
        st.subheader("🚜 Application Technique Breakdown")
        if "application_method" in fert_df.columns:
            method_counts = fert_df["application_method"].value_counts().reset_index()
            method_counts.columns = ["Method", "Count"]
            fig_method = px.pie(
                method_counts,
                names="Method",
                values="Count",
                hole=0.45,
                color="Method",
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_method.update_traces(textposition="outside", textinfo="percent+label")
            fig_method = apply_agrisense_theme(fig_method, title="", height=320, show_legend=False)
            st.plotly_chart(fig_method, use_container_width=True)

    # ── Visual Analytics Row 2: Fertilizer by Crop & Timeline ────────────────
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("🌾 Fertilizer Input by Crop Variety (Tonnes)")
        if not cycles_df.empty:
            merged_f = fert_df.merge(cycles_df[["cycle_id", "crop_name"]].drop_duplicates("cycle_id"), on="cycle_id", how="inner")
            crop_fert = merged_f.groupby("crop_name")["quantity_kg"].sum().reset_index()
            crop_fert["tonnes"] = (crop_fert["quantity_kg"] / 1000.0).round(1)
            crop_fert = crop_fert.sort_values("tonnes", ascending=True)

            fig_cf = px.bar(
                crop_fert,
                x="tonnes",
                y="crop_name",
                orientation="h",
                color="tonnes",
                color_continuous_scale=["#E8EFE5", "#D69B36", "#173F35"],
                text_auto=".1f",
                labels={"tonnes": "Fertilizer Applied (Tonnes)", "crop_name": "Crop Variety"},
            )
            fig_cf.update_coloraxes(showscale=False)
            fig_cf = apply_agrisense_theme(fig_cf, title="", x_title="Total Input (Tonnes)", height=320, show_legend=False)
            st.plotly_chart(fig_cf, use_container_width=True)

    with c4:
        st.subheader("📅 Application Intensity Timeline")
        fert_df["app_date"] = pd.to_datetime(fert_df["date"], errors="coerce")
        clean_fert = fert_df.dropna(subset=["app_date"]).sort_values("app_date")
        if not clean_fert.empty:
            monthly_fert = clean_fert.set_index("app_date").resample("ME").agg(
                total_kg=("quantity_kg", "sum"),
                applications=("fertilizer_id", "count"),
            ).reset_index()

            fig_f_time = px.line(
                monthly_fert,
                x="app_date",
                y="total_kg",
                labels={"total_kg": "Monthly Quantity (kg)", "app_date": "Month"},
                color_discrete_sequence=["#D69B36"],
                markers=True,
            )
            fig_f_time = apply_agrisense_theme(fig_f_time, title="", y_title="Monthly Applied (kg)", height=320, show_legend=False)
            st.plotly_chart(fig_f_time, use_container_width=True)

    # ── Dosage Log Table & Export ─────────────────────────────────────────────
    st.subheader("📋 Agrochemical Application Event Log")
    if not farms_df.empty and "farm_id" in farms_df.columns:
        enriched_fert = fert_df.merge(farms_df[["farm_id", "farm_name"]].drop_duplicates("farm_id"), on="farm_id", how="left")
    else:
        enriched_fert = fert_df.copy()

    fl1, fl2 = st.columns(2)
    with fl1:
        f_types = ["All Types"] + sorted(enriched_fert["fertilizer_type"].dropna().unique().tolist())
        sel_type = st.selectbox("Filter by Fertilizer Type", f_types)
    with fl2:
        f_methods = ["All Methods"] + sorted(enriched_fert["application_method"].dropna().unique().tolist()) if "application_method" in enriched_fert.columns else ["All Methods"]
        sel_m = st.selectbox("Filter by Application Technique", f_methods)

    filtered_fert = enriched_fert.copy()
    if sel_type != "All Types":
        filtered_fert = filtered_fert[filtered_fert["fertilizer_type"] == sel_type]
    if sel_m != "All Methods" and "application_method" in filtered_fert.columns:
        filtered_fert = filtered_fert[filtered_fert["application_method"] == sel_m]

    disp_cols = ["fertilizer_id", "farm_name", "cycle_id", "date", "fertilizer_type", "quantity_kg", "application_method"]
    avail_cols = [c for c in disp_cols if c in filtered_fert.columns]
    rename_fert = {
        "fertilizer_id": "Log ID",
        "farm_name": "Farm",
        "cycle_id": "Cycle ID",
        "date": "Date",
        "fertilizer_type": "Fertilizer Type",
        "quantity_kg": "Quantity (kg)",
        "application_method": "Method",
    }
    disp_df = filtered_fert[avail_cols].rename(columns=rename_fert)
    st.dataframe(disp_df.head(150), use_container_width=True, hide_index=True)

    render_csv_export(disp_df, "agrisense_fertilizer_applications.csv", "📥 Export Fertilizer Records (CSV)")
