import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientListResponse

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(
        select(Patient).where(Patient.medical_record_number == data.medical_record_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Medical record number already exists")

    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    hospital_id: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Patient)
    count_query = select(func.count(Patient.id))

    if hospital_id:
        query = query.where(Patient.hospital_id == hospital_id)
        count_query = count_query.where(Patient.hospital_id == hospital_id)

    if search:
        search_filter = (
            Patient.first_name.ilike(f"%{search}%")
            | Patient.last_name.ilike(f"%{search}%")
            | Patient.medical_record_number.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total = (await db.execute(count_query)).scalar()
    offset = (page - 1) * page_size
    result = await db.execute(query.order_by(Patient.created_at.desc()).offset(offset).limit(page_size))

    return PatientListResponse(
        items=result.scalars().all(),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    await db.commit()
    await db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    await db.delete(patient)
    await db.commit()
