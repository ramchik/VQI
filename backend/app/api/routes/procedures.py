import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.procedure import (
    Procedure, PreOperativeData, IntraOperativeData, PostOperativeData, FollowUpData, ProcedureType,
)
from app.models.user import User
from app.schemas.procedure import (
    ProcedureCreate, ProcedureResponse, ProcedureDetailResponse, ProcedureListResponse,
    PreOperativeDataCreate, IntraOperativeDataCreate, PostOperativeDataCreate, FollowUpDataCreate,
)

router = APIRouter(prefix="/api/procedures", tags=["procedures"])


def _serialize_stage(obj) -> dict | None:
    if obj is None:
        return None
    data = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
    # Convert UUID and date types for JSON
    for k, v in data.items():
        if isinstance(v, uuid.UUID):
            data[k] = str(v)
        elif hasattr(v, "isoformat"):
            data[k] = v.isoformat()
    return data


@router.post("/", response_model=ProcedureResponse, status_code=status.HTTP_201_CREATED)
async def create_procedure(
    data: ProcedureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    procedure = Procedure(**data.model_dump())
    db.add(procedure)
    await db.commit()
    await db.refresh(procedure)
    return procedure


@router.get("/", response_model=ProcedureListResponse)
async def list_procedures(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    patient_id: uuid.UUID | None = None,
    hospital_id: str | None = None,
    procedure_type: ProcedureType | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Procedure)
    count_query = select(func.count(Procedure.id))

    if patient_id:
        query = query.where(Procedure.patient_id == patient_id)
        count_query = count_query.where(Procedure.patient_id == patient_id)
    if hospital_id:
        query = query.where(Procedure.hospital_id == hospital_id)
        count_query = count_query.where(Procedure.hospital_id == hospital_id)
    if procedure_type:
        query = query.where(Procedure.procedure_type == procedure_type)
        count_query = count_query.where(Procedure.procedure_type == procedure_type)

    total = (await db.execute(count_query)).scalar()
    offset = (page - 1) * page_size
    result = await db.execute(query.order_by(Procedure.procedure_date.desc()).offset(offset).limit(page_size))

    return ProcedureListResponse(items=result.scalars().all(), total=total, page=page, page_size=page_size)


@router.get("/{procedure_id}", response_model=ProcedureDetailResponse)
async def get_procedure(
    procedure_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Procedure)
        .where(Procedure.id == procedure_id)
        .options(
            selectinload(Procedure.pre_operative),
            selectinload(Procedure.intra_operative),
            selectinload(Procedure.post_operative),
            selectinload(Procedure.follow_up),
        )
    )
    procedure = result.scalar_one_or_none()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")

    return ProcedureDetailResponse(
        **ProcedureResponse.model_validate(procedure).model_dump(),
        pre_operative=_serialize_stage(procedure.pre_operative),
        intra_operative=_serialize_stage(procedure.intra_operative),
        post_operative=_serialize_stage(procedure.post_operative),
        follow_up=_serialize_stage(procedure.follow_up),
    )


@router.post("/{procedure_id}/pre-operative", status_code=status.HTTP_201_CREATED)
async def add_pre_operative(
    procedure_id: uuid.UUID,
    data: PreOperativeDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = PreOperativeData(procedure_id=procedure_id, **data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _serialize_stage(record)


@router.post("/{procedure_id}/intra-operative", status_code=status.HTTP_201_CREATED)
async def add_intra_operative(
    procedure_id: uuid.UUID,
    data: IntraOperativeDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = IntraOperativeData(procedure_id=procedure_id, **data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _serialize_stage(record)


@router.post("/{procedure_id}/post-operative", status_code=status.HTTP_201_CREATED)
async def add_post_operative(
    procedure_id: uuid.UUID,
    data: PostOperativeDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = PostOperativeData(procedure_id=procedure_id, **data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _serialize_stage(record)


@router.post("/{procedure_id}/follow-up", status_code=status.HTTP_201_CREATED)
async def add_follow_up(
    procedure_id: uuid.UUID,
    data: FollowUpDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = FollowUpData(procedure_id=procedure_id, **data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _serialize_stage(record)
