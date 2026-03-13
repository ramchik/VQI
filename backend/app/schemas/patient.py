import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    medical_record_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    hospital_id: str

    # Risk factors
    smoking_status: str | None = None
    diabetes: bool = False
    diabetes_type: str | None = None
    hypertension: bool = False
    hyperlipidemia: bool = False
    cad: bool = False
    chf: bool = False
    copd: bool = False
    renal_insufficiency: bool = False
    creatinine: float | None = None
    bmi: float | None = None
    height_cm: float | None = None
    weight_kg: float | None = None

    # Medications
    antiplatelet: bool = False
    anticoagulant: bool = False
    statin: bool = False
    beta_blocker: bool = False
    ace_inhibitor: bool = False

    asa_class: int | None = Field(None, ge=1, le=6)


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    smoking_status: str | None = None
    diabetes: bool | None = None
    diabetes_type: str | None = None
    hypertension: bool | None = None
    hyperlipidemia: bool | None = None
    cad: bool | None = None
    chf: bool | None = None
    copd: bool | None = None
    renal_insufficiency: bool | None = None
    creatinine: float | None = None
    bmi: float | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    antiplatelet: bool | None = None
    anticoagulant: bool | None = None
    statin: bool | None = None
    beta_blocker: bool | None = None
    ace_inhibitor: bool | None = None
    asa_class: int | None = Field(None, ge=1, le=6)


class PatientResponse(BaseModel):
    id: uuid.UUID
    medical_record_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    hospital_id: str
    smoking_status: str | None
    diabetes: bool
    hypertension: bool
    hyperlipidemia: bool
    cad: bool
    chf: bool
    copd: bool
    renal_insufficiency: bool
    creatinine: float | None
    bmi: float | None
    asa_class: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    items: list[PatientResponse]
    total: int
    page: int
    page_size: int
