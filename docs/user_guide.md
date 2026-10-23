# AgriSense User Guide & Operational Manual

## 1. Quick Start Guide

### Step 1: Environment Setup
Ensure Python 3.11+ is installed. Clone or navigate to the project directory:
```bash
cd c:\Users\ASUS\agri-sense
```

Activate the virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Verify or update database credentials in `.env`:
```ini
APP_ENV=development
APP_DEBUG=true

# Relational Database (MySQL 8.0+)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=agrisense_db

# NoSQL Database (MongoDB 6.0+)
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=agrisense_nosql

# Automatic verified fallback to local CSV/JSON if MySQL credentials are empty
ALLOW_LOCAL_FALLBACK=true
```

> **Note on Zero Configuration:** If your local MySQL requires credentials not yet configured in `.env`, AgriSense seamlessly starts in **Verified Local Fallback mode**, serving all analytics directly from verified data archives in `data/raw/`. MongoDB operates simultaneously if running on port 27017.

### Step 3: Run the Application
Execute the standard entry point:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 2. Page Navigation & Features

### 📊 Dashboard
- **Executive KPI Strip:** Monitor total farms, cultivated acreage, crop production, mean yield, water consumed, and fertilizer inputs.
- **Interactive Global Filters:** Select specific Years (2023–2026), Seasons (Kharif, Rabi, Zaid, Perennial), Crops, or Districts. Click `↺ Reset` at any time.
- **Main Visualizations:** Compare yield per hectare across crops and explore the distribution of water consumption across irrigation methods.
- **Dynamic Insights:** Review automatically calculated findings such as highest yielding varieties, drip irrigation water savings, and soil nutrient deficits.
- **SDG Alignment:** Understand how monitored metrics directly tie to SDG 2 (Zero Hunger) and SDG 12 (Responsible Consumption).
- **Export Data:** Download filtered summary data as CSV with a single click.

### 🏡 Farms
- Search farm holdings by farmer name, farm name, or village.
- Filter by district, soil classification, or irrigation infrastructure.
- Export complete farm holding directory to CSV.

### 🌾 Crop Analytics
- Explore multi-crop acreage shares and production volumes.
- Analyze crop growth cycle duration from sowing to harvest.
- Review the comprehensive Crop Performance Matrix benchmarking actual yields against standards.

### 🧪 Soil Monitoring
- Inspect soil pH distribution across acidic, neutral, and alkaline bands.
- Review percentage of parcels deficient in Nitrogen, Phosphorus, and Potassium.
- Analyze the correlation matrix and download laboratory test records.

### ⛅ Weather
- Compare mean temperatures and cumulative precipitation across agricultural districts.
- Track weekly weather telemetry trends (temperature vs humidity).
- Filter and download meteorological station logs.

### 💧 Water & Irrigation
- Compare water intensity (m³/ha) between Drip, Sprinkler, Tube Well, and Canal Flood.
- Analyze seasonal irrigation frequency timelines.
- Filter and export irrigation operational event logs.

### 🌿 Fertilizer
- Track agrochemical usage by compound (Urea, DAP, MOP, NPK).
- Review application techniques (Broadcasting, Fertigation, Basal, Foliar).
- Filter and export fertilizer dosage logs.

### 📈 Yield Analysis
- Benchmark actual crop yields against agronomic research standards.
- Evaluate harvest output quality grade distribution (Grade A–D).
- Review district and farm productivity rankings.

### ⚡ Resource Efficiency
- Assess crop water productivity (kg yield per m³ water consumed).
- Assess fertilizer productivity (kg harvest per kg input applied).
- Inspect the cycle-level Resource Efficiency Master Table combining inputs and outputs.
- Review methodological limitations of resource ratios.

### 🚨 Alerts
- Review anomalies flagged by deterministic rules (e.g., severe moisture deficits, soil acidity, high irrigation volumes).
- Click `🚀 Evaluate Rules & Refresh Field Alerts` to run on-demand agronomic rule checks with automatic deduplication.
- Filter and export alert logs to CSV.

### 🛡️ Data Quality
- Review the automated data hygiene audit across 10 system datasets.
- Test database connection latency and verify table/collection schemas.
- Trigger an interactive data sanitization test demonstrating duplicate elimination and outlier clamping.
