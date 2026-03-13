import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.audit import AuditRecord
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.post("/select-cases", status_code=status.HTTP_201_CREATED)
async def select_audit_cases(
    hospital_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    service = AuditService(db)
    records = await service.select_random_cases(hospital_id)
    return {"selected": len(records), "audit_ids": [str(r.id) for r in records]}


@router.get("/")
async def list_audit_records(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(AuditRecord)
    count_query = select(func.count(AuditRecord.id))

    if status_filter:
        query = query.where(AuditRecord.status == status_filter)
        count_query = count_query.where(AuditRecord.status == status_filter)

    total = (await db.execute(count_query)).scalar()
    offset = (page - 1) * page_size
    result = await db.execute(query.order_by(AuditRecord.selected_at.desc()).offset(offset).limit(page_size))

    records = result.scalars().all()
    return {
        "items": [
            {
                "id": str(r.id),
                "procedure_id": str(r.procedure_id),
                "status": r.status,
                "selected_at": r.selected_at.isoformat() if r.selected_at else None,
                "data_accurate": r.data_accurate,
                "discrepancies_found": r.discrepancies_found,
            }
            for r in records
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.patch("/{audit_id}/complete")
async def complete_audit(
    audit_id: uuid.UUID,
    data_accurate: bool = True,
    discrepancies_found: bool = False,
    discrepancy_details: str | None = None,
    notes: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(AuditRecord).where(AuditRecord.id == audit_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Audit record not found")

    record.status = "completed"
    record.auditor_id = current_user.id
    record.data_accurate = data_accurate
    record.discrepancies_found = discrepancies_found
    record.discrepancy_details = discrepancy_details
    record.notes = notes

    from datetime import datetime, timezone
    record.completed_at = datetime.now(timezone.utc)

    await db.commit()
    return {"status": "completed", "id": str(audit_id)}
