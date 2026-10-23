import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0)

print("=== STEP 1: Load Dashboard ===")
dash = client.get("/api/v1/dashboard/overview").json()
print("Dashboard loaded: %s units, Critical incident: %s at %s°C (Target: %s°C)" % (
    dash["active_units_total"],
    dash["critical_vehicle_id"],
    dash["critical_temp_c"],
    dash["critical_temp_target_c"]
))

print("\n=== STEP 2: Open Incident AC-2048 & History ===")
inc = client.get("/api/v1/incidents/INC-8921-TH").json()
print("Incident %s: %s, ECU Fault: %s" % (inc["id"], inc["title"], inc["ecu_fault_code"]))
readings = client.get("/api/v1/fleet/AC-2048/readings").json()
print("Telemetry history: %d readings. Trajectory starts at %s°C and reaches %s°C" % (
    len(readings),
    readings[0]["temperature_c"],
    readings[-1]["temperature_c"]
))

print("\n=== STEP 3: Run AI Risk Assessment & Recovery Recommendation ===")
analysis = client.post("/api/v1/incidents/INC-8921-TH/analyze").json()
print("Risk Level: %s" % analysis["risk_level"])
print("Recommended Facility: %s" % analysis["suggested_recovery_facility"])
print("Confidence Score: %.1f%%" % (analysis["confidence_score"] * 100))
print("AI Narrative: %s..." % analysis["ai_analysis_narrative"][:140])
print("Evidence Checklist: %s" % analysis["evidence_checklist"][:2])

print("\n=== STEP 4: Compare Recovery Destinations ===")
facilities = client.get("/api/v1/recovery/facilities").json()
for f in facilities:
    print("- %s: %d mins, Bay: %s, Recommended: %s" % (
        f["short_name"], f["estimated_travel_minutes"], f["bay_status"], f["is_recommended"]
    ))

print("\n=== STEP 5: Approve Plan as Lead Dispatcher ===")
plan_id = analysis["recovery_plan"]["id"]
approval = client.post(
    "/api/v1/recovery-plans/%s/approve" % plan_id,
    json={"authorized_by": "Sarah Jenkins", "role": "Lead Dispatcher", "notes": "Authorized autonomous diversion via AeroCold HUD."}
).json()
print("Approval Result: Success=%s, Status=%s, Signature=%s" % (
    approval["success"], approval["status"], approval["signature_hash"]
))

print("\n=== STEP 6: Verify Database Persistence & Dashboard Consistency ===")
updated_plan = client.get("/api/v1/recovery-plans/%s" % plan_id).json()
print("Plan Status: %s, Approved By: %s" % (updated_plan["status"], updated_plan["approved_by"]))

vehicle = client.get("/api/v1/fleet/AC-2048").json()
print("Vehicle AC-2048 Status: %s" % vehicle["status"])

incident = client.get("/api/v1/incidents/INC-8921-TH").json()
print("Incident Status: %s" % incident["status"])

dash_after = client.get("/api/v1/dashboard/overview").json()
print("Dashboard After Refresh: Directive Status=%s" % dash_after["recommended_plan"]["status"])

logs = client.get("/api/v1/activity-logs").json()
print("Latest Activity Log: [%s] %s" % (logs[0]["event_type"], logs[0]["message"]))
