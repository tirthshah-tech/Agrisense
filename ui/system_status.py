"""
AgriSense - Database & System Status Page
Live diagnostic panel for MySQL, MongoDB, connection testing, data seeding, and cleaning audit logs.
"""
import streamlit as st
import pandas as pd

from config.settings import settings
from database.mysql_connection import check_mysql_connection, init_mysql_tables
from database.mongo_connection import check_mongo_connection, init_mongo_indexes
from database.seed_data import seed_mysql_from_files, seed_mongo_from_files
from utils.data_cleaning import DataCleaner
from ui.components import render_page_header


def render_system_status_page() -> None:
    """Renders the system health, database configuration, and data cleaning audit view."""
    render_page_header(
        title="Database & System Diagnostics",
        subtitle="Live connection diagnostics, schema initialization, database seeding, and data quality audit logs.",
        sdg_label="System Integrity & Data Architecture",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🐬 MySQL Relational Database")
        mysql_ok, mysql_msg = check_mysql_connection()
        if mysql_ok:
            st.success(f"Status: ONLINE\n\n{mysql_msg}")
        else:
            st.warning(f"Status: OFFLINE / NOT CONFIGURED\n\n{mysql_msg}")

        st.markdown(
            f"""
            - **Host**: `{settings.mysql.host}`
            - **Port**: `{settings.mysql.port}`
            - **Database**: `{settings.mysql.database}`
            - **User**: `{settings.mysql.user}`
            - **Password**: `{'*' * len(settings.mysql.password) if settings.mysql.password else 'Not set'}`
            """
        )

        if st.button("🧪 Test MySQL Connection", key="test_mysql"):
            ok, msg = check_mysql_connection()
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        if mysql_ok:
            if st.button("🌱 Seed MySQL from Data Archive", key="seed_mysql"):
                with st.spinner("Seeding MySQL tables..."):
                    ok, msg = seed_mysql_from_files(settings.paths.raw_data_dir)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

    with col2:
        st.subheader("🍃 MongoDB NoSQL Database")
        mongo_ok, mongo_msg = check_mongo_connection()
        if mongo_ok:
            st.success(f"Status: ONLINE\n\n{mongo_msg}")
        else:
            st.warning(f"Status: OFFLINE / NOT CONFIGURED\n\n{mongo_msg}")

        st.markdown(
            f"""
            - **URI**: `{settings.mongo.uri}`
            - **Database**: `{settings.mongo.database}`
            - **Collections**: `weather_observations`, `field_observations`, `agricultural_alerts`, `sensor_observations`, `activity_logs`
            """
        )

        if st.button("🧪 Test MongoDB Connection", key="test_mongo"):
            ok, msg = check_mongo_connection()
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        if mongo_ok:
            if st.button("🌱 Seed MongoDB from Data Archive", key="seed_mongo"):
                with st.spinner("Seeding MongoDB collections..."):
                    ok, msg = seed_mongo_from_files(settings.paths.raw_data_dir)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🧹 Data Quality & Sanitization Module (Verification Test)")
    st.write(
        "AgriSense enforces strict data sanitization rules. "
        "Run an on-demand audit to verify how the data cleaner handles missing values, impossible pH, negative quantities, and duplicates."
    )

    if st.button("🔍 Run Live Data Quality Audit Test", key="run_audit"):
        cleaner = DataCleaner()
        
        # Test 1: Soil records with intentionally injected edge-cases
        test_soil = pd.DataFrame([
            {"soil_record_id": 1, "farm_id": 1, "record_date": "2024-01-01", "ph": 7.2, "nitrogen": 250.0, "phosphorus": 18.0, "potassium": 210.0, "moisture": 35.0},
            {"soil_record_id": 2, "farm_id": 1, "record_date": "2024-01-01", "ph": 7.2, "nitrogen": 250.0, "phosphorus": 18.0, "potassium": 210.0, "moisture": 35.0}, # Duplicate
            {"soil_record_id": 3, "farm_id": 2, "record_date": "2024-01-02", "ph": 15.8, "nitrogen": 220.0, "phosphorus": 12.0, "potassium": 190.0, "moisture": 40.0}, # Impossible pH > 14
            {"soil_record_id": 4, "farm_id": 3, "record_date": "2024-01-03", "ph": 6.8, "nitrogen": -45.0, "phosphorus": 15.0, "potassium": 200.0, "moisture": 45.0}, # Negative Nitrogen
            {"soil_record_id": 5, "farm_id": 4, "record_date": "2024-01-04", "ph": 7.0, "nitrogen": 280.0, "phosphorus": 20.0, "potassium": 220.0, "moisture": 140.0}, # Moisture > 100%
        ])
        
        cleaned_soil = cleaner.clean_soil_records(test_soil)
        
        # Test 2: Irrigation with negative water
        test_irrig = pd.DataFrame([
            {"irrigation_id": 1, "farm_id": 1, "date": "2024-01-01", "water_used_liters": -5000.0, "irrigation_method": "Drip", "duration_hours": 3.0},
            {"irrigation_id": 2, "farm_id": 2, "date": "2024-01-02", "water_used_liters": 15000.0, "irrigation_method": "Flood", "duration_hours": 30.0},
        ])
        cleaned_irrig = cleaner.clean_irrigation_records(test_irrig)
        
        audit_trail = cleaner.get_audit_trail()
        st.success(f"Audit Complete! {len(audit_trail)} cleaning actions documented.")
        st.dataframe(audit_trail, use_container_width=True, hide_index=True)
