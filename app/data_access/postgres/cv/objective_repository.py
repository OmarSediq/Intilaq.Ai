from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_models import Objective

class CVObjectiveRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_objective(self, header_id: int, description: str = "") -> Objective:
        obj = Objective(header_id=header_id, description=description)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, objective_id: int) -> Objective | None:
        return await self.db.get(Objective, objective_id)

    async def update_description(self, objective: Objective, description: str) -> Objective:
        objective.description = description
        await self.db.commit()
        await self.db.refresh(objective)
        return objective
