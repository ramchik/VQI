import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    String, Date, DateTime, Integer, Float, Boolean, Text, Enum, ForeignKey, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProcedureType(str, enum.Enum):
    CAROTID_ENDARTERECTOMY = "carotid_endarterectomy"
    CAROTID_STENT = "carotid_stent"
    OPEN_AAA = "open_aaa"  # Open abdominal aortic aneurysm
    EVAR = "evar"  # Endovascular aneurysm repair
    SUPRAINGUINAL_BYPASS = "suprainguinal_bypass"
    INFRAINGUINAL_BYPASS = "infrainguinal_bypass"
    PVI = "pvi"  # Peripheral vascular intervention
    VARICOSE_VEIN = "varicose_vein"
    HEMODIALYSIS_ACCESS = "hemodialysis_access"
    THORACIC_ENDOVASCULAR = "thoracic_endovascular"
    IVC_FILTER = "ivc_filter"
    UPPER_EXTREMITY_BYPASS = "upper_extremity_bypass"
    VISCERAL_AORTIC_INTERVENTION = "visceral_aortic_intervention"
    AMPUTATION = "amputation"


class Procedure(Base):
    __tablename__ = "procedures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    procedure_type: Mapped[ProcedureType] = mapped_column(Enum(ProcedureType), nullable=False, index=True)
    procedure_date: Mapped[date] = mapped_column(Date, nullable=False)
    surgeon_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    hospital_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="in_progress")  # in_progress, completed, audited
    urgency: Mapped[str] = mapped_column(String(50), default="elective")  # elective, urgent, emergent

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="procedures")
    pre_operative: Mapped["PreOperativeData | None"] = relationship(back_populates="procedure", uselist=False)
    intra_operative: Mapped["IntraOperativeData | None"] = relationship(back_populates="procedure", uselist=False)
    post_operative: Mapped["PostOperativeData | None"] = relationship(back_populates="procedure", uselist=False)
    follow_up: Mapped["FollowUpData | None"] = relationship(back_populates="procedure", uselist=False)


class PreOperativeData(Base):
    __tablename__ = "pre_operative_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("procedures.id"), unique=True)

    # Indications
    indication: Mapped[str | None] = mapped_column(String(200))
    symptom_status: Mapped[str | None] = mapped_column(String(100))  # asymptomatic, symptomatic
    symptom_onset_days: Mapped[int | None] = mapped_column(Integer)

    # Pre-op imaging
    imaging_type: Mapped[str | None] = mapped_column(String(100))  # duplex, cta, mra, angiogram
    stenosis_percent: Mapped[float | None] = mapped_column(Float)
    lesion_side: Mapped[str | None] = mapped_column(String(20))  # left, right, bilateral

    # Vitals
    heart_rate: Mapped[int | None] = mapped_column(Integer)
    systolic_bp: Mapped[int | None] = mapped_column(Integer)
    diastolic_bp: Mapped[int | None] = mapped_column(Integer)

    # Labs
    hemoglobin: Mapped[float | None] = mapped_column(Float)
    platelet_count: Mapped[int | None] = mapped_column(Integer)
    inr: Mapped[float | None] = mapped_column(Float)
    gfr: Mapped[float | None] = mapped_column(Float)

    # Procedure-specific fields stored as JSON for flexibility
    additional_data: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    procedure: Mapped["Procedure"] = relationship(back_populates="pre_operative")


