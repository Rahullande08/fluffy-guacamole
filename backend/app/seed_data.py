from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from . import models

def seed_database(db: Session):
    """Seed initial demo data idempotently without duplicate records."""
    # Check if already seeded
    existing_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == "AC-2048").first()
    if existing_vehicle:
        return

    now = datetime.now(timezone.utc)

    # 1. Seed Vehicles
    vehicles = [
        models.Vehicle(
            id="AC-2048",
            name="Unit AC-2048",
            carrier="SwiftCold Carrier LLC",
            driver_name="M. Hansen",
            driver_phone="+1 (555) 234-8921",
            status="ALERT",
            latitude=37.4219,
            longitude=-122.0840,
            speed_mph=58.0,
            heading="NW 312°",
            genset_fuel_pct=82.0,
            cargo_name="Organic Strawberries (Driscoll's)",
            cargo_weight_kg=4800.0,
            cargo_pallets=18,
            cargo_value_usd=142000.0,
            target_temp_c=2.0,
            threshold_temp_c=4.0,
            current_temp_c=8.2,
            created_at=now - timedelta(hours=3),
            updated_at=now
        ),
        models.Vehicle(
            id="AC-1012",
            name="Unit AC-1012",
            carrier="Pacific Freight Express",
            driver_name="D. Chen",
            driver_phone="+1 (555) 345-6789",
            status="NOMINAL",
            latitude=37.3861,
            longitude=-122.0839,
            speed_mph=62.0,
            heading="NE 045°",
            genset_fuel_pct=91.0,
            cargo_name="Grade A Whole Milk & Cream",
            cargo_weight_kg=12000.0,
            cargo_pallets=24,
            cargo_value_usd=64000.0,
            target_temp_c=2.0,
            threshold_temp_c=4.0,
            current_temp_c=2.1,
            created_at=now - timedelta(hours=4),
            updated_at=now
        ),
        models.Vehicle(
            id="AC-3091",
            name="Unit AC-3091",
            carrier="Arctic Ocean Logistics",
            driver_name="R. Kowalski",
            driver_phone="+1 (555) 456-7890",
            status="NOMINAL",
            latitude=37.5485,
            longitude=-122.0592,
            speed_mph=55.0,
            heading="W 270°",
            genset_fuel_pct=76.0,
            cargo_name="Wild Alaskan Sockeye Salmon",
            cargo_weight_kg=8500.0,
            cargo_pallets=20,
            cargo_value_usd=118000.0,
            target_temp_c=-18.0,
            threshold_temp_c=-12.0,
            current_temp_c=-18.2,
            created_at=now - timedelta(hours=5),
            updated_at=now
        ),
        models.Vehicle(
            id="AC-4044",
            name="Unit AC-4044",
            carrier="Valley Cold Transport",
            driver_name="S. Martinez",
            driver_phone="+1 (555) 567-8901",
            status="NOMINAL",
            latitude=37.7749,
            longitude=-122.4194,
            speed_mph=50.0,
            heading="N 005°",
            genset_fuel_pct=88.0,
            cargo_name="Hydroponic Butter Lettuce & Herbs",
            cargo_weight_kg=3200.0,
            cargo_pallets=14,
            cargo_value_usd=52000.0,
            target_temp_c=3.0,
            threshold_temp_c=6.0,
            current_temp_c=3.8,
            created_at=now - timedelta(hours=2),
            updated_at=now
        ),
        models.Vehicle(
            id="AC-5120",
            name="Unit AC-5120",
            carrier="BioLogistics Solutions",
            driver_name="A. Vance",
            driver_phone="+1 (555) 678-9012",
            status="NOMINAL",
            latitude=37.6879,
            longitude=-122.4702,
            speed_mph=60.0,
            heading="S 180°",
            genset_fuel_pct=94.0,
            cargo_name="mRNA Biologics & Vaccines",
            cargo_weight_kg=1200.0,
            cargo_pallets=6,
            cargo_value_usd=290000.0,
            target_temp_c=4.0,
            threshold_temp_c=8.0,
            current_temp_c=4.5,
            created_at=now - timedelta(hours=6),
            updated_at=now
        )
    ]
    db.add_all(vehicles)
    db.commit()

    # 2. Seed Sensor Readings for AC-2048 (Past 45 minutes temperature curve)
    # Target: 2.0°C, drifts up to 8.2°C at present
    readings = []
    # 45 minutes ago down to 0
    temp_trajectory = [
        (-45, 2.0, False),
        (-40, 2.1, False),
        (-35, 2.3, False),
        (-30, 2.7, False),
        (-25, 3.2, False),
        (-20, 3.8, False),
        (-15, 4.4, True),  # Excursion begins past 4.0°C
        (-10, 5.8, True),
        (-5, 7.2, True),
        (-2, 7.9, True),
        (0, 8.2, True)     # Current
    ]
    for min_offset, temp, is_anom in temp_trajectory:
        t_time = now + timedelta(minutes=min_offset)
        readings.append(models.SensorReading(
            vehicle_id="AC-2048",
            sensor_code="T-04",
            temperature_c=temp,
            humidity_pct=88.0 + (temp * 0.5),
            timestamp=t_time,
            is_anomaly=is_anom,
            is_simulated=True
        ))
        # Auxiliary sensor readings
        readings.append(models.SensorReading(
            vehicle_id="AC-2048",
            sensor_code="T-01_AIR_RETURN",
            temperature_c=round(temp + 1.2, 1),
            humidity_pct=84.0,
            timestamp=t_time,
            is_anomaly=is_anom,
            is_simulated=True
        ))
        readings.append(models.SensorReading(
            vehicle_id="AC-2048",
            sensor_code="T-02_AMBIENT",
            temperature_c=24.5,
            humidity_pct=42.0,
            timestamp=t_time,
            is_anomaly=False,
            is_simulated=True
        ))
    db.add_all(readings)
    db.commit()

    # 3. Seed Incident for AC-2048
    incident = models.Incident(
        id="INC-8921-TH",
        vehicle_id="AC-2048",
        title="Refrigeration Anomaly Detected",
        description="Evaporator Blower Fan RPM Drop (320 RPM vs 1450 RPM cmd). Dual compressor forced to 40% duty cycle.",
        ecu_fault_code="E-104",
        severity="CRITICAL",
        status="ACTIVE",
        excursion_temp_c=8.2,
        drift_rate_c_per_min=0.22,
        breach_time=now - timedelta(minutes=15),
        time_to_spoilage_minutes=102, # 1h 42m
        biological_yield_projected_pct=99.4,
        created_at=now - timedelta(minutes=15),
        updated_at=now
    )
    db.add(incident)
    db.commit()

    # 4. Seed Recovery Facilities
    facilities = [
        models.RecoveryFacility(
            id="FAC-001",
            name="Cold Storage A (Berkeley Port Terminal)",
            short_name="Cold Storage A",
            address="Pier 3, Maritime Blvd, Berkeley, CA 94710",
            latitude=37.8651,
            longitude=-122.3108,
            distance_km=4.2,
            estimated_travel_minutes=38, # Requirement: Illustrative estimated travel time: 38 minutes
            bay_status="Bay 4 Intake Clear",
            prechilled_dock_ready=True,
            temp_range_min_c=-25.0,
            temp_range_max_c=4.0,
            capacity_pct=64.0,
            rating=4.9,
            is_recommended=True,
            hourly_rate_usd=185.0
        ),
        models.RecoveryFacility(
            id="FAC-002",
            name="Oakland Metro Intermodal Cold Hub",
            short_name="Oakland Cold Hub",
            address="700 7th St, Oakland, CA 94607",
            latitude=37.8044,
            longitude=-122.2712,
            distance_km=6.8,
            estimated_travel_minutes=46,
            bay_status="Bay 1 Standby",
            prechilled_dock_ready=True,
            temp_range_min_c=-20.0,
            temp_range_max_c=6.0,
            capacity_pct=81.0,
            rating=4.7,
            is_recommended=False,
            hourly_rate_usd=210.0
        ),
        models.RecoveryFacility(
            id="FAC-003",
            name="Richmond Cryo-Logistics Center",
            short_name="Richmond Cryo Center",
            address="1200 S 10th St, Richmond, CA 94804",
            latitude=37.9358,
            longitude=-122.3478,
            distance_km=14.1,
            estimated_travel_minutes=62,
            bay_status="Bay 6 Staged (Queue: 1)",
            prechilled_dock_ready=False,
            temp_range_min_c=-30.0,
            temp_range_max_c=2.0,
            capacity_pct=92.0,
            rating=4.5,
            is_recommended=False,
            hourly_rate_usd=165.0
        )
    ]
    db.add_all(facilities)
    db.commit()

    # 5. Seed Recovery Plan for INC-8921-TH
    plan = models.RecoveryPlan(
        id="PLAN-7741",
        incident_id="INC-8921-TH",
        vehicle_id="AC-2048",
        facility_id="FAC-001",
        status="RECOMMENDED",
        confidence_score=0.96,
        estimated_arrival_minutes=38,
        projected_salvage_usd=141148.0,
        biological_yield_pct=99.4,
        ai_reasoning=(
            "Unit AC-2048 reefer subsystem indicates an active thermal excursion breach at 8.2°C "
            "(+6.2°C above setpoint) with positive thermal velocity (+0.22°C/min). "
            "Diversion to Cold Storage A (Berkeley Port Terminal) achieves cross-dock intake in "
            "38 minutes, preserving 99.4% biological yield and safeguarding $141,148 of asset value."
        ),
        evidence_summary=(
            "1. Sensor T-04 Core CAN-bus telematics verified (1.8s pulse rate).\n"
            "2. Excursion exceeds critical 4.0°C threshold by 4.2°C.\n"
            "3. Cold Storage A provides verified Bay 4 Intake Clear with pre-chilled cryo-blast capability.\n"
            "4. 38-minute transit vector provides 64 minutes of safety margin before irreversible strawberry cellular breakdown."
        ),
        assumptions=(
            "Corridor traffic along I-90 W remains nominal at 58 MPH; secondary genset duty cycle remains stable at 40%; "
            "cross-dock intake bay remains cleared upon arrival."
        ),
        created_by="AeroCold Autonomous Intelligence Agent",
        created_at=now - timedelta(minutes=12),
        updated_at=now - timedelta(minutes=12)
    )
    db.add(plan)
    db.commit()

    # 6. Seed Notifications
    notifications = [
        models.Notification(
            id="NOTIF-001",
            title="CRITICAL THERMAL EXCURSION",
            message="Unit AC-2048 core temperature breached 4.0°C threshold. Currently at 8.2°C.",
            severity="CRITICAL",
            is_read=False,
            timestamp=now - timedelta(minutes=15)
        ),
        models.Notification(
            id="NOTIF-002",
            title="AI RECOMMENDATION READY",
            message="Plan PLAN-7741 generated: Divert to Cold Storage A (ETA 38m, 99.4% yield).",
            severity="INFO",
            is_read=False,
            timestamp=now - timedelta(minutes=12)
        ),
        models.Notification(
            id="NOTIF-003",
            title="FLEET TELEMETRY SYNCHRONIZED",
            message="48 active telemetry units synchronized via CAN-bus vector 07.",
            severity="INFO",
            is_read=True,
            timestamp=now - timedelta(minutes=30)
        )
    ]
    db.add_all(notifications)
    db.commit()

    # 7. Seed Activity Logs
    activity_logs = [
        models.ActivityLog(
            event_type="INCIDENT_DETECTED",
            message="Priority Alpha Incident INC-8921-TH triggered by Core Sensor T-04 (+8.2°C)",
            vehicle_id="AC-2048",
            incident_id="INC-8921-TH",
            user_name="AeroCold Telematics Watchdog",
            timestamp=now - timedelta(minutes=15)
        ),
        models.ActivityLog(
            event_type="ECU_FAULT_DIAGNOSED",
            message="Fault code E-104: Evaporator Blower Fan RPM drop (320 RPM vs 1450 RPM cmd)",
            vehicle_id="AC-2048",
            incident_id="INC-8921-TH",
            user_name="CAN-bus Gateway",
            timestamp=now - timedelta(minutes=14)
        ),
        models.ActivityLog(
            event_type="AI_PLAN_SYNTHESIZED",
            message="Plan PLAN-7741 synthesized with 96% confidence score for Cold Storage A diversion",
            vehicle_id="AC-2048",
            incident_id="INC-8921-TH",
            user_name="AeroCold Agent",
            timestamp=now - timedelta(minutes=12)
        )
    ]
    db.add_all(activity_logs)
    db.commit()

    # 8. Seed Settings
    settings_records = [
        models.Setting(key="DEMO_MODE", value="true", description="Runs application in simulated demo mode with verified telemetry mocks."),
        models.Setting(key="FDA_21_CFR_PART_11", value="ENABLED", description="Cryptographic dispatch signature and audit logging for regulatory compliance."),
        models.Setting(key="AUTOPILOT_THRESHOLD_MINS", value="45", description="Maximum transit buffer time before requiring automated escalation.")
    ]
    db.add_all(settings_records)
    db.commit()
