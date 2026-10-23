from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Vehicle Schemas
class SensorReadingBase(BaseModel):
    sensor_code: str
    temperature_c: float
    humidity_pct: float
    timestamp: datetime
    is_anomaly: bool = False
    is_simulated: bool = True

class SensorReadingOut(SensorReadingBase):
    id: int
    vehicle_id: str

    model_config = ConfigDict(from_attributes=True)

class VehicleBase(BaseModel):
    id: str
    name: str
    carrier: str
    driver_name: str
    driver_phone: str
    status: str
    latitude: float
    longitude: float
    speed_mph: float
    heading: str
    genset_fuel_pct: float
    cargo_name: str
    cargo_weight_kg: float
    cargo_pallets: int
    cargo_value_usd: float
    target_temp_c: float
    threshold_temp_c: float
    current_temp_c: float

class VehicleOut(VehicleBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Facility Schemas
class RecoveryFacilityBase(BaseModel):
    id: str
    name: str
    short_name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    estimated_travel_minutes: int
    bay_status: str
    prechilled_dock_ready: bool
    temp_range_min_c: float
    temp_range_max_c: float
    capacity_pct: float
    rating: float
    is_recommended: bool
    hourly_rate_usd: float

class RecoveryFacilityOut(RecoveryFacilityBase):
    model_config = ConfigDict(from_attributes=True)

# Recovery Plan Schemas
class RecoveryPlanCreate(BaseModel):
    facility_id: str
    reason: Optional[str] = None

class RecoveryPlanOut(BaseModel):
    id: str
    incident_id: str
    vehicle_id: str
    facility_id: str
    status: str
    confidence_score: float
    estimated_arrival_minutes: int
    projected_salvage_usd: float
    biological_yield_pct: float
    ai_reasoning: Optional[str] = None
    evidence_summary: Optional[str] = None
    assumptions: Optional[str] = None
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    facility: Optional[RecoveryFacilityOut] = None

    model_config = ConfigDict(from_attributes=True)

# Incident Schemas
class IncidentBase(BaseModel):
    id: str
    vehicle_id: str
    title: str
    description: str
    ecu_fault_code: str
    severity: str
    status: str
    excursion_temp_c: float
    drift_rate_c_per_min: float
    breach_time: datetime
    time_to_spoilage_minutes: int
    biological_yield_projected_pct: float

class IncidentOut(IncidentBase):
    vehicle: Optional[VehicleOut] = None
    recovery_plans: List[RecoveryPlanOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IncidentAnalyzeRequest(BaseModel):
    trigger_source: Optional[str] = "dispatcher_manual"
    notes: Optional[str] = None

class IncidentAnalyzeResponse(BaseModel):
    incident_id: str
    risk_level: str
    temperature_breach_c: float
    drift_rate_c_per_min: float
    time_to_quality_loss_minutes: int
    salvage_percentage_projected: float
    ai_analysis_narrative: str
    evidence_checklist: List[str]
    suggested_recovery_facility: str
    confidence_score: float
    recovery_plan: RecoveryPlanOut

# Approval Request & Response
class ApprovePlanRequest(BaseModel):
    authorized_by: Optional[str] = "Sarah Jenkins"
    role: Optional[str] = "Lead Dispatcher"
    notes: Optional[str] = "Authorized emergency diversion via AeroCold Autopilot."

class ApprovePlanResponse(BaseModel):
    success: bool
    message: str
    plan_id: str
    status: str
    authorized_by: str
    timestamp: datetime
    dispatch_edi_code: str
    signature_hash: str
    simulated: bool = True

# Dashboard Overview Schema
class DashboardOverviewOut(BaseModel):
    active_units_total: int
    active_units_synchronized: int
    critical_breaches_count: int
    critical_vehicle_id: str
    critical_temp_c: float
    critical_temp_target_c: float
    active_dispatch_directives_count: int
    cargo_asset_exposure_usd: float
    projected_yield_preservation_pct: float
    system_status: str
    telemetry_sync_seconds: float
    critical_incident: Optional[IncidentOut] = None
    recommended_plan: Optional[RecoveryPlanOut] = None

# Analytics Schema
class AnalyticsOverviewOut(BaseModel):
    cold_chain_uptime_pct: float
    total_prevented_spoilage_usd: float
    average_incident_resolution_minutes: float
    fda_audit_compliance_score_pct: float
    excursion_trends_by_week: List[dict]
    facility_success_metrics: List[dict]

# Notification Schema
class NotificationOut(BaseModel):
    id: str
    title: str
    message: str
    severity: str
    is_read: bool
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Setting Schema
class SettingOut(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
