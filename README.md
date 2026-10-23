# AgriSense

### A Python-Based Data-Driven Crop Monitoring and Agricultural Analytics Platform

> **Academic & Scientific Declaration:**  
> AgriSense is an agricultural data analytics platform and does not rely on artificial intelligence or machine learning. All agronomic insights, resource efficiencies, and alerts originate strictly from deterministic Python data processing, relational (SQL) queries, document (NoSQL) aggregations, statistical calculations, and domain-grounded rule-based thresholds.

---

## 1. Project Overview & Problem Statement

Modern Indian agriculture faces severe challenges regarding water scarcity, soil degradation, imbalanced chemical fertilizer consumption, and unpredictable seasonal yield fluctuations. In critical agricultural hubs such as Maharashtra, smallholder and commercial farmers require precise, transparent, and actionable analytics to understand operational performance across their land parcels.

Existing tools often resort to opaque "black-box" predictions or complex AI models that lack interpretability and require heavy computational infrastructure. **AgriSense** addresses this challenge by providing a **production-quality, data-driven agricultural analytics platform** built on transparent statistical principles, rigorous data cleaning protocols, a hybrid database architecture, and a bespoke "Modern Botanical Intelligence" design language.

---

## 2. Project Objectives

1. **Structured Operational Monitoring:** Track farms, farmers, crops, cycles, soil chemical properties, irrigation events, and fertilizer applications in a normalized relational schema.
2. **Resource Consumption Tracking (SDG 12):** Quantify irrigation water usage (liters, m³, liters per kg of yield) and fertilizer intensity (kg/ha) across irrigation methods (Drip, Sprinkler, Canal Flood, Tube Well).
3. **Productivity Benchmarking (SDG 2):** Benchmark actual harvest yields against agricultural reference standards to compute the "yield gap" and evaluate output quality grades.
4. **Semi-Structured Telemetry Storage:** Capture polymorphic sensor readings, weather station observations, qualitative agronomist field notes, and audit logs in a flexible NoSQL document database.
5. **Deterministic Rule-Based Alerts:** Evaluate field observations against established agronomic thresholds to flag soil acidity/alkalinity, water deficits, and over-irrigation without probabilistic guessing.
6. **Data Quality & Auditability:** Ensure transparent data sanitization with fully documented cleaning rules for missing values, duplicates, out-of-bounds metrics, and orphan records.

---

## 3. UN Sustainable Development Goals (SDG) Alignment

| Goal | Title | AgriSense Implementation |
| :--- | :--- | :--- |
| **SDG 2** | **Zero Hunger** | Evaluates crop productivity, tracks harvest yield gaps against ICAR benchmarks, monitors seasonal crop cycles, and highlights soil fertility indices to enhance sustainable food production. |
| **SDG 12** | **Responsible Consumption & Production** | Measures water application intensity across irrigation methods (demonstrating Drip irrigation savings vs Canal Flood) and tracks fertilizer dosage rates to minimize chemical runoff and resource wastage. |

---

## 4. Key Platform Features & Navigation Pages

AgriSense is organized into **11 comprehensive operational pages**:

### OVERVIEW
- **📊 Dashboard:** Executive KPI strip, global multidimensional filters (Year, Season, Crop, District), main visualizations (Crop Productivity & Water Stewardship), dynamic data-driven insights panel, active field alert tracker, and SDG 2 & 12 alignment matrix.

### MONITORING
- **🏡 Farms:** Interactive landholdings directory, farmer profiles, district/soil/irrigation filters, farm-level acreage distributions, and search capabilities.
- **🌾 Crop Analytics:** Botanical catalog, cultivation duration analysis, multi-crop acreage shares, production volume comparisons, and agronomic performance matrix.
- **🧪 Soil Monitoring:** Chemical laboratory analysis, pH distribution bands, NPK deficiency proportions, moisture vs available nitrogen correlation, and soil parameter correlation matrix.
- **⛅ Weather:** District-level meteorological telemetry, temperature trends, cumulative rainfall, relative humidity, and environmental time-series trends.

