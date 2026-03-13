from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.patient import Patient
from app.models.procedure import Procedure, PostOperativeData, ProcedureType
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse, HospitalSummary, ProcedureVolume, OutcomeRate, SurgeonReportCard,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/hospital/{hospital_id}", response_model=DashboardResponse)
async def get_hospital_dashboard(
    hospital_id: str,
    period_start: date = Query(default=None),
    period_end: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Default to current year
    if not period_start:
        period_start = date(date.today().year, 1, 1)
    if not period_end:
        period_end = date.today()

    # Procedure counts
    proc_query = (
        select(Procedure.procedure_type, func.count(Procedure.id))
        .where(
            Procedure.hospital_id == hospital_id,
            Procedure.procedure_date >= period_start,
            Procedure.procedure_date <= period_end,
        )
        .group_by(Procedure.procedure_type)
    )
    proc_result = await db.execute(proc_query)
    volumes = [ProcedureVolume(procedure_type=row[0], count=row[1]) for row in proc_result.all()]
    total_procedures = sum(v.count for v in volumes)

    # Patient count
    patient_count_result = await db.execute(
        select(func.count(func.distinct(Procedure.patient_id))).where(
            Procedure.hospital_id == hospital_id,
            Procedure.procedure_date >= period_start,
            Procedure.procedure_date <= period_end,
        )
    )
    total_patients = patient_count_result.scalar() or 0

    # Outcome rates from post-operative data
    outcome_query = (
        select(
            func.count(PostOperativeData.id).label("total"),
            func.sum(case((PostOperativeData.mortality == True, 1), else_=0)).label("mortality"),
            func.sum(case((PostOperativeData.stroke == True, 1), else_=0)).label("stroke"),
            func.sum(case((PostOperativeData.mi == True, 1), else_=0)).label("mi"),
            func.sum(case((PostOperativeData.wound_complication == True, 1), else_=0)).label("wound"),
            func.sum(case((PostOperativeData.return_to_or == True, 1), else_=0)).label("reop"),
        )
        .join(Procedure, PostOperativeData.procedure_id == Procedure.id)
        .where(
            Procedure.hospital_id == hospital_id,
            Procedure.procedure_date >= period_start,
            Procedure.procedure_date <= period_end,
        )
    )
    outcome_result = (await db.execute(outcome_query)).first()

    outcome_rates = []
    if outcome_result and outcome_result.total and outcome_result.total > 0:
        total = outcome_result.total
        # National averages (illustrative benchmark values from VQI literature)
        benchmarks = {
            "Mortality": (outcome_result.mortality, 0.018),
            "Stroke": (outcome_result.stroke, 0.015),
            "Myocardial Infarction": (outcome_result.mi, 0.012),
            "Wound Complication": (outcome_result.wound, 0.045),
            "Return to OR": (outcome_result.reop, 0.035),
        }
        for label, (count, national) in benchmarks.items():
            hospital_rate = (count or 0) / total
            outcome_rates.append(OutcomeRate(
                label=label,
                hospital_rate=round(hospital_rate, 4),
                national_rate=national,
            ))

    return DashboardResponse(
        hospital_summary=HospitalSummary(
            hospital_id=hospital_id,
            total_procedures=total_procedures,
            total_patients=total_patients,
            procedure_volumes=volumes,
            outcome_rates=outcome_rates,
            audit_completion_rate=0.0,
        ),
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
    )


@router.get("/surgeon/{surgeon_id}", response_model=SurgeonReportCard)
async def get_surgeon_report_card(
    surgeon_id: str,
    period_start: date = Query(default=None),
    period_end: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not period_start:
        period_start = date(date.today().year, 1, 1)
    if not period_end:
        period_end = date.today()

    # Surgeon info
    surgeon_result = await db.execute(select(User).where(User.id == surgeon_id))
    surgeon = surgeon_result.scalar_one_or_none()
    surgeon_name = surgeon.full_name if surgeon else "Unknown"

    # Volumes
    proc_query = (
        select(Procedure.procedure_type, func.count(Procedure.id))
        .where(
            Procedure.surgeon_id == surgeon_id,
            Procedure.procedure_date >= period_start,
            Procedure.procedure_date <= period_end,
        )
        .group_by(Procedure.procedure_type)
    )
    proc_result = await db.execute(proc_query)
    volumes = [ProcedureVolume(procedure_type=row[0], count=row[1]) for row in proc_result.all()]
    total_procedures = sum(v.count for v in volumes)

    # Outcomes
    outcome_query = (
        select(
            func.count(PostOperativeData.id).label("total"),
            func.sum(case((PostOperativeData.mortality == True, 1), else_=0)).label("mortality"),
            func.sum(case((PostOperativeData.stroke == True, 1), else_=0)).label("stroke"),
            func.sum(case((PostOperativeData.mi == True, 1), else_=0)).label("mi"),
        )
        .join(Procedure, PostOperativeData.procedure_id == Procedure.id)
        .where(
            Procedure.surgeon_id == surgeon_id,
            Procedure.procedure_date >= period_start,
            Procedure.procedure_date <= period_end,
        )
    )
    outcome_result = (await db.execute(outcome_query)).first()

    outcome_rates = []
    if outcome_result and outcome_result.total and outcome_result.total > 0:
        total = outcome_result.total
        for label, count, national in [
            ("Mortality", outcome_result.mortality, 0.018),
            ("Stroke", outcome_result.stroke, 0.015),
            ("MI", outcome_result.mi, 0.012),
        ]:
            outcome_rates.append(OutcomeRate(
                label=label,
                hospital_rate=round((count or 0) / total, 4),
                national_rate=national,
            ))

    return SurgeonReportCard(
        surgeon_id=surgeon_id,
        surgeon_name=surgeon_name,
        total_procedures=total_procedures,
        procedure_volumes=volumes,
        outcome_rates=outcome_rates,
    )
