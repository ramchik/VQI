import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Integer, Float, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Risk factors
    smoking_status: Mapped[str | None] = mapped_column(String(50))  # never, former, current
    diabetes: Mapped[bool] = mapped_column(Boolean, default=False)
    diabetes_type: Mapped[str | None] = mapped_column(String(20))  # type1, type2
    hypertension: Mapped[bool] = mapped_column(Boolean, default=False)
    hyperlipidemia: Mapped[bool] = mapped_column(Boolean, default=False)
    cad: Mapped[bool] = mapped_column(Boolean, default=False)  # coronary artery disease
    chf: Mapped[bool] = mapped_column(Boolean, default=False)  # congestive heart failure
    copd: Mapped[bool] = mapped_column(Boolean, default=False)
    renal_insufficiency: Mapped[bool] = mapped_column(Boolean, default=False)
    creatinine: Mapped[float | None] = mapped_column(Float)
    bmi: Mapped[float | None] = mapped_column(Float)
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)

    # Medications
    antiplatelet: Mapped[bool] = mapped_column(Boolean, default=False)
    anticoagulant: Mapped[bool] = mapped_column(Boolean, default=False)
    statin: Mapped[bool] = mapped_column(Boolean, default=False)
    beta_blocker: Mapped[bool] = mapped_column(Boolean, default=False)
    ace_inhibitor: Mapped[bool] = mapped_column(Boolean, default=False)

    # ASA classification (1-6)
    asa_class: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    procedures: Mapped[list["Procedure"]] = relationship(back_populates="patient")
