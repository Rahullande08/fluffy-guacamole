from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, index=True) # e.g. "AC-2048"
    name = Column(String, nullable=False)
    carrier = Column(String, default="SwiftCold Carrier LLC")
    driver_name = Column(String, default="M. Hansen")
    driver_phone = Column(String, default="+1 (555) 234-8921")
    status = Column(String, default="NOMINAL") # "ALERT", "NOMINAL", "TRANSIT", "DIVERTED"
    latitude = Column(Float, default=37.4219)
    longitude = Column(Float, default=-122.0840)
    speed_mph = Column(Float, default=58.0)
    heading = Column(String, default="NW 312°")
    genset_fuel_pct = Column(Float, default=82.0)
    cargo_name = Column(String, default="Organic Strawberries (Driscoll's)")
    cargo_weight_kg = Column(Float, default=4800.0)
    cargo_pallets = Column(Integer, default=18)
    cargo_value_usd = Column(Float, default=142000.0)
    target_temp_c = Column(Float, default=2.0)
    threshold_temp_c = Column(Float, default=4.0)
    current_temp_c = Column(Float, default=8.2)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    readings = relationship("SensorReading", back_populates="vehicle", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="vehicle", cascade="all, delete-orphan")

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), index=True, nullable=False)
    sensor_code = Column(String, default="T-04") # T-04, T-01_AIR_RETURN, T-02_AMBIENT
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, default=88.0)
    timestamp = Column(DateTime, default=utcnow, index=True)
    is_anomaly = Column(Boolean, default=False)
    is_simulated = Column(Boolean, default=True)

    vehicle = relationship("Vehicle", back_populates="readings")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True) # e.g. "INC-8921-TH"
    vehicle_id = Column(String, ForeignKey("vehicles.id"), index=True, nullable=False)
    title = Column(String, default="Refrigeration Anomaly Detected")
    description = Column(Text, default="Evaporator Blower Fan RPM Drop (320 RPM vs 1450 RPM cmd). Dual compressor duty cycle compromised.")
    ecu_fault_code = Column(String, default="E-104")
    severity = Column(String, default="CRITICAL") # CRITICAL, WARNING, RESOLVED
    status = Column(String, default="ACTIVE") # ACTIVE, MITIGATING, RESOLVED
    excursion_temp_c = Column(Float, default=8.2)
    drift_rate_c_per_min = Column(Float, default=0.22)
    breach_time = Column(DateTime, default=utcnow)
    time_to_spoilage_minutes = Column(Integer, default=102) # 1h 42m
    biological_yield_projected_pct = Column(Float, default=99.4)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    vehicle = relationship("Vehicle", back_populates="incidents")
    recovery_plans = relationship("RecoveryPlan", back_populates="incident", cascade="all, delete-orphan")

class RecoveryFacility(Base):
    __tablename__ = "recovery_facilities"

    id = Column(String, primary_key=True, index=True) # FAC-001, FAC-002, FAC-003
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    distance_km = Column(Float, default=4.2)
    estimated_travel_minutes = Column(Integer, default=38)
    bay_status = Column(String, default="Bay 4 Intake Clear")
    prechilled_dock_ready = Column(Boolean, default=True)
    temp_range_min_c = Column(Float, default=-25.0)
    temp_range_max_c = Column(Float, default=4.0)
    capacity_pct = Column(Float, default=64.0)
    rating = Column(Float, default=4.9)
    is_recommended = Column(Boolean, default=False)
    hourly_rate_usd = Column(Float, default=185.0)
    created_at = Column(DateTime, default=utcnow)

    plans = relationship("RecoveryPlan", back_populates="facility")

class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"

    id = Column(String, primary_key=True, index=True) # e.g. "PLAN-7741"
    incident_id = Column(String, ForeignKey("incidents.id"), index=True, nullable=False)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), index=True, nullable=False)
    facility_id = Column(String, ForeignKey("recovery_facilities.id"), index=True, nullable=False)
    status = Column(String, default="RECOMMENDED") # RECOMMENDED, APPROVED, DISPATCHED, REJECTED
    confidence_score = Column(Float, default=0.96)
    estimated_arrival_minutes = Column(Integer, default=38)
    projected_salvage_usd = Column(Float, default=141148.0)
    biological_yield_pct = Column(Float, default=99.4)
    ai_reasoning = Column(Text, nullable=True)
    evidence_summary = Column(Text, nullable=True)
    assumptions = Column(Text, nullable=True)
    created_by = Column(String, default="AeroCold Autonomous Intelligence Agent")
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    incident = relationship("Incident", back_populates="recovery_plans")
    facility = relationship("RecoveryFacility", back_populates="plans")
    approvals = relationship("Approval", back_populates="plan", cascade="all, delete-orphan")

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("recovery_plans.id"), index=True, nullable=False)
    authorized_by = Column(String, default="Sarah Jenkins")
    role = Column(String, default="Lead Dispatcher")
    demo_mode = Column(Boolean, default=True)
    signature_hash = Column(String, nullable=True)
    dispatch_transmitted = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=utcnow)

    plan = relationship("RecoveryPlan", back_populates="approvals")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_type = Column(String, nullable=False) # e.g. INCIDENT_DETECTED, DIVERSION_APPROVED, SIMULATION_SPIKE
    message = Column(Text, nullable=False)
    vehicle_id = Column(String, nullable=True)
    incident_id = Column(String, nullable=True)
    user_name = Column(String, default="System / Dispatcher")
    payload_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, default="CRITICAL") # CRITICAL, WARNING, INFO
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=utcnow)

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
