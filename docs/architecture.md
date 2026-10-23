# AgriSense System Architecture & Database Topology

## 1. System Overview

**AgriSense** is an academic-grade, data-driven crop monitoring and agricultural analytics platform developed for Maharashtra's agro-climatic zones. The architecture adheres to a strict layered design:

$$\text{UI Layer (Streamlit)} \longrightarrow \text{Service Layer} \longrightarrow \text{Analytics Engine} \longrightarrow \text{Repository Layer} \longrightarrow \text{Database Layer}$$

### Strict Non-AI / Non-ML Paradigm
AgriSense deliberately excludes machine learning, neural networks, LLMs, and generative AI. All analytical insights, yield gaps, and alerts are calculated through **deterministic SQL aggregation**, **Pandas/NumPy statistical operations**, and **agronomic rule thresholds**.

---

## 2. Dual Database Distribution Model

To guarantee ACID guarantees for transactional financial/operational entities alongside elastic flexibility for time-series meteorological logs, AgriSense implements a hybrid database model:

```
                            ┌───────────────────────────────────┐
                            │    Streamlit Application (UI)     │
                            └─────────────────┬─────────────────┘
                                              │
                            ┌─────────────────▼─────────────────┐
                            │     Service & Analytics Layer     │
                            └─────────┬───────────────┬─────────┘
                                      │               │
             ┌────────────────────────┴──────┐ ┌──────┴────────────────────────┐
             │    SQL Relational Repository  │ │   NoSQL Telemetry Repository  │
             └───────────────┬───────────────┘ └──────────────┬────────────────┘
                             │                                │
                             ▼                                ▼
                 ┌───────────────────────┐        ┌───────────────────────┐
                 │     MySQL 8.0+        │        │     MongoDB 6.0+      │
                 │  (Normalized ACID)    │        │ (Semi-Structured IoT) │
                 ├───────────────────────┤        ├───────────────────────┤
                 │ • farmers             │        │ • weather_observations│
                 │ • farms               │        │ • field_observations  │
                 │ • crops               │        │ • agricultural_alerts │
                 │ • seasons             │        │ • sensor_observations │
                 │ • crop_cycles         │        │ • activity_logs       │
                 │ • soil_records        │        └───────────────────────┘
                 │ • irrigation_records  │
                 │ • fertilizer_records  │
                 │ • yield_records       │
                 └───────────────────────┘
```

### Relational Database (MySQL 8.0+)
- **Role**: Normalized operational data store enforcing strict foreign key integrity, domain check constraints, and cascading deletes.
- **Key Tables**:
  - `farmers`: Farmer demographic profile, phone unique index, village, district, state.
  - `farms`: Parcel area (hectares), soil classification, irrigation infrastructure, latitude/longitude.
  - `crops`: Botanical catalog, ideal season, typical growth duration, reference standard yield.
  - `seasons`: Kharif, Rabi, Zaid, Perennial, year, start/end dates.
  - `crop_cycles`: Lifecycle tracking (Planned, Active, Harvested, Failed), sowing/harvest dates.
  - `soil_records`: Laboratory chemical analysis (pH, N, P, K, moisture %, EC, OC).
  - `irrigation_records`: Water volume applied (liters), method (Drip, Sprinkler, Canal Flood, Tube Well), duration.
  - `fertilizer_records`: Chemical input type (Urea, DAP, MOP, etc.), dosage (kg), application technique.
  - `yield_records`: Harvest output (kg), yield per hectare, quality grade (Grade A–D).

### Document Database (MongoDB 6.0+)
- **Role**: High-throughput, semi-structured document store for sensor observations, time-series telemetry, and rule-based alerts.
- **Collections**:
  - `weather_observations`: Station meteorological logs (temperature, humidity, precipitation, wind speed, solar radiation).
  - `field_observations`: Agronomist scouting reports, pest/disease symptoms, crop stage metadata.
  - `agricultural_alerts`: Deterministic rule exceptions with severity (CRITICAL, WARNING, INFO), metric value, and threshold.
  - `sensor_observations`: IoT moisture, temperature, and electrical conductivity telemetry payloads.
  - `activity_logs`: Governance audit logs for data modifications.

---

## 3. High-Fidelity Fallback Architecture

To guarantee 100% operational readiness across developer workstations, classroom grading, and offline environments, AgriSense implements an automatic **verified fallback mechanism**:

1. Upon invocation, connection verification probes `MySQL` and `MongoDB`.
2. If MySQL credentials are not supplied in `.env`, the repository layer automatically pivots to the verified, normalized CSV archives in `data/raw/`.
3. If MongoDB is unreachable, the observation repository pivots to the JSON archive in `data/raw/`.
4. The UI status strip clearly discloses data source status:
   - `MySQL: Connected` vs `MySQL: Verified Local Fallback`
   - `MongoDB: Connected` vs `MongoDB: Verified Local Fallback`
5. No fake mock timestamps or randomized numbers are fabricated—all calculations query real records.

---

## 4. Layer Separation & Design Patterns

- **UI Layer (`ui/`)**: Pure presentation, layout, and Plotly figure rendering. No direct SQL queries.
- **Service Layer (`services/`)**: Business logic, entity enrichment, multi-table aggregation, alert triggering.
- **Analytics Layer (`analytics/`)**: Mathematical formulas, descriptive statistics (mean, median, standard deviation), correlation matrices, ratio computations.
- **Repository Layer (`repositories/`)**: Abstracted data access layer providing identical method signatures (`get_all()`, `get_by_id()`, `create()`) regardless of whether backed by live MySQL/MongoDB or local CSV/JSON archives.
- **Data Cleaner (`utils/data_cleaning.py`)**: Strict hygiene module tracking every dropped duplicate or clamped outlier in an internal audit trail.