### RESOURCES
- **💧 Water & Irrigation:** Volumetric consumption (liters and m³), irrigation method efficiency comparisons (Drip vs Sprinkler vs Flood), duration analysis, and monthly frequency timelines.
- **🌿 Fertilizer:** Chemical compound breakdown (Urea, DAP, MOP, 10:26:26, Compost), application techniques (Broadcasting, Fertigation, Basal, Foliar), and monthly dosage timelines.

### PERFORMANCE
- **📈 Yield Analysis:** Harvest output benchmarking against standard research station benchmarks, yield gap evaluation (kg/ha), seasonal comparisons, and quality grading (Grade A–D).
- **⚡ Resource Efficiency:** Crop water productivity (kg/m³), fertilizer productivity (kg/kg), land productivity (kg/ha), resource intensity correlation, and cycle-level efficiency master table.

### SYSTEM
- **🚨 Alerts:** Deterministic agronomic rule evaluation engine, severity breakdown (CRITICAL, WARNING, INFO), on-demand rule execution with automated deduplication into MongoDB.
- **🛡️ Data Quality:** Automated 10-dataset hygiene audit, missing value and duplicate detection, boundary check verification, database connection diagnostics, and interactive sanitization test.

---

## 5. Technology Stack

- **Frontend / Presentation:** Streamlit, Custom CSS (Design System: Modern Botanical Intelligence), Plotly Interactive Visualizations.
- **Backend & Application Logic:** Python 3.11+, Pandas, NumPy, SQLAlchemy 2.0+, Pydantic 2.0+.
- **Relational Database:** MySQL 8.0+ (PyMySQL driver with connection pooling).
- **NoSQL Database:** MongoDB 6.0+ (PyMongo driver with timeout protection).
- **Configuration & Security:** `python-dotenv` with strictly masked credential handling.
- **Testing & Quality Assurance:** Python `unittest` framework, comprehensive 16-test assertion suite.

---

## 6. System Architecture & Database Responsibilities

```text
User / Agronomist / Evaluator
             │
             ▼
     Streamlit Web UI (Botanical Theme + Plotly Charts)
             │
             ▼
   Application / Service Layer (FarmService, CropService, SoilService, ResourceService, AlertService, etc.)
             │
             ▼
   Analytics Layer (Formulas, Ratios, Pearson Correlations, Yield Gap Benchmarks)
             │
             ▼
   Data Cleaning & Quality Module (DataCleaner, Validation Rules, Audit Logging)
             │
    ┌────────┴──────────────────────────┐
    ▼                                   ▼
Relational Repository (MySQL 8.0+)   NoSQL Repository (MongoDB 6.0+)
• farmers, farms, crops, seasons     • weather_observations
• crop_cycles, yield_records         • field_observations
• soil_records, irrigation_records   • agricultural_alerts
• fertilizer_records                 • sensor_observations, activity_logs
    │                                   │
    ▼ (Graceful Fallback)               ▼ (Graceful Fallback)
data/raw/*.csv                      data/raw/*.json
```

