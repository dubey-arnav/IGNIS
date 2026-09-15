# IGNIS — Frontend Application

**IGNIS: Industrial Thermal Anomaly Classification & Monitoring System**

IGNIS is an enterprise web application designed for real-time detection, spatial classification, and risk evaluation of industrial thermal anomalies (refinery fires, power plant flaring, industrial heat sources) versus natural wildfires and seasonal agricultural burning.

---

## Technical Architecture & Technology Stack

- **Framework**: React 18 + Vite
- **Design System**: Enterprise Navy Core Palette (CSS Custom Properties)
- **Routing**: React Router DOM v6
- **Mapping Engine**: Leaflet + React Leaflet (BBox querying, custom circle markers, popups)
- **Data Visualization**: Recharts (Pie, Line, Stacked Bar charts)
- **HTTP Client**: Axios with automatic fallback to high-fidelity mock datasets when backend endpoints are offline
- **Icons**: Lucide React

---

## Required Environment Variables

Create `.env` inside `frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Quick Start & Installation

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Launch development server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## Production Build

```bash
npm run build
```

The output bundle will be compiled into `frontend/dist/`.

---

## Application Route Map

| Route | Page | Key Features |
|---|---|---|
| `/` | **Dashboard** | KPI stat cards, classification breakdown grid (primary output), risk tier summary, model accuracy banner, recent alerts. |
| `/map` | **Interactive Map** | Interactive Leaflet map with classification-coded circle markers, bounding box listener (`moveend`), map legend, primary classification chips & secondary risk tier filters (`FilterBar`), side event drawer panel (`EventDetailPanel`). |
| `/analytics` | **Analytics & Trends** | Classification distribution pie chart, temporal series line chart, facility distance profile stacked bar chart (0-500m, 500-1500m, 1.5-5km, 5-10km, >10km). |
| `/facilities` | **Facilities Directory** | Searchable registry of refineries, power plants, and metallurgy hubs with spatial anomaly density metrics. |
| `/facilities/:id` | **Facility Detail** | Detailed facility profile, spatial anomaly density breakdown, and recent nearby detections list. |
| `/alerts` | **Alerts Feed** | Dedicated feed of high-priority Industrial Fire and Persistent Industrial thermal sources. |
| `/about` | **Methodology** | Explanatory 9-stage pipeline guide for non-technical judges covering NASA FIRMS, OSM context, DBSCAN clustering, XGBoost classifier (98.6% accuracy, 19 features), and risk engine. |

---

## Resilient Offline / Demo Behavior

When the FastAPI backend or database is offline, the centralized API layer (`src/api/*`) gracefully falls back to realistic Indian spatial mock datasets (`src/data/mockData.js`). The application remains 100% functional from a visual and interactive standpoint without crashing.
