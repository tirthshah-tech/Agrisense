"""
AgriSense - Weather & Environmental Telemetry View (MongoDB Semi-Structured Archive)
Meteorological telemetry across Maharashtra agricultural districts:
Temperature trends, precipitation tracking, relative humidity, and microclimate comparisons.
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
from services.weather_service import WeatherService
from repositories.observation_repository import ObservationRepository


def render_weather_page() -> None:
    """Renders the Weather & Environmental Telemetry view."""
    render_page_header(
        title="Weather & Environmental Telemetry",
        subtitle="District-level meteorological observations, precipitation tracking, humidity, and microclimate indicators.",
        sdg_label="Climate Action & Agricultural Resilience",
    )
    render_database_status_strip()

    weather_svc = WeatherService()
    obs_repo = ObservationRepository()

    metrics = weather_svc.get_weather_summary()
    raw_weather_df = obs_repo.get_weather_observations(limit=1500)
    weather_df = weather_svc._normalize_weather_df(raw_weather_df)

    if weather_df.empty:
        render_empty_state("No weather observation telemetry available in MongoDB or local archive.")
        return

    # ── Macro KPI Strip ────────────────────────────────────────────────────────
    w1, w2, w3, w4 = st.columns(4)
    render_kpi(w1, "Telemetry Readings", f"{metrics['total_observations']:,}", "Weather Stations", icon="📡", is_dark=True)
    render_kpi(w2, "Mean Temperature", f"{metrics['avg_temperature']} °C", f"Range: {metrics['min_temp']}° – {metrics['max_temp']}°", icon="🌡️")
    render_kpi(w3, "Mean Humidity", f"{metrics['avg_humidity']} %", "Relative Humidity", icon="💧")
    render_kpi(w4, "Cumulative Rainfall", f"{metrics['total_rainfall_mm']:,.0f} mm", "Across Stations", icon="🌧️")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visual Analytics Row 1: District Comparisons ──────────────────────────
    c1, c2 = st.columns(2)
    dist_df = weather_svc.get_district_weather_comparison()

    with c1:
        st.subheader("🌡️ Mean Temperature by Agricultural District")
        if not dist_df.empty and "avg_temp" in dist_df.columns:
            fig_temp = px.bar(
                dist_df.sort_values("avg_temp", ascending=True),
                x="avg_temp",
                y="district",
                orientation="h",
                color="avg_temp",
                color_continuous_scale=["#78A85A", "#D69B36", "#C65C50"],
                text_auto=".1f",
                labels={"avg_temp": "Mean Temperature (°C)", "district": "District"},
            )
            fig_temp.update_coloraxes(showscale=False)
            fig_temp = apply_agrisense_theme(fig_temp, title="", x_title="Temperature (°C)", height=310, show_legend=False)
            st.plotly_chart(fig_temp, use_container_width=True)

    with c2:
        st.subheader("🌧️ Cumulative Rainfall by District")
        if not dist_df.empty and "total_rain" in dist_df.columns:
            fig_rain = px.bar(
                dist_df.sort_values("total_rain", ascending=False),
                x="district",
                y="total_rain",
                color="total_rain",
                color_continuous_scale=["#E8EFE5", "#2A9D8F", "#173F35"],
                text_auto=".0f",
                labels={"total_rain": "Precipitation (mm)", "district": "District"},
            )
            fig_rain.update_coloraxes(showscale=False)
            fig_rain = apply_agrisense_theme(fig_rain, title="", y_title="Rainfall (mm)", height=310, show_legend=False)
            st.plotly_chart(fig_rain, use_container_width=True)

    # ── Monthly / Date Trends ─────────────────────────────────────────────────
    st.subheader("📈 Environmental Telemetry Trends Over Time")
    st.write("Weather columns:", weather_df.columns.tolist())
    st.write("Weather data preview:", weather_df.head())
    
    # Normalize column names first
    weather_df.columns = weather_df.columns.astype(str).str.strip()

# Support common date-field names
    date_candidates = [
    "timestamp",
    "observed_at",
    "observation_date",
    "obs_date",
    "recorded_at",
    "date",
    ]

    date_col = next(
    (col for col in date_candidates if col in weather_df.columns),
    None,
    )

    if date_col is None:
        st.error("Weather observation date column was not found.")
        st.write("Available columns:", weather_df.columns.tolist())
        st.stop()

    weather_df["obs_date"] = pd.to_datetime(
    weather_df[date_col],
    errors="coerce",
    ) 

    weather_df = weather_df.dropna(subset=["obs_date"])

    weather_clean = weather_df.dropna(subset=["obs_date"]).sort_values("obs_date")

    if not weather_clean.empty:
        # Group by weekly date for smooth trendline
        weekly_trend = weather_clean.set_index("obs_date").resample("W").agg(
            mean_temp=("temperature", "mean"),
            mean_humidity=("humidity", "mean"),
            total_rainfall=("rainfall_mm", "sum"),
        ).reset_index()

        fig_trend = px.line(
            weekly_trend,
            x="obs_date",
            y=["mean_temp", "mean_humidity"],
            labels={"value": "Observation Value", "obs_date": "Timeline", "variable": "Metric"},
            color_discrete_map={"mean_temp": "#C65C50", "mean_humidity": "#2A9D8F"},
        )
        fig_trend = apply_agrisense_theme(fig_trend, title="Weekly Meteorological Trends (Temperature °C vs Humidity %)", height=300, show_legend=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    # ── Telemetry Logs Filter & Table ─────────────────────────────────────────
    st.subheader("📋 Weather Telemetry Logs (MongoDB Archive)")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        sel_dist = st.selectbox("Filter by District", ["All Districts"] + sorted(weather_df["district"].dropna().unique().tolist()))
    with d_col2:
        conditions = ["All Conditions"] + sorted(weather_df["weather_condition"].dropna().unique().tolist()) if "weather_condition" in weather_df.columns else ["All Conditions"]
        sel_cond = st.selectbox("Filter by Weather Condition", conditions)

    filtered_w = weather_df.copy()
    if sel_dist != "All Districts":
        filtered_w = filtered_w[filtered_w["district"] == sel_dist]
    if sel_cond != "All Conditions" and "weather_condition" in filtered_w.columns:
        filtered_w = filtered_w[filtered_w["weather_condition"] == sel_cond]

    disp_cols = ["station_id", "district", "timestamp", "temperature", "humidity", "rainfall_mm", "wind_speed_kmh", "weather_condition"]
    avail_cols = [c for c in disp_cols if c in filtered_w.columns]
    rename_w = {
        "station_id": "Station ID",
        "district": "District",
        "timestamp": "Timestamp",
        "temperature": "Temp (°C)",
        "humidity": "Humidity (%)",
        "rainfall_mm": "Rainfall (mm)",
        "wind_speed_kmh": "Wind (km/h)",
        "weather_condition": "Condition",
    }
    disp_df = filtered_w[avail_cols].rename(columns=rename_w)
    st.dataframe(disp_df.head(150), use_container_width=True, hide_index=True)

    render_csv_export(disp_df, "agrisense_weather_telemetry.csv", "📥 Export Weather Telemetry (CSV)")
