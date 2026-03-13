import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.procedure import ProcedureType


class ProcedureCreate(BaseModel):
    patient_id: uuid.UUID
    procedure_type: ProcedureType
    procedure_date: date
    surgeon_id: uuid.UUID | None = None
    hospital_id: str
    urgency: str = "elective"


class PreOperativeDataCreate(BaseModel):
    indication: str | None = None
    symptom_status: str | None = None
    symptom_onset_days: int | None = None
    imaging_type: str | None = None
    stenosis_percent: float | None = Field(None, ge=0, le=100)
    lesion_side: str | None = None
    heart_rate: int | None = Field(None, ge=20, le=300)
    systolic_bp: int | None = Field(None, ge=50, le=300)
    diastolic_bp: int | None = Field(None, ge=20, le=200)
    hemoglobin: float | None = Field(None, ge=1, le=25)
    platelet_count: int | None = Field(None, ge=0, le=1500000)
    inr: float | None = Field(None, ge=0.5, le=20)
    gfr: float | None = Field(None, ge=0, le=200)
    additional_data: dict | None = None


class IntraOperativeDataCreate(BaseModel):
    anesthesia_type: str | None = None
    operative_time_minutes: int | None = Field(None, ge=0, le=2880)
    estimated_blood_loss_ml: int | None = Field(None, ge=0)
    contrast_volume_ml: float | None = Field(None, ge=0)
    fluoroscopy_time_minutes: float | None = Field(None, ge=0)
    device_manufacturer: str | None = None
    device_model: str | None = None
    graft_type: str | None = None
    graft_material: str | None = None
    approach: str | None = None
    access_site: str | None = None
    closure_method: str | None = None
    completion_angiogram: bool = False
    technical_success: bool = True
    intra_op_complication: bool = False
    complication_details: str | None = None
    additional_data: dict | None = None


class PostOperativeDataCreate(BaseModel):
    discharge_date: date | None = None
    los_days: int | None = Field(None, ge=0)
    discharge_disposition: str | None = None
    mortality: bool = False
    stroke: bool = False
    mi: bool = False
    bleeding_requiring_transfusion: bool = False
    wound_complication: bool = False
    respiratory_complication: bool = False
    renal_complication: bool = False
    return_to_or: bool = False
    readmission_30day: bool = False
    leg_saved: bool | None = None
    amputation_level: str | None = None
    additional_data: dict | None = None


class FollowUpDataCreate(BaseModel):
    follow_up_date: date | None = None
    days_since_procedure: int | None = None
    alive: bool = True
    death_date: date | None = None
    cause_of_death: str | None = None
    graft_patent: bool | None = None
    restenosis: bool = False
    restenosis_percent: float | None = Field(None, ge=0, le=100)
    reintervention: bool = False
    reintervention_type: str | None = None
    ambulatory_status: str | None = None
    living_status: str | None = None
    late_stroke: bool = False
    late_mi: bool = False
    amputation: bool = False
    additional_data: dict | None = None


class ProcedureResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    procedure_type: ProcedureType
    procedure_date: date
    surgeon_id: uuid.UUID | None
    hospital_id: str
    status: str
    urgency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProcedureDetailResponse(ProcedureResponse):
    pre_operative: dict | None = None
    intra_operative: dict | None = None
    post_operative: dict | None = None
    follow_up: dict | None = None


class ProcedureListResponse(BaseModel):
    items: list[ProcedureResponse]
    total: int
    page: int
    page_size: int
