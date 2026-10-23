"""
AgriSense - Water & Irrigation Analytics View (SDG 12)
Monitors agricultural water consumption, compares irrigation methods,
evaluates water intensity per hectare, and promotes responsible water stewardship.
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


def render_resources_page() -> None:
    """Renders the comprehensive Water & Irrigation analytics view."""
    render_page_header(
        title="Water & Irrigation Resource Analytics",
        subtitle="Tracking agricultural water consumption, evaluating irrigation method efficiencies, and optimizing water intensity under SDG 12.",
        sdg_label="SDG 12: Responsible Water Stewardship & Resource Conservation",
    )
    render_database_status_strip()

    res_svc = ResourceService()
    res_repo = ResourceRepository()
    crop_repo = CropRepository()
    farm_repo = FarmRepository()

    metrics = res_svc.get_water_metrics()
    irrig_df = res_repo.get_all_irrigation_records()
    cycles_df = crop_repo.get_cycles_enriched()
    farms_df = farm_repo.get_all_farms()

    if irrig_df.empty:
        render_empty_state("No irrigation event records available.")
        return

    # Handle duration column
    if "duration_minutes" in irrig_df.columns and "duration_hours" not in irrig_df.columns:
        irrig_df["duration_hours"] = irrig_df["duration_minutes"] / 60.0

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    total_water_m3 = metrics["total_water_m3"]
    total_events = metrics["total_irrigation_events"]
    avg_event_l = metrics["avg_liters_per_event"]

    w1, w2, w3, w4 = st.columns(4)
    render_kpi(w1, "Total Water Consumed", f"{total_water_m3:,.0f} m³", f"{metrics['total_water_liters']:,.0f} Liters", icon="💧", is_dark=True)
    render_kpi(w2, "Irrigation Events", f"{total_events:,}", "Field application logs", icon="🚿")
    render_kpi(w3, "Mean / Application", f"{avg_event_l:,.0f} L", "Per event", icon="⏱️")
    render_kpi(w4, "Method Efficiency", "Drip 85% Savings", "vs Traditional Canal Flood", icon="🌱")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visual Analytics Row 1: Volume by Method & Duration ───────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🚿 Total Water Consumption by Irrigation Method")
        method_df = res_svc.get_water_by_method()
        if not method_df.empty:
            fig_bar = px.bar(
                method_df,
                x="irrigation_method",
                y="total_m3",
                color="irrigation_method",
                text="total_m3",
                labels={"irrigation_method": "Irrigation Method", "total_m3": "Volume (m³)"},
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_bar.update_traces(texttemplate="%{text:,.0f} m³", textposition="outside")
            fig_bar = apply_agrisense_theme(fig_bar, title="", y_title="Total Water Volume (m³)", height=320, show_legend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("⏱️ Average Irrigation Duration (Hours per Event)")
        if "duration_hours" in irrig_df.columns:
            dur_df = irrig_df.groupby("irrigation_method")["duration_hours"].mean().reset_index().round(1)
            fig_dur = px.bar(
                dur_df,
                x="irrigation_method",
                y="duration_hours",
                color="irrigation_method",
                text="duration_hours",
                labels={"irrigation_method": "Method", "duration_hours": "Duration (Hours)"},
                color_discrete_sequence=AGRI_COLOR_SEQUENCE,
            )
            fig_dur.update_traces(texttemplate="%{text:.1f} hrs", textposition="outside")
            fig_dur = apply_agrisense_theme(fig_dur, title="", y_title="Mean Duration (Hours)", height=320, show_legend=False)
            st.plotly_chart(fig_dur, use_container_width=True)

    # ── Visual Analytics Row 2: Water by Crop & Monthly Distribution ─────────
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("🌾 Water Consumption by Crop Variety (m³)")
        if not cycles_df.empty:
            merged_w = irrig_df.merge(cycles_df[["cycle_id", "crop_name"]].drop_duplicates("cycle_id"), on="cycle_id", how="inner")
            crop_water = merged_w.groupby("crop_name")["water_used_liters"].sum().reset_index()
            crop_water["total_m3"] = (crop_water["water_used_liters"] / 1000.0).round(1)
            crop_water = crop_water.sort_values("total_m3", ascending=True)

            fig_cw = px.bar(
                crop_water,
                x="total_m3",
                y="crop_name",
                orientation="h",
                color="total_m3",
                color_continuous_scale=["#E8EFE5", "#2A9D8F", "#173F35"],
                text_auto=".0f",
                labels={"total_m3": "Water Applied (m³)", "crop_name": "Crop Variety"},
            )
            fig_cw.update_coloraxes(showscale=False)
            fig_cw = apply_agrisense_theme(fig_cw, title="", x_title="Total Volume (m³)", height=320, show_legend=False)
            st.plotly_chart(fig_cw, use_container_width=True)

    with c4:
        st.subheader("📅 Irrigation Frequency Timeline")
        irrig_df["irrig_date"] = pd.to_datetime(irrig_df["date"], errors="coerce")
        clean_irrig = irrig_df.dropna(subset=["irrig_date"]).sort_values("irrig_date")
        if not clean_irrig.empty:
            timeline_df = clean_irrig.set_index("irrig_date").resample("ME").agg(
                total_water_m3=("water_used_liters", lambda s: s.sum() / 1000.0),
                events=("irrigation_id", "count"),
            ).reset_index()

            fig_time = px.line(
                timeline_df,
                x="irrig_date",
                y="total_water_m3",
                labels={"total_water_m3": "Monthly Water (m³)", "irrig_date": "Month"},
                color_discrete_sequence=["#26734D"],
                markers=True,
            )
            fig_time = apply_agrisense_theme(fig_time, title="", y_title="Water Applied (m³)", height=320, show_legend=False)
            st.plotly_chart(fig_time, use_container_width=True)

    # ── Operational Irrigation Log & Export ──────────────────────────────────
    st.subheader("📋 Irrigation Operational Event Log")
    if not farms_df.empty and "farm_id" in farms_df.columns:
        enriched_irrig = irrig_df.merge(farms_df[["farm_id", "farm_name"]].drop_duplicates("farm_id"), on="farm_id", how="left")
    else:
        enriched_irrig = irrig_df.copy()

    f1, f2 = st.columns(2)
    with f1:
        method_options = ["All Methods"] + sorted(enriched_irrig["irrigation_method"].dropna().unique().tolist())
        sel_m = st.selectbox("Filter by Method", method_options)
    with f2:
        farm_options = ["All Farms"] + sorted(enriched_irrig["farm_name"].dropna().unique().tolist()) if "farm_name" in enriched_irrig.columns else ["All Farms"]
        sel_f = st.selectbox("Filter by Farm", farm_options)

    filtered_irrig = enriched_irrig.copy()
    if sel_m != "All Methods":
        filtered_irrig = filtered_irrig[filtered_irrig["irrigation_method"] == sel_m]
    if sel_f != "All Farms" and "farm_name" in filtered_irrig.columns:
        filtered_irrig = filtered_irrig[filtered_irrig["farm_name"] == sel_f]

    disp_cols = ["irrigation_id", "farm_name", "cycle_id", "date", "water_used_liters", "irrigation_method", "duration_hours"]
    avail_cols = [c for c in disp_cols if c in filtered_irrig.columns]
    rename_irrig = {
        "irrigation_id": "Log ID",
        "farm_name": "Farm",
        "cycle_id": "Cycle ID",
        "date": "Date",
        "water_used_liters": "Water Used (Liters)",
        "irrigation_method": "Method",
        "duration_hours": "Duration (Hrs)",
    }
    disp_df = filtered_irrig[avail_cols].rename(columns=rename_irrig)
    st.dataframe(disp_df.head(150), use_container_width=True, hide_index=True)

    render_csv_export(disp_df, "agrisense_irrigation_records.csv", "📥 Export Irrigation Logs (CSV)")
