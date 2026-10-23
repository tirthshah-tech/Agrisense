# AgriSense Dashboard Design System & UI/UX Guide

## 1. Design Direction: "Modern Botanical Intelligence"

AgriSense rejects generic administrative templates, purple gradients, and basic academic prototypes. It implements a refined, natural design language inspired by environmental monitoring stations and sustainable agriculture platforms.

### Core Color Palette Tokens
| Token | Hex Value | Semantic Role in AgriSense |
|---|---|---|
| **Deep Forest Green** | `#173F35` | Hero backgrounds, primary headings, dark KPI cards, chart title emphasis. |
| **Agricultural Green** | `#26734D` | Brand primary color, buttons, active navigation markers, positive trends. |
| **Fresh Leaf Green** | `#78A85A` | Subheadings, KPI accent bars, secondary series in Plotly charts. |
| **Pale Sage** | `#E8EFE5` | Card backgrounds, tab headers, muted status badges. |
| **Warm Off-White** | `#F7F8F3` | Canvas background, reducing visual fatigue compared to stark white. |
| **White Surface** | `#FFFFFF` | Primary data cards, tables, Plotly canvas background. |
| **Dark Charcoal** | `#24332C` | High-contrast body typography, table values, chart ticks. |
| **Muted Text** | `#738078` | Subtitles, KPI units, table column descriptions. |
| **Soft Border** | `#E1E8DF` | Card borders, Plotly gridlines, table row separators. |
| **Muted Amber** | `#D69B36` | Warning status badges, standard benchmark yield series. |
| **Muted Red** | `#C65C50` | Critical alert badges, temperature extremes. |

---

## 2. Typography Hierarchy

AgriSense uses **Manrope** (with **DM Sans** as secondary fallback) to maintain an editorial, clean aesthetic:

- **Hero Title:** 1.95rem, weight 800, tight letter-spacing (`-0.025em`).
- **Page Subtitle:** 0.95rem, weight 500, soft contrast (`#E8EFE5`).
- **Section Heading:** 1.15rem – 1.30rem, weight 700 (`#173F35`).
- **KPI Value:** 1.85rem – 2.10rem, weight 800 (`#173F35` or `#FFFFFF`).
- **KPI Label:** 0.72rem, weight 700, uppercase with letter-spacing (`0.08em`).
- **Body & Table Text:** 0.85rem – 0.90rem, weight 500.

---

## 3. Visual Features & Reusable Components

### A. Photographic Agricultural Hero Banner
- Located at the top of the Executive Dashboard.
- Features high-resolution local photography (`assets/hero_banner.jpg`) depicting Maharashtra's terraced agricultural landscapes.
- Overlaid with a dark forest green directional gradient (`rgba(23,63,53,0.92)` to `rgba(38,115,77,0.76)`).
- Complete pure CSS botanical gradient fallback if the image asset is absent.

### B. Custom KPI Cards (`render_kpi`)
- Custom HTML/CSS component with 3px top green accent line.
- Smooth hover elevation (`translateY(-2px)`) and subtle box-shadow.
- Hero variant (`kpi-card-dark`) utilizing `#173F35` gradient for primary headline metrics.

### C. Plotly Botanical Chart Theme (`apply_agrisense_theme`)
All Plotly figures across the 11 pages use a standardized helper enforcing:
- White plot background (`#FFFFFF`).
- Transparent paper background (`rgba(0,0,0,0)`).
- Soft border gridlines (`#E1E8DF`).
- Manrope typography for ticks and axes.
- Deep forest hover tooltip cards with white text.

### D. Global Multidimensional Filter Bar
- Sits below the hero banner.
- Filters Year, Season, Crop Variety, and District.
- Propagates filters simultaneously to all KPIs, charts, and tables.
- Includes a one-click `↺ Reset` button restoring full dataset visibility.

---

## 4. Navigation Architecture (11 Pages)

```
OVERVIEW
 └── 📊 Dashboard (Executive KPIs, Multi-Chart Overview, Dynamic Insights, SDG Panel)

MONITORING
 ├── 🏡 Farms (Directory, Holding Boundaries, District/Soil Filters, Search)
 ├── 🌾 Crop Analytics (Acreage Share, Production, Growth Duration, Agronomic Matrix)
 ├── 🧪 Soil Monitoring (pH Distribution, NPK Deficiencies, Moisture vs N, Lab Logs)
 └── ⛅ Weather (District Temperatures, Rainfall, Weekly Trends, Telemetry Logs)

RESOURCES
 ├── 💧 Water & Irrigation (Method Breakdown, Duration, Frequency, Logs)
 └── 🌿 Fertilizer (Chemical Types, Application Methods, Timeline, Logs)

PERFORMANCE
 ├── 📈 Yield Analysis (Benchmark Gap, Grade Breakdown, Seasonal Yields, Farm Rankings)
 └── ⚡ Resource Efficiency (Water & Fertilizer Productivity Ratios, Intensity Matrix)

SYSTEM
 ├── 🚨 Alerts (Rule Engine Trigger, Severity Breakdown, Deduplicated Registry)
 └── 🛡️ Data Quality (10-Dataset Hygiene Audit, Connection Diagnostics, Sanitizer Test)
```
