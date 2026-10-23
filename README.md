# AeroCold — Autonomous Cold-Chain Intelligence Platform

AeroCold is a full-stack telematics, thermal risk control, and autonomous recovery platform for perishable logistics. It couples real-time CAN-bus sensory monitoring with an AI recovery agent and deterministic risk rules to safeguard cold-chain cargo under refrigeration failure conditions.

The frontend preserves 100% of the Google Stitch editorial design system (monochrome high-contrast precision, Newsreader editorial serif headers, Inter interface metrics, glassmorphic HUD overlays, and tabular lining telematics).

---

## Architecture Overview

```
aerocold/
├── backend/
│   ├── app/
│   │   ├── config.py              # Configuration & settings management (.env)
│   │   ├── database.py            # SQLite / SQLAlchemy 2.0 engine & session
│   │   ├── models.py              # Vehicles, Incidents, Facilities, Plans, Approvals, Logs
│   │   ├── schemas.py             # Pydantic v2 validation models
│   │   ├── seed_data.py           # Idempotent demo dataset seeder
│   │   ├── main.py                # FastAPI app with static frontend mounting
│   │   ├── services/
│   │   │   ├── agent_tools.py     # Deterministic telemetry, risk, facilities, & approval tools
│   │   │   ├── gemini_agent.py    # Google Gemini AI reasoning with deterministic fallback
│   │   │   └── maps_service.py    # Google Maps Routes API integration with calibrated fallback
│   │   └── routers/
│   │       ├── dashboard.py       # GET /api/v1/dashboard/overview
│   │       ├── fleet.py           # GET /api/v1/fleet, GET /api/v1/fleet/{id}/readings
│   │       ├── incidents.py       # GET /api/v1/incidents, POST /api/v1/incidents/{id}/analyze
│   │       ├── recovery.py        # GET /api/v1/recovery/facilities, POST /api/v1/recovery-plans/{id}/approve
│   │       ├── analytics.py       # GET /api/v1/analytics/overview
│   │       ├── notifications.py   # GET /api/v1/notifications, GET /api/v1/activity-logs
│   │       └── settings.py        # GET /api/v1/settings
│   └── tests/
│       └── test_api.py            # Automated pytest test suite
├── frontend/
│   ├── index.html                 # Brand & Architecture Landing Page
│   ├── overview.html              # Operations Overview Dashboard HUD
│   ├── incident.html              # Incident Workspace (Unit AC-2048)
│   ├── recovery.html              # Multi-Hub Recovery Facility Planner
│   ├── fleet.html                 # Live Fleet Registry
│   ├── analytics.html             # Cold-Chain Analytics & Compliance Dossier
│   ├── settings.html              # Platform Integrations & Settings
│   ├── js/
│   │   ├── api.js                 # Centralized API client for /api/v1
│   │   ├── overview.js            # Live KPI telemetry, authorization, & drill triggers
│   │   ├── incident.js            # Excursion simulation & dispatch authorization
│   │   ├── recovery.js            # Multi-facility comparison matrix controller
│   │   └── navigation.js          # Unified header navigation & routing
│   ├── package.json               # Vite build configuration
│   └── vite.config.js             # Multi-page build setup with API proxy
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Backend Python dependencies
└── test_demo_flow.py              # End-to-end AC-2048 demonstration script
```

---

## Quickstart

### 1. Backend Server
Install dependencies and run the backend:
```bash
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- Open `http://127.0.0.1:8000/health` to verify server health.
- Open `http://127.0.0.1:8000/overview` to open the Operations Overview HUD directly.

### 2. Frontend Development & Build
The frontend is built with Vite and runs standalone or proxied:
```bash
cd frontend
npm install
npm run dev      # Local Vite server at http://localhost:5173
npm run build    # Production build into dist/
```

### 3. Run Automated Tests
```bash
python -m pytest backend/tests/test_api.py -v
```

### 4. Run Full AC-2048 Demo Scenario
```bash
python test_demo_flow.py
```

---

## Required Demo Scenario (Unit AC-2048)
- **Vehicle**: `AC-2048`
- **Cargo**: Fresh Organic Strawberries (Driscoll's), $142,000 value
- **Target Temperature**: `2.0°C ± 1.5°C`
- **Simulated Current Temperature**: `8.2°C` (Limit breached at 4.0°C)
- **ECU Fault**: Code `E-104` (Evaporator blower fan RPM drop)
- **Candidate Recovery Facility**: `Cold Storage A (Berkeley Port Terminal)`
- **Estimated Travel Time**: `38 minutes` (Bay 4 pre-chilled intake reserved)
- **Biological Yield Preserved**: `99.4%` ($141,148 of $142,000 saved)
- **Approval**: Authorized by Lead Dispatcher with cryptographic signature & EDI 214 dispatch token.
