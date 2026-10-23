# AgriSense Agronomic Analytics & Rule Engine Specification

## 1. Core Mathematical & Agronomic Formulas

AgriSense enforces verified scientific formulas grounded in agricultural economics and agronomic engineering. All formulas incorporate zero-division guards and strict unit consistency.

### A. Land Productivity (Yield per Hectare)
$$\text{Yield per Hectare (kg/ha)} = \frac{\text{Total Harvested Yield (kg)}}{\text{Cultivated Parcel Area (ha)}}$$
- **Zero-Division Protection:** $\text{Parcel Area} = \max(\text{area}, 0.01)$
- **Usage:** Benchmarked against reference crop standards in `crops` catalog to evaluate yield gaps.

### B. Water Application Intensity
$$\text{Water Intensity (L/ha)} = \frac{\text{Irrigation Water Consumed (Liters)}}{\text{Cultivated Parcel Area (ha)}}$$
$$\text{Water Intensity (m}^3\text{/ha)} = \frac{\text{Water Intensity (L/ha)}}{1000}$$
- **SDG 12 Context:** Compares water intensity between Micro-Irrigation (Drip/Sprinkler) and Surface Irrigation (Canal Flood).

### C. Fertilizer Application Intensity
$$\text{Fertilizer Intensity (kg/ha)} = \frac{\text{Total Fertilizer Applied (kg)}}{\text{Cultivated Parcel Area (ha)}}$$
- **Nutrient Stratification:** Computed independently for macro-nutrients (N, P, K) and commercial chemical compounds (Urea, DAP, MOP, 10:26:26).

### D. Crop Water Productivity (WP)
$$\text{Water Productivity (kg/m}^3\text{)} = \frac{\text{Total Harvested Yield (kg)}}{\text{Irrigation Water Consumed (m}^3\text{)}}$$
$$\text{Water Footprint (L/kg)} = \frac{\text{Irrigation Water Consumed (Liters)}}{\text{Total Harvested Yield (kg)}}$$
- **Agronomic Limitation:** Reflects applied irrigation water only. Effective precipitation contribution is not subtracted in unmetered rainfed conditions.

### E. Fertilizer Productivity (FP)
$$\text{Fertilizer Productivity (kg/kg)} = \frac{\text{Total Harvested Yield (kg)}}{\text{Total Agrochemical Input Applied (kg)}}$$
- **Agronomic Limitation:** Productivity ratios naturally differ between high-biomass perennials (e.g., Sugarcane) and legumes capable of biological nitrogen fixation (e.g., Soybean, Chickpea).

---

## 2. Deterministic Rule-Based Alert Engine

Alerts in AgriSense are **100% deterministic**. They do not use AI/ML or black-box predictions. Each alert corresponds to a clear, measurable agronomic threshold:

| Rule Name | Target Domain | Trigger Condition | Severity | Actionable Operational Advice |
|---|---|---|---|---|
| **Severe Moisture Deficit** | Soil / Water | $\text{Moisture} < 20.0\%$ | `CRITICAL` | Immediate irrigation scheduling required to avoid permanent wilting point. |
| **Low Soil Moisture** | Soil / Water | $20.0\% \le \text{Moisture} < 25.0\%$ | `WARNING` | Soil moisture falling below optimal field capacity. Plan next irrigation cycle. |
| **Severe Soil Acidity** | Soil Chemistry | $\text{pH} < 5.2$ | `CRITICAL` | Severe aluminum toxicity risk. Apply agricultural lime ($\text{CaCO}_3$) per soil buffer test. |
| **Soil Acidity** | Soil Chemistry | $5.2 \le \text{pH} < 6.0$ | `WARNING` | Moderately acidic. Monitor phosphorus fixation and plan liming amendments. |
| **Soil Alkalinity** | Soil Chemistry | $8.0 < \text{pH} \le 8.7$ | `WARNING` | Alkaline condition. Micronutrient availability (Fe, Zn, Mn) restricted. |
| **Severe Soil Alkalinity** | Soil Chemistry | $\text{pH} > 8.7$ | `CRITICAL` | Sodic/saline risk. Apply gypsum ($\text{CaSO}_4$) and flush with adequate drainage. |
| **Excessive Single Irrigation** | Resource Stewardship | $\text{Volume} > 25,000 \text{ L/event}$ | `CRITICAL` | Potential deep percolation and nutrient leaching. Inspect drip regulators. |
| **High Irrigation Event** | Resource Stewardship | $\text{Volume} > 15,000 \text{ L/event}$ | `WARNING` | High water consumption. Verify irrigation duration against crop evapotranspiration. |
| **Over-Irrigation in Rainfall** | Resource Stewardship | Irrigation logged when daily $\text{Rainfall} > 25 \text{ mm}$ | `WARNING` | Irrigation during heavy rainfall causes runoff and waterlogging. Suppress pumps. |
| **Excessive Agrochemical Application** | Input Efficiency | $\text{Fertilizer Dosage} > 350 \text{ kg/event}$ | `CRITICAL` | Severe fertilizer burn and groundwater nitrate runoff hazard. Split dosage into fertigation pulses. |
| **Critical Yield Failure** | Production Gap | $\text{Actual Yield} < 50\% \text{ Standard Benchmark}$ | `CRITICAL` | Severe cultivation underperformance. Investigate drought, pest attack, or soil salinity. |
| **Yield Benchmark Gap** | Production Gap | $50\% \le \text{Actual Yield} < 75\% \text{ Standard}$ | `WARNING` | Moderate underperformance compared to regional research station yields. |

### Deduplication Strategy
To prevent alert explosion on dashboard refresh, each alert is assigned a deterministic deduplication key:
$$\text{dedup\_key} = f(\text{farm\_id}, \text{alert\_type}, \text{timestamp})$$
MongoDB uses an `$setOnInsert` upsert on `dedup_key`, guaranteeing idempotency.

---

## 3. Dynamic Data-Driven Agricultural Insights

Insights are dynamically generated across five key indicators:
1. **Highest Yielding Crop:** Statistical maximum of average yield across all harvested cycles.
2. **Irrigation Efficiency Disparity:** Direct percentage water savings computed between Drip ($Mean_{drip}$) and Flood ($Mean_{flood}$):
   $$\text{Savings \%} = \frac{Mean_{flood} - Mean_{drip}}{Mean_{flood}} \times 100$$
3. **Soil Health Diagnostic:** Proportion of parcels with Nitrogen deficits ($N < 280\text{ kg/ha}$) and mean regional pH.
4. **Agrochemical Volume Leader:** Chemical fertilizer type accounting for the highest cumulative mass.
5. **Field Alert Pressure:** Count of open anomalies requiring agronomic inspection.
