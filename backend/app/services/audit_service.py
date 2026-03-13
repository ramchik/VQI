import random

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.audit import AuditRecord
from app.models.procedure import Procedure


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def select_random_cases(self, hospital_id: str) -> list[AuditRecord]:
        """Select 10% of completed procedures for audit (not already audited)."""
        # Get completed procedures not yet selected for audit
        already_audited = select(AuditRecord.procedure_id)
        result = await self.db.execute(
            select(Procedure.id).where(
                Procedure.hospital_id == hospital_id,
                Procedure.status == "completed",
                Procedure.id.notin_(already_audited),
            )
        )
        procedure_ids = [row[0] for row in result.all()]

        # Randomly select the configured percentage
        sample_size = max(1, int(len(procedure_ids) * settings.AUDIT_SAMPLE_RATE))
        selected_ids = random.sample(procedure_ids, min(sample_size, len(procedure_ids)))

        records = []
        for pid in selected_ids:
            record = AuditRecord(procedure_id=pid)
            self.db.add(record)
            records.append(record)

        await self.db.commit()
        for r in records:
            await self.db.refresh(r)

        return records
