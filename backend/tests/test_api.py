import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_data import seed_database

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
    yield

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["telemetry_stream"] == "NOMINAL"

def test_dashboard_overview():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["active_units_total"] >= 48
    assert data["critical_vehicle_id"] == "AC-2048"
    assert data["critical_temp_c"] == 8.2
    assert data["cargo_asset_exposure_usd"] == 142000.0

def test_fleet_endpoints():
    # List fleet
    res = client.get("/api/v1/fleet")
    assert res.status_code == 200
    fleet = res.json()
    assert len(fleet) >= 5
    vehicle_ids = [v["id"] for v in fleet]
    assert "AC-2048" in vehicle_ids

    # Vehicle readings
    res_readings = client.get("/api/v1/fleet/AC-2048/readings")
    assert res_readings.status_code == 200
    readings = res_readings.json()
    assert len(readings) > 0
    assert readings[-1]["temperature_c"] >= 8.0

def test_incident_and_ai_agent_analysis():
    # Get incident
    res = client.get("/api/v1/incidents/INC-8921-TH")
    assert res.status_code == 200
    inc = res.json()
    assert inc["vehicle_id"] == "AC-2048"
    assert inc["ecu_fault_code"] == "E-104"

    # Run AI Analysis
    res_analysis = client.post("/api/v1/incidents/INC-8921-TH/analyze")
    assert res_analysis.status_code == 200
    analysis = res_analysis.json()
    assert analysis["incident_id"] == "INC-8921-TH"
    assert analysis["risk_level"] == "CRITICAL"
    assert "Cold Storage A" in analysis["suggested_recovery_facility"]
    assert analysis["confidence_score"] >= 0.90
    assert len(analysis["evidence_checklist"]) > 0

def test_recovery_facilities_and_approval_workflow():
    # List facilities
    res_fac = client.get("/api/v1/recovery/facilities")
    assert res_fac.status_code == 200
    facilities = res_fac.json()
    assert len(facilities) >= 3
    assert facilities[0]["short_name"] == "Cold Storage A"
    assert facilities[0]["estimated_travel_minutes"] == 38

    # Approve recovery plan
    res_plans = client.get("/api/v1/incidents/INC-8921-TH/recovery-plans")
    assert res_plans.status_code == 200
    plans = res_plans.json()
    assert len(plans) > 0
    plan_id = plans[0]["id"]

    # Dispatcher approval
    approve_res = client.post(
        f"/api/v1/recovery-plans/{plan_id}/approve",
        json={"authorized_by": "Sarah Jenkins", "role": "Lead Dispatcher"}
    )
    assert approve_res.status_code == 200
    approval_data = approve_res.json()
    assert approval_data["success"] is True
    assert approval_data["status"] == "APPROVED"
    assert "SHA256" in approval_data["signature_hash"]

    # Verify state persistence throughout application
    updated_plan = client.get(f"/api/v1/recovery-plans/{plan_id}").json()
    assert updated_plan["status"] == "APPROVED"
    assert "Sarah Jenkins" in updated_plan["approved_by"]

    # Verify vehicle is now DIVERTED and incident is MITIGATING
    veh = client.get("/api/v1/fleet/AC-2048").json()
    assert veh["status"] == "DIVERTED"

    inc = client.get("/api/v1/incidents/INC-8921-TH").json()
    assert inc["status"] == "MITIGATING"

    # Verify activity logs contain the dispatch audit record
    res_logs = client.get("/api/v1/activity-logs")
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert any("DIVERSION_APPROVED" in l["event_type"] for l in logs)
