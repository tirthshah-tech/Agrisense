"""
AgriSense - Rule-Based Agricultural Alerts & Anomaly Monitor
Automated agronomic rule checks against deterministic thresholds for soil acidity,
moisture deficits, excessive water consumption, and agrochemical over-application.
Strictly non-AI / non-ML: fully explainable and deterministic.
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
from services.alert_service import AlertService
from repositories.observation_repository import ObservationRepository


def render_alerts_page() -> None:
    """Renders the Rule-Based Agricultural Alerts view."""
    render_page_header(
        title="Rule-Based Agricultural Alerts",
        subtitle="Automated agronomic rule checks against critical thresholds for soil, water, weather, and agrochemicals.",
        sdg_label="Rule-Based Decision Support (Deterministic Thresholds, Non-AI)",
    )
    render_database_status_strip()

    alert_svc = AlertService()
    obs_repo = ObservationRepository()

    summary = alert_svc.get_alert_summary()
    alerts_df = obs_repo.get_agricultural_alerts()

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    a1, a2, a3, a4 = st.columns(4)
    render_kpi(a1, "Total Alerts Logged", f"{summary['total_alerts']:,}", "Evaluated by Engine", icon="🚨", is_dark=True)
    render_kpi(a2, "Open Active Alerts", f"{summary['open_alerts']:,}", "Require Field Action", icon="⚠️")
    render_kpi(a3, "Critical Severity", f"{summary['critical_alerts']:,}", "High Risk Anomalies", icon="🔴")
    render_kpi(a4, "Warning Severity", f"{summary['warning_alerts']:,}", "Monitoring Thresholds", icon="🟠")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Alert Engine Execution Button ─────────────────────────────
    st.markdown(
        """
        <div class="content-card" style="padding: 1.1rem 1.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <strong style="color: #173F35; font-size: 0.95rem;">⚙️ Run Agronomic Rule Engine Evaluation</strong>
                    <div style="font-size: 0.8rem; color: #738078;">
                        Executes deterministic rule verification across soil, water, fertilizer, and harvest records with automatic deduplication into MongoDB.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚀 Evaluate Rules & Refresh Field Alerts", key="run_alert_eval"):
        with st.spinner("Evaluating deterministic rules across all agricultural records..."):
            new_count = alert_svc.evaluate_rules_and_generate_alerts()
            st.success(f"Rule Evaluation Complete! {new_count} newly identified anomalous conditions logged. Deduplication verified.")
            st.rerun()

    if alerts_df.empty:
        render_empty_state("No agricultural alerts currently recorded.")
        return

    # ── Visual Analytics Row: Distribution by Type and Severity ──────────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Alerts by Agronomic Rule Type")
        type_df = alert_svc.get_alerts_by_type()
        if not type_df.empty:
            fig_type = px.bar(
                type_df.head(7).sort_values("alert_count", ascending=True),
                x="alert_count",
                y="alert_type",
                orientation="h",
                color="alert_count",
                color_continuous_scale=["#E8EFE5", "#D69B36", "#C65C50"],
                text_auto=".0f",
                labels={"alert_count": "Alert Count", "alert_type": "Rule Type"},
            )
            fig_type.update_coloraxes(showscale=False)
            fig_type = apply_agrisense_theme(fig_type, title="", x_title="Number of Alerts", height=280, show_legend=False)
            st.plotly_chart(fig_type, use_container_width=True)

    with c2:
        st.subheader("🚨 Severity Breakdown")
        if "severity" in alerts_df.columns:
            sev_counts = alerts_df["severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            sev_colors = {
                "Critical": "#C65C50",
                "High": "#D69B36",
                "Warning": "#78A85A",
                "Info": "#2A9D8F",
            }
            fig_sev = px.pie(
                sev_counts,
                names="Severity",
                values="Count",
                color="Severity",
                color_discrete_map=sev_colors,
                hole=0.45,
            )
            fig_sev.update_traces(textposition="outside", textinfo="percent+label")
            fig_sev = apply_agrisense_theme(fig_sev, title="", height=280, show_legend=False)
            st.plotly_chart(fig_sev, use_container_width=True)

    # ── Filtering & Alert Log Table ──────────────────────────────────────────
    st.subheader("📋 Agricultural Alert Log Registry")
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        sev_options = ["All Severities"] + sorted(alerts_df["severity"].dropna().unique().tolist()) if "severity" in alerts_df.columns else ["All Severities"]
        sel_sev = st.selectbox("Filter by Severity", sev_options)
    with f_col2:
        stat_options = ["All Statuses"] + sorted(alerts_df["status"].dropna().unique().tolist()) if "status" in alerts_df.columns else ["All Statuses"]
        sel_stat = st.selectbox("Filter by Status", stat_options)
    with f_col3:
        type_options = ["All Rule Types"] + sorted(alerts_df["alert_type"].dropna().unique().tolist()) if "alert_type" in alerts_df.columns else ["All Rule Types"]
        sel_t = st.selectbox("Filter by Rule Type", type_options)

    filtered = alerts_df.copy()
    if sel_sev != "All Severities":
        filtered = filtered[filtered["severity"] == sel_sev]
    if sel_stat != "All Statuses":
        filtered = filtered[filtered["status"] == sel_stat]
    if sel_t != "All Rule Types":
        filtered = filtered[filtered["alert_type"] == sel_t]

    st.caption(f"Displaying {len(filtered)} alerts matching criteria")

    display_cols = ["alert_id", "farm_id", "alert_type", "severity", "trigger_rule", "metric_value", "threshold_value", "status", "timestamp"]
    avail_cols = [c for c in display_cols if c in filtered.columns]
    rename_alerts = {
        "alert_id": "Alert ID",
        "farm_id": "Farm ID",
        "alert_type": "Alert Rule",
        "severity": "Severity",
        "trigger_rule": "Trigger Rule Condition",
        "metric_value": "Observed Metric",
        "threshold_value": "Threshold Bound",
        "status": "Status",
        "timestamp": "Timestamp",
    }
    disp_df = filtered[avail_cols].rename(columns=rename_alerts)
    st.dataframe(disp_df.head(200), use_container_width=True, hide_index=True)

    render_csv_export(disp_df, "agrisense_agricultural_alerts.csv", "📥 Export Alerts Registry (CSV)")