class IntraOperativeData(Base):
    __tablename__ = "intra_operative_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("procedures.id"), unique=True)

    # General surgical details
    anesthesia_type: Mapped[str | None] = mapped_column(String(50))  # general, regional, local, sedation
    operative_time_minutes: Mapped[int | None] = mapped_column(Integer)
    estimated_blood_loss_ml: Mapped[int | None] = mapped_column(Integer)
    contrast_volume_ml: Mapped[float | None] = mapped_column(Float)
    fluoroscopy_time_minutes: Mapped[float | None] = mapped_column(Float)

    # Device / graft
    device_manufacturer: Mapped[str | None] = mapped_column(String(200))
    device_model: Mapped[str | None] = mapped_column(String(200))
    graft_type: Mapped[str | None] = mapped_column(String(100))  # autologous_vein, prosthetic, hybrid
    graft_material: Mapped[str | None] = mapped_column(String(100))

    # Technique
    approach: Mapped[str | None] = mapped_column(String(100))  # open, endovascular, hybrid
    access_site: Mapped[str | None] = mapped_column(String(100))
    closure_method: Mapped[str | None] = mapped_column(String(100))

    # Completion
    completion_angiogram: Mapped[bool] = mapped_column(Boolean, default=False)
    technical_success: Mapped[bool] = mapped_column(Boolean, default=True)

    # Intra-op complications
    intra_op_complication: Mapped[bool] = mapped_column(Boolean, default=False)
    complication_details: Mapped[str | None] = mapped_column(Text)

    additional_data: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    procedure: Mapped["Procedure"] = relationship(back_populates="intra_operative")


class PostOperativeData(Base):
    __tablename__ = "post_operative_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("procedures.id"), unique=True)

    # Discharge info
    discharge_date: Mapped[date | None] = mapped_column(Date)
    los_days: Mapped[int | None] = mapped_column(Integer)  # length of stay
    discharge_disposition: Mapped[str | None] = mapped_column(String(100))  # home, rehab, snf, death

    # Outcomes before discharge
    mortality: Mapped[bool] = mapped_column(Boolean, default=False)
    stroke: Mapped[bool] = mapped_column(Boolean, default=False)
    mi: Mapped[bool] = mapped_column(Boolean, default=False)  # myocardial infarction
    bleeding_requiring_transfusion: Mapped[bool] = mapped_column(Boolean, default=False)
    wound_complication: Mapped[bool] = mapped_column(Boolean, default=False)
    respiratory_complication: Mapped[bool] = mapped_column(Boolean, default=False)
    renal_complication: Mapped[bool] = mapped_column(Boolean, default=False)
    return_to_or: Mapped[bool] = mapped_column(Boolean, default=False)
    readmission_30day: Mapped[bool] = mapped_column(Boolean, default=False)

    # Leg-specific (for lower extremity procedures)
    leg_saved: Mapped[bool | None] = mapped_column(Boolean)
    amputation_level: Mapped[str | None] = mapped_column(String(100))

    additional_data: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    procedure: Mapped["Procedure"] = relationship(back_populates="post_operative")


class FollowUpData(Base):
    __tablename__ = "follow_up_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("procedures.id"), unique=True)

    follow_up_date: Mapped[date | None] = mapped_column(Date)
    days_since_procedure: Mapped[int | None] = mapped_column(Integer)

    # Status
    alive: Mapped[bool] = mapped_column(Boolean, default=True)
    death_date: Mapped[date | None] = mapped_column(Date)
    cause_of_death: Mapped[str | None] = mapped_column(String(200))

    # Graft / intervention patency
    graft_patent: Mapped[bool | None] = mapped_column(Boolean)
    restenosis: Mapped[bool] = mapped_column(Boolean, default=False)
    restenosis_percent: Mapped[float | None] = mapped_column(Float)
    reintervention: Mapped[bool] = mapped_column(Boolean, default=False)
    reintervention_type: Mapped[str | None] = mapped_column(String(200))

    # Functional outcomes
    ambulatory_status: Mapped[str | None] = mapped_column(String(100))
    living_status: Mapped[str | None] = mapped_column(String(100))  # independent, assisted, nursing_home

    # Late complications
    late_stroke: Mapped[bool] = mapped_column(Boolean, default=False)
    late_mi: Mapped[bool] = mapped_column(Boolean, default=False)
    amputation: Mapped[bool] = mapped_column(Boolean, default=False)

    additional_data: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    procedure: Mapped["Procedure"] = relationship(back_populates="follow_up")
