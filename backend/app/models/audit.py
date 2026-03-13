import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditRecord(Base):
    __tablename__ = "audit_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("procedures.id"), nullable=False)
    auditor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, in_progress, completed
    selected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Audit findings
    data_accurate: Mapped[bool | None] = mapped_column(Boolean)
    discrepancies_found: Mapped[bool] = mapped_column(Boolean, default=False)
    discrepancy_details: Mapped[str | None] = mapped_column(Text)
    field_corrections: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    notes: Mapped[str | None] = mapped_column(Text)
