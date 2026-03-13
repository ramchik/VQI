from pydantic import BaseModel

from app.models.procedure import ProcedureType


class OutcomeRate(BaseModel):
    label: str
    hospital_rate: float
    national_rate: float
    risk_adjusted_rate: float | None = None


class ProcedureVolume(BaseModel):
    procedure_type: ProcedureType
    count: int


class HospitalSummary(BaseModel):
    hospital_id: str
    total_procedures: int
    total_patients: int
    procedure_volumes: list[ProcedureVolume]
    outcome_rates: list[OutcomeRate]
    audit_completion_rate: float


class SurgeonReportCard(BaseModel):
    surgeon_id: str
    surgeon_name: str
    total_procedures: int
    procedure_volumes: list[ProcedureVolume]
    outcome_rates: list[OutcomeRate]
    risk_adjusted_mortality: float | None = None
    risk_adjusted_morbidity: float | None = None


class DashboardResponse(BaseModel):
    hospital_summary: HospitalSummary
    period_start: str
    period_end: str