For detailed architecture specifications, see [docs/architecture.md](file:///c:/Users/ASUS/agri-sense/docs/architecture.md).

---

## 7. Mathematical Formulas & KPIs

| Analytical Metric | Formula | Units |
|---|---|---|
| **Land Productivity** | $\text{Yield (kg)} / \text{Cultivated Area (ha)}$ | $\text{kg/ha}$ |
| **Water Intensity** | $\text{Water Used (Liters)} / \text{Cultivated Area (ha)}$ | $\text{L/ha}$ or $\text{m}^3\text{/ha}$ |
| **Fertilizer Intensity** | $\text{Fertilizer Applied (kg)} / \text{Cultivated Area (ha)}$ | $\text{kg/ha}$ |
| **Water Productivity** | $\text{Harvest Yield (kg)} / \text{Water Used (m}^3\text{)}$ | $\text{kg/m}^3$ |
| **Fertilizer Productivity** | $\text{Harvest Yield (kg)} / \text{Fertilizer Applied (kg)}$ | $\text{kg/kg}$ |
| **Yield Gap** | $\text{Standard Benchmark Yield} - \text{Actual Harvest Yield}$ | $\text{kg/ha}$ |

For full formula constraints and limitations, see [docs/analytics.md](file:///c:/Users/ASUS/agri-sense/docs/analytics.md).

---

## 8. Installation & Setup

### Prerequisites
- Python 3.11+
- Git

### Step 1: Clone and Navigate
```bash
git clone https://github.com/your-username/agri-sense.git
cd agri-sense
```

### Step 2: Set up Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Variables Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update database credentials if running live MySQL and MongoDB:
```env
APP_ENV=development
APP_DEBUG=true

# Relational Database (MySQL 8.0+)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=agrisense_db

# NoSQL Database (MongoDB 6.0+)
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=agrisense_nosql

# Hybrid Fallback Engine
ALLOW_LOCAL_FALLBACK=true
```

> **Zero Configuration Readiness:** If MySQL is not locally configured with a password, AgriSense automatically runs in **Verified Local Fallback Mode**, querying pre-sanitized CSV archives in `data/raw/`. MongoDB operates live if running on port 27017.

---

## 9. Database Seeding Instructions

### Option A: Automated Synthetic Seeding
```bash
python database/seed_data.py
```

### Option B: Seeding Through the User Interface
1. Launch the platform: `streamlit run app.py`.
2. Open the **🛡️ Data Quality** page in the sidebar.
3. Click **"Seed MySQL from Data Archive"** or **"Seed MongoDB Collections"**.

---

## 10. Startup Command

Launch the AgriSense analytics platform:
```bash
streamlit run app.py
```
Access the dashboard at `http://localhost:8501`.

---

## 11. Automated Testing Instructions

AgriSense includes comprehensive test suites verifying data cleaning rules, validators, repositories, services, and formula correctness:

```bash
# Run the Master Integration & Unit Test Suite:
python tests/test_master_suite.py

# Run the Foundation Test Suite:
python tests/test_foundation.py
```
Expected output: **All tests pass (100% PASS rate, 0 errors).**

For the detailed testing report, see [docs/testing_report.md](file:///c:/Users/ASUS/agri-sense/docs/testing_report.md).

---

## 12. Documentation Index

- [System Architecture & Database Topology](file:///c:/Users/ASUS/agri-sense/docs/architecture.md)
- [Agronomic Analytics & Rule Engine Specification](file:///c:/Users/ASUS/agri-sense/docs/analytics.md)
- [Dashboard Design System & UI/UX Guide](file:///c:/Users/ASUS/agri-sense/docs/dashboard.md)
- [User Guide & Operational Manual](file:///c:/Users/ASUS/agri-sense/docs/user_guide.md)
- [Automated Testing & Verification Report](file:///c:/Users/ASUS/agri-sense/docs/testing_report.md)

---

## 13. Limitations & Future Scope

### Current Limitations
1. **Synthetic / Demo Data:** All demo records are synthetically modeled on Maharashtra's agricultural distributions and agronomic benchmarks for academic evaluation.
2. **Precipitation Partitioning:** Water productivity ratios measure metered irrigation water only; effective precipitation contribution is not deducted in rainfed plots.
3. **Correlation vs Causation:** Observed correlations between fertilizer or irrigation inputs and harvest yields do not imply causation without controlled agricultural randomized parcel trials.

### Future Scope
1. **Spatial GIS Field Boundary Mapping:** Integration of GeoPandas and Kepler.gl for interactive polygon boundary visualization.
2. **Automated Agronomic Advisory Reports:** Generating farmer-level PDF scorecards for seasonal soil amendments.
3. **Multi-State Agricultural Benchmarks:** Expanding standard crop yield datasets across Punjab, Uttar Pradesh, Karnataka, and Madhya Pradesh.

---

## License

This project is developed as an academic capstone platform for the BTech Artificial Intelligence and Machine Learning curriculum. Distributed under the MIT License.
